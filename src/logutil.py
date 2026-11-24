from __future__ import annotations

import logging

logger = logging.getLogger("support_copilot")


def configure_logging(level: str) -> None:
    logging.basicConfig(level=level.upper(), format="%(name)s %(levelname)s %(message)s")


def log_request(
    *,
    endpoint: str,
    category: str | None,
    blocked: bool,
    reason: str | None,
    text_length: int,
    latency_ms: float,
) -> None:
    logger.info(
        "endpoint=%s category=%s blocked=%s reason=%s text_length=%s latency_ms=%.2f",
        endpoint,
        category,
        blocked,
        reason,
        text_length,
        latency_ms,
    )
