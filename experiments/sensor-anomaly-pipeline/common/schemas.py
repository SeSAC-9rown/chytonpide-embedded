from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class SensorReading(BaseModel):
    device_id: str = Field(min_length=1)
    temperature: float
    humidity: float
    battery: float | None = None
    measured_at: datetime


AnomalyType = Literal[
    "TEMP_HIGH",
    "TEMP_LOW",
    "HUMIDITY_HIGH",
    "HUMIDITY_LOW",
    "SUDDEN_TEMP_CHANGE",
    "SUDDEN_HUMIDITY_CHANGE",
    "SENSOR_STUCK",
    "MODEL_ANOMALY",
]


class AnomalyEvent(BaseModel):
    device_id: str
    reading_id: int | None = None
    anomaly_type: AnomalyType
    anomaly_score: float | None = None
    reason: str
    measured_at: datetime
    detected_at: datetime = Field(default_factory=datetime.utcnow)

