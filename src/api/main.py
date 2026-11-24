from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.routes import router
from src.config import get_settings
from src.logutil import configure_logging, logger
from src.ml.predict import load_classifier
from src.rag.pipeline import build_llm_client, load_rag_index


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    configure_logging(settings.log_level)
    app.state.settings = settings
    try:
        app.state.classifier = load_classifier(settings=settings)
    except FileNotFoundError:
        app.state.classifier = None
    try:
        app.state.rag_index = load_rag_index(settings=settings)
    except Exception as exc:
        # A mensagem pode ecoar a chave do provedor; o log fica só com o tipo.
        app.state.rag_index = None
        logger.warning(
            "rag_index_unavailable error=%s path=%s",
            type(exc).__name__,
            settings.manual_path,
        )
    app.state.llm = build_llm_client(settings)
    yield
    app.state.classifier = None
    app.state.rag_index = None
    app.state.llm = None


def create_app() -> FastAPI:
    app = FastAPI(
        title="Support Copilot",
        description="Triagem clássica, RAG de manual e Guardrails (Datathon Grupo 40).",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.include_router(router)
    return app


app = create_app()
