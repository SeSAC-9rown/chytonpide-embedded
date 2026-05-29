from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env")


def _path(name: str, default: str) -> Path:
    value = os.getenv(name, default)
    path = Path(value)
    return path if path.is_absolute() else ROOT_DIR / path


def _bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    kafka_bootstrap_servers: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    kafka_consumer_group_id: str = os.getenv("KAFKA_CONSUMER_GROUP_ID", "sensor-anomaly-detector")
    sensor_topic: str = os.getenv("SENSOR_TOPIC", "sensor-readings")
    anomaly_topic: str = os.getenv("ANOMALY_TOPIC", "anomaly-events")
    database_path: Path = _path("DATABASE_PATH", "./data/sensor_anomaly.db")
    sensor_csv_path: Path = _path("SENSOR_CSV_PATH", "./data/processed/sensor_readings.csv")
    model_path: Path = _path("MODEL_PATH", "./models/isolation_forest.joblib")
    model_anomaly_score_threshold: float = float(os.getenv("MODEL_ANOMALY_SCORE_THRESHOLD", "-0.08"))
    emit_uncorroborated_model_anomalies: bool = _bool("EMIT_UNCORROBORATED_MODEL_ANOMALIES", False)
    publish_interval_seconds: float = float(os.getenv("PUBLISH_INTERVAL_SECONDS", "1.0"))


settings = Settings()
