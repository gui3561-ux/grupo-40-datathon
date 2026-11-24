from src.rag.privacy import redact_pii


def test_redact_cpf_email_phone() -> None:
    text = "CPF 123.456.789-09 email joao.silva@exemplo.com tel +55 11 98888-7777"
    redacted = redact_pii(text)
    assert "[CPF]" in redacted
    assert "[EMAIL]" in redacted
    assert "[PHONE]" in redacted
    assert "123.456.789-09" not in redacted
    assert "joao.silva@exemplo.com" not in redacted
    assert "98888-7777" not in redacted


def test_redact_cpf_digits_only() -> None:
    assert "[CPF]" in redact_pii("documento 12345678909 na ficha")
