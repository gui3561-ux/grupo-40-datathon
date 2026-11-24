from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from src.api.main import create_app
from src.config import ROOT
from src.ml.prepare_data import write_tickets_csv
from src.ml.train import train
from src.ml.write_manual import write_manual_pdf


@pytest.fixture(scope="session", autouse=True)
def artifacts() -> None:
    write_tickets_csv()
    write_manual_pdf()
    model = ROOT / "models" / "ticket_classifier.joblib"
    if not model.exists():
        train()


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
def client(app):
    with TestClient(app) as test_client:
        yield test_client


class RecordingLlm:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def invoke(self, prompt: str) -> str:
        self.calls.append(prompt)
        return "Use o DHCP na faixa 192.168.1.100 a 192.168.1.200 conforme o manual."
