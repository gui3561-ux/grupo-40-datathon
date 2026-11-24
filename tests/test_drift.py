from pathlib import Path

import pandas as pd

from src.config import get_settings
from src.drift.report import run_control_report, run_degraded_report
from src.drift.simulate import simulate_production


def test_simulated_production_differs_from_reference() -> None:
    reference = pd.read_csv(get_settings().tickets_csv)
    production = simulate_production(reference)
    assert production["text"].str.len().mean() > reference["text"].str.len().mean()
    assert production["label"].value_counts().idxmax() == "billing"
    assert not production["label"].value_counts().equals(reference["label"].value_counts())


def test_degraded_report_html_marks_drift(tmp_path: Path) -> None:
    result = run_degraded_report()
    html = Path(result["html_path"])
    assert html.exists()
    content = html.read_text(encoding="utf-8")
    assert "<html" in content.lower()
    assert result["drift_detected"] is True


def test_control_report_is_not_the_degraded_alert() -> None:
    degraded = run_degraded_report()
    control = run_control_report()
    assert degraded["drift_detected"] is True
    assert control["drift_detected"] is False
