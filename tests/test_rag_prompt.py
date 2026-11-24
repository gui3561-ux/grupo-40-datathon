from src.rag.pipeline import NOT_IN_MANUAL, answer_from_context, build_prompt
from tests.conftest import RecordingLlm


def test_empty_context_refuses_without_llm() -> None:
    fake = RecordingLlm()
    answer = answer_from_context("Qual a senha da NASA?", [], fake)
    assert answer == NOT_IN_MANUAL
    assert fake.calls == []


def test_prompt_instructs_manual_only() -> None:
    prompt = build_prompt("Como resetar?", ["Pressione Reset por 10 segundos."])
    assert "SOMENTE" in prompt or "somente" in prompt.lower()
    assert NOT_IN_MANUAL in prompt
