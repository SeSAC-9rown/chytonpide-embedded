from __future__ import annotations

from collections import defaultdict, deque
from statistics import mean, stdev

from common.schemas import SensorReading


FEATURE_COLUMNS = [
    "temperature",
    "humidity",
    "battery",
    "hour",
    "temp_diff",
    "humidity_diff",
    "temp_rolling_mean",
    "humidity_rolling_mean",
    "temp_rolling_std",
    "humidity_rolling_std",
]


class FeatureBuilder:
    def __init__(self, window_size: int = 5):
        self.window_size = window_size
        self.history: dict[str, deque[SensorReading]] = defaultdict(lambda: deque(maxlen=window_size))

    def build(self, reading: SensorReading) -> list[float]:
        previous = self.history[reading.device_id][-1] if self.history[reading.device_id] else None
        readings = list(self.history[reading.device_id]) + [reading]
        temperatures = [item.temperature for item in readings]
        humidities = [item.humidity for item in readings]

        temp_std = stdev(temperatures) if len(temperatures) > 1 else 0.0
        humidity_std = stdev(humidities) if len(humidities) > 1 else 0.0

        features = [
            reading.temperature,
            reading.humidity,
            reading.battery if reading.battery is not None else 100.0,
            float(reading.measured_at.hour),
            reading.temperature - previous.temperature if previous else 0.0,
            reading.humidity - previous.humidity if previous else 0.0,
            mean(temperatures),
            mean(humidities),
            temp_std,
            humidity_std,
        ]
        self.history[reading.device_id].append(reading)
        return features

