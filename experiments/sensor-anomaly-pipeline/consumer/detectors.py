from __future__ import annotations

from collections import defaultdict, deque
from datetime import datetime

import joblib

from common.config import settings
from common.features import FeatureBuilder
from common.schemas import AnomalyEvent, SensorReading


class RuleBasedDetector:
    def __init__(self, stuck_window: int = 5):
        self.previous: dict[str, SensorReading] = {}
        self.stuck_values: dict[str, deque[tuple[float, float]]] = defaultdict(lambda: deque(maxlen=stuck_window))
        self.active_stuck_devices: set[str] = set()

    def detect(self, reading: SensorReading, reading_id: int | None = None) -> list[AnomalyEvent]:
        events: list[AnomalyEvent] = []
        now = datetime.utcnow()

        def add(anomaly_type: str, reason: str, score: float | None = None) -> None:
            events.append(
                AnomalyEvent(
                    device_id=reading.device_id,
                    reading_id=reading_id,
                    anomaly_type=anomaly_type,  # type: ignore[arg-type]
                    anomaly_score=score,
                    reason=reason,
                    measured_at=reading.measured_at,
                    detected_at=now,
                )
            )

        if reading.temperature > 40:
            add("TEMP_HIGH", f"temperature {reading.temperature:.1f}C is above 40C")
        if reading.temperature < 5:
            add("TEMP_LOW", f"temperature {reading.temperature:.1f}C is below 5C")
        if reading.humidity > 90:
            add("HUMIDITY_HIGH", f"humidity {reading.humidity:.1f}% is above 90%")
        if reading.humidity < 20:
            add("HUMIDITY_LOW", f"humidity {reading.humidity:.1f}% is below 20%")

        previous = self.previous.get(reading.device_id)
        if previous:
            temp_diff = abs(reading.temperature - previous.temperature)
            humidity_diff = abs(reading.humidity - previous.humidity)
            if temp_diff >= 10:
                add("SUDDEN_TEMP_CHANGE", f"temperature changed by {temp_diff:.1f}C from previous reading")
            if humidity_diff >= 20:
                add("SUDDEN_HUMIDITY_CHANGE", f"humidity changed by {humidity_diff:.1f}% from previous reading")

        values = self.stuck_values[reading.device_id]
        values.append((reading.temperature, reading.humidity))
        is_stuck = len(values) == values.maxlen and len(set(values)) == 1
        if is_stuck and reading.device_id not in self.active_stuck_devices:
            add("SENSOR_STUCK", "temperature and humidity did not change across the recent window")
            self.active_stuck_devices.add(reading.device_id)
        elif not is_stuck:
            self.active_stuck_devices.discard(reading.device_id)

        self.previous[reading.device_id] = reading
        return events


class IsolationForestDetector:
    def __init__(self):
        self.feature_builder = FeatureBuilder()
        self.model = joblib.load(settings.model_path) if settings.model_path.exists() else None

    def detect(self, reading: SensorReading, reading_id: int | None = None) -> list[AnomalyEvent]:
        if self.model is None:
            return []

        features = self.feature_builder.build(reading)
        prediction = int(self.model.predict([features])[0])
        score = float(self.model.decision_function([features])[0])
        if prediction != -1 or score > settings.model_anomaly_score_threshold:
            return []

        return [
            AnomalyEvent(
                device_id=reading.device_id,
                reading_id=reading_id,
                anomaly_type="MODEL_ANOMALY",
                anomaly_score=score,
                reason=(
                    "Isolation Forest score "
                    f"{score:.3f} is below threshold {settings.model_anomaly_score_threshold:.3f}"
                ),
                measured_at=reading.measured_at,
                detected_at=datetime.utcnow(),
            )
        ]
