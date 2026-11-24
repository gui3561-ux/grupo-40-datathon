from __future__ import annotations

from pathlib import Path

import joblib
from sklearn.pipeline import Pipeline

from src.config import Settings, get_settings


class TicketClassifier:
    def __init__(self, pipeline: Pipeline, model_id: str) -> None:
        self.pipeline = pipeline
        self.model_id = model_id

    def predict(self, text: str) -> tuple[str, float]:
        proba = self.pipeline.predict_proba([text])[0]
        index = int(proba.argmax())
        category = str(self.pipeline.classes_[index])
        return category, float(proba[index])


def load_classifier(path: Path | None = None, settings: Settings | None = None) -> TicketClassifier:
    cfg = settings or get_settings()
    model_path = path or cfg.model_path
    if not model_path.exists():
        raise FileNotFoundError(str(model_path))
    pipeline = joblib.load(model_path)
    return TicketClassifier(pipeline, cfg.model_id)
