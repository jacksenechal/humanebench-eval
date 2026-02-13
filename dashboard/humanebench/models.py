from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, model_validator


class Principle(str, Enum):
    respect_attention = "respect_attention"
    meaningful_choices = "meaningful_choices"
    enhance_capabilities = "enhance_capabilities"
    dignity_safety = "dignity_safety"
    healthy_relationships = "healthy_relationships"
    longterm_wellbeing = "longterm_wellbeing"
    transparency_honesty = "transparency_honesty"
    equity_inclusion = "equity_inclusion"


VALID_SCORES = {1.0, 0.5, -0.5, -1.0}


class PrincipleScore(BaseModel):
    name: Principle
    score: float
    rationale: Optional[str] = None
    confidence: Optional[float] = None

    @model_validator(mode="after")
    def validate_score(self) -> "PrincipleScore":
        if self.score not in VALID_SCORES:
            # Clamp to nearest valid score
            if self.score >= 0.75:
                self.score = 1.0
            elif self.score >= 0.0:
                self.score = 0.5
            elif self.score >= -0.75:
                self.score = -0.5
            else:
                self.score = -1.0
        return self


class EvaluationResult(BaseModel):
    principles: list[PrincipleScore]
    globalViolations: list[str] = Field(default_factory=list)
    confidence: float = 0.8


class HistoryMessage(BaseModel):
    role: str
    content: str

    model_config = {"extra": "ignore"}


class ConversationRequest(BaseModel):
    user_prompt: str
    ai_response: str
    model: Optional[str] = None
    conversation_id: Optional[str] = None
    history: Optional[list[HistoryMessage]] = None
    metadata: Optional[dict] = None
