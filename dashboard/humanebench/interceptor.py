import logging
import uuid
from typing import Any

from litellm.integrations.custom_logger import CustomLogger

from humanebench import db
from humanebench.evaluator import queue_evaluation

logger = logging.getLogger(__name__)


class HumaneBenchCallback(CustomLogger):
    """LiteLLM CustomLogger that captures every user_prompt + ai_response pair
    and queues it for HumaneBench evaluation.

    Usage:
        import litellm
        from humanebench import HumaneBenchCallback
        litellm.callbacks = [HumaneBenchCallback()]
    """

    def log_success_event(self, kwargs: dict, response_obj: Any, start_time: Any, end_time: Any) -> None:
        try:
            messages = kwargs.get("messages", [])
            user_prompt = ""
            for m in reversed(messages):
                if m.get("role") == "user":
                    content = m.get("content", "")
                    if isinstance(content, str):
                        user_prompt = content
                    elif isinstance(content, list):
                        # Handle multimodal messages
                        for part in content:
                            if isinstance(part, dict) and part.get("type") == "text":
                                user_prompt = part.get("text", "")
                                break
                    break

            ai_response = ""
            if response_obj and hasattr(response_obj, "choices") and response_obj.choices:
                ai_response = response_obj.choices[0].message.content or ""

            if not user_prompt or not ai_response:
                return

            model = kwargs.get("model")
            conversation_id = str(uuid.uuid4())

            history = []
            for m in messages[:-1]:
                role = m.get("role", "")
                if role in ("user", "assistant"):
                    content = m.get("content", "")
                    if isinstance(content, str):
                        history.append({"role": role, "content": content})

            db.insert_conversation(
                id=conversation_id,
                user_prompt=user_prompt,
                ai_response=ai_response,
                model=model,
                history=history if history else None,
            )

            queue_evaluation(
                conversation_id=conversation_id,
                user_prompt=user_prompt,
                ai_response=ai_response,
                history=history if history else None,
                model=model,
            )

            logger.debug("HumaneBench queued conversation %s", conversation_id)

        except Exception as e:
            logger.error("HumaneBenchCallback error: %s", e)
