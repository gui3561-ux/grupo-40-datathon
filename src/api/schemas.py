from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator

TEXT_MAX = 1000


class TicketRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    text: str = Field(..., min_length=1, max_length=TEXT_MAX)

    @field_validator("text")
    @classmethod
    def reject_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("O texto do chamado não pode ser vazio.")
        return value


class PredictResponse(BaseModel):
    category: str
    confidence: float
    model: str


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    rag_ready: bool
    llm_configured: bool


class ChatResponse(BaseModel):
    category: str
    confidence: float
    rag_applied: bool
    blocked: bool = False
    reason: str | None = None
    answer: str


class GuardrailError(BaseModel):
    blocked: bool = True
    reason: str
    detail: str
