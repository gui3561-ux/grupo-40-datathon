"""Treina TF-IDF + LogisticRegression e registra Accuracy/F1 no MLflow."""

from __future__ import annotations

import os
from pathlib import Path

import joblib
import mlflow
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from src.config import get_settings

NGRAM_RANGE = (1, 2)
MIN_DF = 2
MAX_ITER = 1000
TEST_SIZE = 0.2
RANDOM_STATE = 42
C_PARAM = 1.0


def build_pipeline() -> Pipeline:
    return Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(ngram_range=NGRAM_RANGE, min_df=MIN_DF),
            ),
            (
                "clf",
                LogisticRegression(
                    max_iter=MAX_ITER,
                    class_weight="balanced",
                    C=C_PARAM,
                    random_state=RANDOM_STATE,
                ),
            ),
        ]
    )


def train(csv_path: Path | None = None, model_path: Path | None = None) -> dict[str, float]:
    settings = get_settings()
    data_path = csv_path or settings.tickets_csv
    artifact_path = model_path or settings.model_path
    frame = pd.read_csv(data_path)
    texts = frame["text"].astype(str)
    labels = frame["label"].astype(str)
    x_train, x_test, y_train, y_test = train_test_split(
        texts,
        labels,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=labels,
    )
    pipeline = build_pipeline()
    pipeline.fit(x_train, y_train)
    y_pred = pipeline.predict(x_test)
    metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "f1_macro": float(f1_score(y_test, y_pred, average="macro")),
    }
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, artifact_path)

    os.environ.setdefault("MLFLOW_DISABLE_AGENT_HINT", "1")
    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    mlflow.set_experiment(settings.mlflow_experiment)
    with mlflow.start_run(run_name="ticket-triage"):
        mlflow.log_params(
            {
                "ngram_range": str(NGRAM_RANGE),
                "min_df": MIN_DF,
                "C": C_PARAM,
                "max_iter": MAX_ITER,
            }
        )
        mlflow.log_metrics(metrics)
        mlflow.log_artifact(str(artifact_path), artifact_path="model")
    return metrics


def main() -> None:
    metrics = train()
    print(metrics)


if __name__ == "__main__":
    main()
