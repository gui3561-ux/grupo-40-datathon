from __future__ import annotations

import re

CPF_DOTTED = re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b")
CPF_DIGITS = re.compile(r"\b\d{11}\b")
EMAIL = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
PHONE = re.compile(
    r"(?:\+55\s?)(?:\(?\d{2}\)?\s?)?\d{4,5}-?\d{4}\b"
    r"|(?:\(?\d{2}\)?\s)\d{4,5}-?\d{4}\b"
    r"|\b\d{4,5}-\d{4}\b"
)


def redact_pii(text: str) -> str:
    redacted = CPF_DOTTED.sub("[CPF]", text)
    redacted = EMAIL.sub("[EMAIL]", redacted)
    redacted = CPF_DIGITS.sub("[CPF]", redacted)
    redacted = PHONE.sub("[PHONE]", redacted)
    return redacted
