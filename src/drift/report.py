from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
from evidently import DataDefinition, Dataset, Report
from evidently.presets import DataDriftPreset

from src.config import get_settings
from src.drift.simulate import write_production_csv

NON_LETTER = re.compile(r"[^A-Za-zÀ-ÿ]")


def add_text_descriptors(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    text = out["text"].astype(str)
    out["text_length"] = text.str.len()
    out["word_count"] = text.str.split().str.len()
    out["non_letter_ratio"] = text.map(lambda value: len(NON_LETTER.findall(value)) / max(len(value), 1))
    return out[["text_length", "word_count", "non_letter_ratio", "label"]]


def _definition() -> DataDefinition:
    return DataDefinition(
        numerical_columns=["text_length", "word_count", "non_letter_ratio"],
        categorical_columns=["label"],
    )


def drift_detected(snapshot) -> bool:
    payload = snapshot.dict()
    for metric in payload.get("metrics", []):
        name = str(metric.get("metric_name", ""))
        if "DriftedColumnsCount" not in name:
            continue
        value = metric.get("value", {})
        if isinstance(value, dict):
            return float(value.get("count", 0)) > 0
    return False


def build_report(
    current: pd.DataFrame,
    reference: pd.DataFrame,
    html_path: Path | None = None,
) -> dict[str, object]:
    settings = get_settings()
    target = html_path or settings.drift_html
    definition = _definition()
    current_ds = Dataset.from_pandas(add_text_descriptors(current), data_definition=definition)
    reference_ds = Dataset.from_pandas(add_text_descriptors(reference), data_definition=definition)
    report = Report([DataDriftPreset()])
    snapshot = report.run(current_ds, reference_ds)
    target.parent.mkdir(parents=True, exist_ok=True)
    snapshot.save_html(str(target))
    detected = drift_detected(snapshot)
    return {"html_path": str(target), "drift_detected": detected}


def run_degraded_report() -> dict[str, object]:
    settings = get_settings()
    reference = pd.read_csv(settings.tickets_csv)
    production = write_production_csv()
    return build_report(production, reference)


def run_control_report(html_path: Path | None = None) -> dict[str, object]:
    settings = get_settings()
    reference = pd.read_csv(settings.tickets_csv)
    path = html_path or settings.drift_html.with_name("drift_control.html")
    return build_report(reference, reference, html_path=path)


def main() -> None:
    degraded = run_degraded_report()
    control = run_control_report()
    print({"degraded": degraded, "control": control})


if __name__ == "__main__":
    main()
