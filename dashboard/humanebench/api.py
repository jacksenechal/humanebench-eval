import os
import uuid
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from humanebench import db
from humanebench.evaluator import queue_evaluation
from humanebench.models import ConversationRequest

app = FastAPI(title="HumaneBench Eval API", version="0.1.0")

_CORS_ORIGINS = os.environ.get(
    "HUMANEBENCH_CORS_ORIGINS", "http://localhost:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_DASHBOARD_PATH = Path(__file__).parent.parent / "dashboard" / "index.html"


@app.on_event("startup")
def startup() -> None:
    db.init_db()


@app.get("/")
def dashboard() -> FileResponse:
    if not _DASHBOARD_PATH.exists():
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return FileResponse(_DASHBOARD_PATH, media_type="text/html")


@app.post("/evaluate", status_code=202)
def evaluate_endpoint(req: ConversationRequest) -> JSONResponse:
    conversation_id = req.conversation_id or str(uuid.uuid4())

    history_dicts = (
        [h.model_dump() for h in req.history] if req.history else None
    )

    db.insert_conversation(
        id=conversation_id,
        user_prompt=req.user_prompt,
        ai_response=req.ai_response,
        model=req.model,
        history=history_dicts,
        metadata=req.metadata,
    )

    queue_evaluation(
        conversation_id=conversation_id,
        user_prompt=req.user_prompt,
        ai_response=req.ai_response,
        history=history_dicts,
        model=req.model,
    )

    return JSONResponse(
        status_code=202,
        content={"status": "accepted", "conversation_id": conversation_id},
    )


@app.get("/results/{conversation_id}")
def get_results(conversation_id: str) -> dict:
    conv = db.get_conversation(conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    evaluations = db.get_evaluations_for_conversation(conversation_id)
    run = db.get_evaluation_run(conversation_id)

    return {
        "conversation_id": conversation_id,
        "conversation": conv,
        "evaluations": evaluations,
        "run": run,
    }


@app.get("/api/overview")
def api_overview(time_range: str = Query("all")) -> dict:
    return db.get_overview_stats(time_range)


@app.get("/api/incidents")
def api_incidents(
    limit: int = Query(50, ge=1, le=500),
    principle: Optional[str] = Query(None),
) -> list:
    return db.get_incidents(limit=limit, principle=principle)


@app.get("/api/conversations")
def api_conversations(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> list:
    return db.get_conversations_with_scores(limit=limit, offset=offset)


@app.get("/api/conversations/{conversation_id}")
def api_conversation_detail(conversation_id: str) -> dict:
    conv = db.get_conversation(conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    evaluations = db.get_evaluations_for_conversation(conversation_id)
    run = db.get_evaluation_run(conversation_id)

    return {
        "conversation": conv,
        "evaluations": evaluations,
        "run": run,
    }


def main() -> None:
    import uvicorn

    uvicorn.run("humanebench.api:app", host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    main()
