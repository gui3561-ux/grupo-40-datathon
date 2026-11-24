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


def test_bare_mobile_near_cue_is_phone_not_cpf() -> None:
    redacted = redact_pii("CPF 123.456.789-09 e telefone 11987654321")
    assert "[CPF]" in redacted
    assert "[PHONE]" in redacted
    assert "11987654321" not in redacted
    assert "123.456.789-09" not in redacted


def test_hyphenated_mobile_without_space_is_redacted() -> None:
    redacted = redact_pii("ligar tel 1198765-4321 agora")
    assert "[PHONE]" in redacted
    assert "1198765-4321" not in redacted
    assert "11987654321" not in redacted


def test_parenthesized_ddd_is_fully_redacted() -> None:
    redacted = redact_pii("chamar (11)98765-4321")
    assert redacted == "chamar [PHONE]"
