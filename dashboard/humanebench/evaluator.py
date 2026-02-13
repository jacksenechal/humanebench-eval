import json
import logging
import os
import queue
import re
import threading
import uuid
from typing import Optional

import litellm

from humanebench import db
from humanebench.models import (
    EvaluationResult,
    Principle,
    PrincipleScore,
)
from humanebench.rubric import format_rubric_prompt

logger = logging.getLogger(__name__)

EVAL_MODEL = os.environ.get(
    "HUMANEBENCH_EVAL_MODEL", "openrouter/google/gemini-2.0-flash-001"
)

_eval_queue: queue.Queue = queue.Queue()
_worker_started = False
_worker_lock = threading.Lock()

NEUTRAL_FALLBACK = EvaluationResult(
    principles=[
        PrincipleScore(name=p, score=0.5, confidence=0.0) for p in Principle
    ],
    globalViolations=[],
    confidence=0.0,
)


def _strip_fences(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _parse_eval_json(raw: str) -> EvaluationResult:
    cleaned = _strip_fences(raw)
    data = json.loads(cleaned)
    return EvaluationResult(
        principles=[PrincipleScore(**p) for p in data["principles"]],
        globalViolations=data.get("globalViolations", []),
        confidence=data.get("confidence", 0.8),
    )


def evaluate(
    user_prompt: str,
    ai_response: str,
    history: Optional[list] = None,
) -> EvaluationResult:
    system_prompt = format_rubric_prompt(user_prompt, ai_response, history)

    for attempt in range(2):
        try:
            resp = litellm.completion(
                model=EVAL_MODEL,
                messages=[{"role": "user", "content": system_prompt}],
                temperature=0,
                response_format={"type": "json_object"},
            )
            raw = resp.choices[0].message.content
            return _parse_eval_json(raw)
        except json.JSONDecodeError as e:
            if attempt == 0:
                logger.warning("JSON parse error on attempt 1, retrying: %s", e)
                continue
            logger.error("JSON parse failed after retry: %s", e)
        except Exception as e:
            logger.error("Evaluator LLM call failed: %s", e)
            break

    return NEUTRAL_FALLBACK


def _worker_loop() -> None:
    while True:
        item = _eval_queue.get()
        try:
            conversation_id = item["conversation_id"]
            user_prompt = item["user_prompt"]
            ai_response = item["ai_response"]
            history = item.get("history")
            model = item.get("model")

            result = evaluate(user_prompt, ai_response, history)

            overall_score = (
                sum(p.score for p in result.principles) / len(result.principles)
                if result.principles
                else 0.0
            )

            for principle_score in result.principles:
                eval_id = str(uuid.uuid4())
                db.insert_evaluation(
                    id=eval_id,
                    conversation_id=conversation_id,
                    principle=principle_score.name.value,
                    score=principle_score.score,
                    rationale=principle_score.rationale,
                    confidence=principle_score.confidence,
                )

            run_id = str(uuid.uuid4())
            db.insert_evaluation_run(
                id=run_id,
                conversation_id=conversation_id,
                overall_score=overall_score,
                global_violations=result.globalViolations,
                confidence=result.confidence,
                evaluator_model=EVAL_MODEL,
            )

            logger.info(
                "Evaluated conversation %s: overall=%.2f", conversation_id, overall_score
            )
        except Exception as e:
            logger.error("Worker failed for %s: %s", item.get("conversation_id"), e)
        finally:
            _eval_queue.task_done()


def _ensure_worker() -> None:
    global _worker_started
    with _worker_lock:
        if not _worker_started:
            t = threading.Thread(target=_worker_loop, daemon=True)
            t.start()
            _worker_started = True


def queue_evaluation(
    conversation_id: str,
    user_prompt: str,
    ai_response: str,
    history: Optional[list] = None,
    model: Optional[str] = None,
) -> None:
    _ensure_worker()
    _eval_queue.put(
        {
            "conversation_id": conversation_id,
            "user_prompt": user_prompt,
            "ai_response": ai_response,
            "history": history,
            "model": model,
        }
    )
