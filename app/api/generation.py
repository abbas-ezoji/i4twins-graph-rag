from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.graph.workflow import build_graph


router = APIRouter(
    prefix="/generation",
    tags=["generation"],
)


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class GenerationRequest(BaseModel):
    message: str = Field(..., min_length=1)
    session_id: str | None = None


class GenerationResponse(BaseModel):
    session_id: str | None = None
    message: str
    answer: str
    language: str | None = None
    intent: str | None = None
    answer_status: str | None = None
    evidence: list[dict[str, Any]] = Field(default_factory=list)
    steps: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Graph
# ---------------------------------------------------------------------------

_graph = build_graph()


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("", response_model=GenerationResponse)
def generate(request: GenerationRequest) -> GenerationResponse:
    """
    Execute the Evidence Graph pipeline for a user message.
    """

    message = request.message.strip()

    if not message:
        raise HTTPException(
            status_code=400,
            detail="Message must not be empty.",
        )

    initial_state = {
        "session_id": request.session_id,
        "message": message,
        "steps": [],
        "metadata": {},
    }

    try:
        result = _graph.invoke(initial_state)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Generation pipeline failed: {exc}",
        ) from exc

    return GenerationResponse(
        session_id=result.get("session_id"),
        message=message,
        answer=result.get("answer", ""),
        language=result.get("language"),
        intent=result.get("intent"),
        answer_status=result.get("answer_status"),
        evidence=result.get("evidence", []),
        steps=result.get("steps", []),
        metadata=result.get("metadata", {}),
    )


@router.get("/health")
def generation_health() -> dict[str, str]:
    """
    Health check for the generation pipeline.
    """

    return {
        "status": "ok",
        "service": "generation",
    }