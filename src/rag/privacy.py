from __future__ import annotations

import re

CPF_DOTTED = re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b")
CPF_DIGITS = re.compile(r"\b\d{11}\b")
EMAIL = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
# Telefone com separador. Onze dígitos colados ficam para a janela da pista,
# senão um CPF nú seria cortado no meio.
PHONE_PLUS = re.compile(r"\+55\s?(?:\(?\d{2}\)?\s?)?\d{4,5}-?\d{4}\b")
PHONE_PAREN = re.compile(r"\(\d{2}\)\s?\d{4,5}-?\d{4}\b")
PHONE_GLUED_HYPHEN = re.compile(r"\b\d{2}\d{4,5}-\d{4}\b")
PHONE_SPACED = re.compile(r"\b\d{2}\s\d{4,5}-?\d{4}\b")
PHONE_LOCAL = re.compile(r"\b\d{4,5}-\d{4}\b")
CUE = r"(?:whatsapp|telefone|celular|fone|tel)"
BARE_AFTER_CUE = re.compile(rf"(\b{CUE}\b.{{0,24}}?)(\d{{11}}\b)", re.I)
BARE_BEFORE_CUE = re.compile(rf"(\b\d{{11}})(.{{0,24}}?\b{CUE}\b)", re.I)


def _redact_bare_near_cue(text: str) -> str:
    text = BARE_AFTER_CUE.sub(lambda match: f"{match.group(1)}[PHONE]", text)
    return BARE_BEFORE_CUE.sub(lambda match: f"[PHONE]{match.group(2)}", text)


def redact_pii(text: str) -> str:
    redacted = PHONE_PLUS.sub("[PHONE]", text)
    redacted = PHONE_PAREN.sub("[PHONE]", redacted)
    redacted = PHONE_GLUED_HYPHEN.sub("[PHONE]", redacted)
    redacted = PHONE_SPACED.sub("[PHONE]", redacted)
    redacted = PHONE_LOCAL.sub("[PHONE]", redacted)
    redacted = _redact_bare_near_cue(redacted)
    redacted = CPF_DOTTED.sub("[CPF]", redacted)
    redacted = EMAIL.sub("[EMAIL]", redacted)
    redacted = CPF_DIGITS.sub("[CPF]", redacted)
    return redacted
