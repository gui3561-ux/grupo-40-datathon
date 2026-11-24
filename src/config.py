from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    model_path: Path = ROOT / "models" / "ticket_classifier.joblib"
    tickets_csv: Path = ROOT / "data" / "processed" / "tickets.csv"
    manual_path: Path = ROOT / "manuals" / "router-manual.pdf"
    drift_html: Path = ROOT / "reports" / "drift_report.html"
    production_csv: Path = ROOT / "data" / "processed" / "tickets_production.csv"
    mlflow_tracking_uri: str = "sqlite:///mlflow.db"
    mlflow_experiment: str = "support-copilot-triage"
    llm_provider: str = "gemini"
    gemini_api_key: str | None = None
    gemini_chat_model: str = "gemini-3.1-flash-lite"
    gemini_embedding_model: str = "gemini-embedding-001"
    openai_api_key: str | None = None
    log_level: str = "INFO"
    model_id: str = "ticket_classifier"

    @property
    def llm_api_key(self) -> str | None:
        if self.llm_provider == "openai":
            return self.openai_api_key
        return self.gemini_api_key


def get_settings() -> Settings:
    return Settings()
