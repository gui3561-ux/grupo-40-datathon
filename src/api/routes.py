from __future__ import annotations

import time

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
from src.rag.pipeline import RagIndex, answer_from_context
from src.rag.privacy import redact_pii

router = APIRouter()
TECHNICAL = "technical"


def _classifier(request: Request) -> TicketClassifier | None:
    return getattr(request.app.state, "classifier", None)


def _rag(request: Request) -> RagIndex | None:
    return getattr(request.app.state, "rag_index", None)


def _log(
    *,
    endpoint: str,
    category: str | None,
    blocked: bool,
    reason: str | None,
    text_length: int,
    started: float,
) -> None:
    log_request(
        endpoint=endpoint,
        category=category,
        blocked=blocked,
        reason=reason,
        text_length=text_length,
        latency_ms=(time.perf_counter() - started) * 1000,
    )


@router.get("/health", response_model=HealthResponse)
def health(request: Request) -> HealthResponse:
    model_loaded = _classifier(request) is not None
    rag_ready = _rag(request) is not None
    settings = request.app.state.settings
    llm_configured = bool(settings.llm_api_key)
    status = "ok" if model_loaded else "degraded"
    return HealthResponse(
        status=status,
        model_loaded=model_loaded,
        rag_ready=rag_ready,
        llm_configured=llm_configured,
    )


@router.post("/predict", response_model=PredictResponse)
def predict(payload: TicketRequest, request: Request) -> PredictResponse:
    started = time.perf_counter()
    classifier = _classifier(request)
    if classifier is None:
        _log(
            endpoint="predict",
            category=None,
            blocked=False,
            reason="model_missing",
            text_length=len(payload.text),
            started=started,
        )
        raise HTTPException(status_code=503, detail="Modelo de triagem não carregado")
    category, confidence = classifier.predict(payload.text)
    _log(
        endpoint="predict",
        category=category,
        blocked=False,
        reason=None,
        text_length=len(payload.text),
        started=started,
    )
    return PredictResponse(category=category, confidence=confidence, model=classifier.model_id)


@router.post("/chat", response_model=ChatResponse)
def chat(payload: TicketRequest, request: Request) -> ChatResponse:
    started = time.perf_counter()
    decision = inspect(payload.text)
    if decision.blocked:
        _log(
            endpoint="chat",
            category=None,
            blocked=True,
            reason=decision.reason,
            text_length=len(payload.text),
            started=started,
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
        _log(
            endpoint="chat",
            category=None,
            blocked=False,
            reason="model_missing",
            text_length=len(payload.text),
            started=started,
        )
        raise HTTPException(status_code=503, detail="Modelo de triagem não carregado")
    category, confidence = classifier.predict(payload.text)
    if category != TECHNICAL:
        _log(
            endpoint="chat",
            category=category,
            blocked=False,
            reason="not_technical",
            text_length=len(payload.text),
            started=started,
        )
        return ChatResponse(
            category=category,
            confidence=confidence,
            rag_applied=False,
            answer="O Copilot RAG aplica-se apenas a chamados técnicos. Encaminhe este chamado para a fila correspondente.",
        )

    llm = getattr(request.app.state, "llm", None)
    if llm is None:
        _log(
            endpoint="chat",
            category=category,
            blocked=False,
            reason="llm_key_missing",
            text_length=len(payload.text),
            started=started,
        )
        raise HTTPException(status_code=503, detail="Chave do LLM não configurada")

    index = _rag(request)
    if index is None:
        _log(
            endpoint="chat",
            category=category,
            blocked=False,
            reason="rag_index_missing",
            text_length=len(payload.text),
            started=started,
        )
        raise HTTPException(status_code=503, detail="Índice do manual não carregado")

    redacted = redact_pii(payload.text)
    chunks = index.retrieve(redacted)
    answer = answer_from_context(redacted, chunks, llm)
    _log(
        endpoint="chat",
        category=category,
        blocked=False,
        reason=None,
        text_length=len(payload.text),
        started=started,
    )
    return ChatResponse(
        category=category,
        confidence=confidence,
        rag_applied=True,
        answer=answer,
    )
