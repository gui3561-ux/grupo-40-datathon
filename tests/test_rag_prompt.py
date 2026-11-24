from src.config import Settings
from src.rag.pipeline import (
    NOT_IN_MANUAL,
    GeminiClient,
    answer_from_context,
    build_prompt,
    message_text,
)
from tests.conftest import RecordingLlm


def test_empty_context_refuses_without_llm() -> None:
    fake = RecordingLlm()
    answer = answer_from_context("Qual a senha da NASA?", [], fake)
    assert answer == NOT_IN_MANUAL
    assert fake.calls == []


def test_message_text_keeps_plain_string() -> None:
    assert message_text("Pressione Reset por 10 segundos.") == "Pressione Reset por 10 segundos."


def test_message_text_drops_signature_block() -> None:
    block = [
        {
            "type": "text",
            "text": "Pressione Reset por 10 segundos.",
            "extras": {"signature": "segredo-do-modelo"},
        }
    ]
    answer = message_text(block)
    assert answer == "Pressione Reset por 10 segundos."
    assert "signature" not in answer
    assert "segredo-do-modelo" not in answer
    assert "extras" not in answer


def test_gemini_client_returns_plain_answer(monkeypatch) -> None:
    class _Message:
        content = [
            {
                "type": "text",
                "text": "Pressione Reset por 10 segundos.",
                "extras": {"signature": "segredo-do-modelo"},
            }
        ]

    class _Chat:
        def __init__(self, **_kwargs) -> None:
            pass

        def invoke(self, _prompt: str) -> _Message:
            return _Message()

    monkeypatch.setattr("langchain_google_genai.ChatGoogleGenerativeAI", _Chat)
    client = GeminiClient("k", Settings(_env_file=None, gemini_api_key="k"))
    answer = client.invoke("Como resetar?")
    assert answer == "Pressione Reset por 10 segundos."
    assert "segredo-do-modelo" not in answer


def test_prompt_instructs_manual_only() -> None:
    prompt = build_prompt("Como resetar?", ["Pressione Reset por 10 segundos."])
    assert "SOMENTE" in prompt or "somente" in prompt.lower()
    assert NOT_IN_MANUAL in prompt
