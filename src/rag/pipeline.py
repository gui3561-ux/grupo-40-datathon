from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_core.embeddings import FakeEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config import Settings, get_settings

NOT_IN_MANUAL = "A informação não foi encontrada no manual."
SYSTEM_PROMPT = (
    "Você é um Copilot de suporte. Responda SOMENTE com o conteúdo do manual abaixo. "
    "Se a resposta não estiver no manual, diga exatamente: "
    f'"{NOT_IN_MANUAL}" '
    "Não invente procedimentos fora do PDF."
)


class LlmClient(Protocol):
    def invoke(self, prompt: str) -> str: ...


@dataclass
class RagIndex:
    vectorstore: FAISS

    def retrieve(self, query: str, k: int = 4) -> list[str]:
        docs = self.vectorstore.similarity_search(query, k=k)
        return [doc.page_content for doc in docs]


def build_prompt(question: str, chunks: list[str]) -> str:
    context = "\n\n".join(chunks)
    return f"{SYSTEM_PROMPT}\n\nManual:\n{context}\n\nPergunta:\n{question}"


def answer_from_context(question: str, chunks: list[str], llm: LlmClient | None) -> str:
    cleaned = [chunk.strip() for chunk in chunks if chunk.strip()]
    if not cleaned:
        return NOT_IN_MANUAL
    if llm is None:
        raise RuntimeError("llm_missing")
    return llm.invoke(build_prompt(question, cleaned))


def _embeddings(settings: Settings):
    key = settings.llm_api_key
    if settings.llm_provider == "openai" and key:
        from langchain_openai import OpenAIEmbeddings

        return OpenAIEmbeddings(api_key=key)
    if settings.llm_provider == "gemini" and key:
        from langchain_google_genai import GoogleGenerativeAIEmbeddings

        return GoogleGenerativeAIEmbeddings(model="models/text-embedding-004", google_api_key=key)
    return FakeEmbeddings(size=64)


def load_rag_index(manual_path: Path | None = None, settings: Settings | None = None) -> RagIndex:
    cfg = settings or get_settings()
    path = manual_path or cfg.manual_path
    documents = PyPDFLoader(str(path)).load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=120)
    chunks = splitter.split_documents(documents)
    store = FAISS.from_documents(chunks, _embeddings(cfg))
    return RagIndex(vectorstore=store)


class GeminiClient:
    def __init__(self, api_key: str) -> None:
        from langchain_google_genai import ChatGoogleGenerativeAI

        self._model = ChatGoogleGenerativeAI(model="gemini-2.0-flash", api_key=api_key, temperature=0)

    def invoke(self, prompt: str) -> str:
        return str(self._model.invoke(prompt).content)


class OpenAiClient:
    def __init__(self, api_key: str) -> None:
        from langchain_openai import ChatOpenAI

        self._model = ChatOpenAI(model="gpt-4o-mini", api_key=api_key, temperature=0)

    def invoke(self, prompt: str) -> str:
        return str(self._model.invoke(prompt).content)


def build_llm_client(settings: Settings | None = None) -> LlmClient | None:
    cfg = settings or get_settings()
    key = cfg.llm_api_key
    if not key:
        return None
    if cfg.llm_provider == "openai":
        return OpenAiClient(key)
    return GeminiClient(key)
