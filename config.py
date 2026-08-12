from pathlib import Path
import os
import yaml

DEFAULT_CONFIG = Path(__file__).parent / "config" / "default_study.yaml"


def load_study_config(path: str | None = None) -> dict:
    config_path = Path(path) if path else DEFAULT_CONFIG
    with config_path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def database_url() -> str:
    return os.getenv("DATABASE_URL", "sqlite:///human_performance.db")


def api_base_url() -> str:
    return os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/")


def researcher_username() -> str:
    return os.getenv("RESEARCHER_USERNAME", "admin")


def researcher_password() -> str:
    return os.getenv("RESEARCHER_PASSWORD", "change-me")
