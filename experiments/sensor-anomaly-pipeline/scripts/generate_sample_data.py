from __future__ import annotations

import csv
import math
import random
from datetime import datetime, timedelta
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT_DIR / "data" / "processed" / "sensor_readings.csv"


def main() -> None:
    random.seed(42)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    start = datetime(2026, 5, 29, 9, 0, 0)
    devices = ["plant-001", "plant-002", "plant-003"]

    rows = []
    for i in range(240):
        measured_at = start + timedelta(minutes=i)
        for device_index, device_id in enumerate(devices):
            daily_wave = math.sin(i / 24)
            temperature = 25 + daily_wave * 2 + random.uniform(-0.5, 0.5) + device_index
            humidity = 62 - daily_wave * 4 + random.uniform(-1.0, 1.0) - device_index
            battery = 96 - i * 0.01 - device_index

            # Inject deterministic faults for demo and tests.
            if device_id == "plant-001" and 70 <= i < 73:
                temperature = 44 + random.uniform(0, 1)
            if device_id == "plant-002" and 120 <= i < 123:
                humidity = 12 + random.uniform(0, 2)
            if device_id == "plant-003" and 165 <= i < 170:
                temperature = 19.0
                humidity = 48.0
            if device_id == "plant-002" and i == 190:
                temperature += 16
                humidity -= 24

            rows.append(
                {
                    "device_id": device_id,
                    "temperature": round(temperature, 2),
                    "humidity": round(humidity, 2),
                    "battery": round(battery, 2),
                    "measured_at": measured_at.isoformat(),
                }
            )

    with OUTPUT_PATH.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["device_id", "temperature", "humidity", "battery", "measured_at"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"wrote {len(rows)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

