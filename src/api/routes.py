from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from src.api.schemas import (
    ChatResponse,
    GuardrailError,
    HealthResponse,
    PredictResponse,
    TicketRequest,
)
from src.logutil import log_request
from src.ml.predict import TicketClassifier
from src.rag.guardrails import inspect
from src.rag.pipeline import RagIndex, answer_from_context, build_llm_client
from src.rag.privacy import redact_pii

router = APIRouter()
TECHNICAL = "technical"


def _classifier(request: Request) -> TicketClassifier | None:
    return getattr(request.app.state, "classifier", None)


def _rag(request: Request) -> RagIndex | None:
    return getattr(request.app.state, "rag_index", None)


@router.get("/health", response_model=HealthResponse)
def health(request: Request) -> HealthResponse:
    model_loaded = _classifier(request) is not None
    rag_ready = _rag(request) is not None
    status = "ok" if model_loaded else "degraded"
    return HealthResponse(status=status, model_loaded=model_loaded, rag_ready=rag_ready)


@router.post("/predict", response_model=PredictResponse)
def predict(payload: TicketRequest, request: Request) -> PredictResponse:
    classifier = _classifier(request)
    if classifier is None:
        raise HTTPException(status_code=503, detail="Modelo de triagem não carregado")
    category, confidence = classifier.predict(payload.text)
    log_request(
        endpoint="predict",
        category=category,
        blocked=False,
        reason=None,
        text_length=len(payload.text),
    )
    return PredictResponse(category=category, confidence=confidence, model=classifier.model_id)


@router.post("/chat", response_model=ChatResponse)
def chat(payload: TicketRequest, request: Request) -> ChatResponse:
    decision = inspect(payload.text)
    if decision.blocked:
        log_request(
            endpoint="chat",
            category=None,
            blocked=True,
            reason=decision.reason,
            text_length=len(payload.text),
        )
        raise HTTPException(
            status_code=400,
            detail=GuardrailError(
                reason=decision.reason or "blocked",
                detail="Prompt bloqueado pelos Guardrails",
            ).model_dump(),
        )

    classifier = _classifier(request)
    if classifier is None:
        raise HTTPException(status_code=503, detail="Modelo de triagem não carregado")
    category, confidence = classifier.predict(payload.text)
    if category != TECHNICAL:
        log_request(
            endpoint="chat",
            category=category,
            blocked=False,
            reason="not_technical",
            text_length=len(payload.text),
        )
        return ChatResponse(
            category=category,
            confidence=confidence,
            rag_applied=False,
            answer="O Copilot RAG aplica-se apenas a chamados técnicos. Encaminhe este chamado para a fila correspondente.",
        )

    redacted = redact_pii(payload.text)
    llm = getattr(request.app.state, "llm", None) or build_llm_client()
    if llm is None:
        raise HTTPException(status_code=503, detail="Chave do LLM não configurada")

    index = _rag(request)
    chunks = index.retrieve(redacted) if index is not None else []
    answer = answer_from_context(redacted, chunks, llm)
    log_request(
        endpoint="chat",
        category=category,
        blocked=False,
        reason=None,
        text_length=len(payload.text),
    )
    return ChatResponse(
        category=category,
        confidence=confidence,
        rag_applied=True,
        answer=answer,
    )
