from __future__ import annotations

import re
from dataclasses import dataclass

PROHIBITED_TERMS = (
    "cartao clonado",
    "cartão clonado",
    "credit card dump",
    "malware kit",
    "explosive recipe",
)

JAILBREAK_PATTERNS = (
    re.compile(r"ignore (the )?(pdf|manual|previous instructions)", re.I),
    re.compile(r"ignore o manual", re.I),
    re.compile(r"desconsidere (as instru[cç][oõ]es|o pdf|o manual)", re.I),
    re.compile(r"reveal (the )?system prompt", re.I),
    re.compile(r"\bjailbreak\b", re.I),
    re.compile(r"ignore previous instructions", re.I),
    re.compile(
        r"\b(esque[cç]a|esquece|ignora|ignore|desconsidere|n[aã]o siga)\b"
        r"\s+(?:o\s+|a\s+|as\s+)?(pdf|manual|instru[cç][oõ]es)\b",
        re.I,
    ),
    re.compile(
        r"\b(disregard|forget|do not follow)\b\s+(?:the\s+)?(pdf|manual|instructions)\b",
        re.I,
    ),
)


@dataclass(frozen=True)
class GuardrailDecision:
    blocked: bool
    reason: str | None = None


def inspect(text: str) -> GuardrailDecision:
    lowered = text.lower()
    for term in PROHIBITED_TERMS:
        if term in lowered:
            return GuardrailDecision(blocked=True, reason="prohibited_term")
    for pattern in JAILBREAK_PATTERNS:
        if pattern.search(text):
            return GuardrailDecision(blocked=True, reason="jailbreak")
    return GuardrailDecision(blocked=False)
