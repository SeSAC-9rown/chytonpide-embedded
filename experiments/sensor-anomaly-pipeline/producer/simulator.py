from __future__ import annotations

import argparse
import csv
import json
import time

from confluent_kafka import Producer

from common.config import settings
from common.schemas import SensorReading


def delivery_report(err, msg) -> None:
    if err is not None:
        print(f"delivery failed: {err}")
    else:
        print(f"published topic={msg.topic()} partition={msg.partition()} offset={msg.offset()}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish CSV sensor readings to Kafka.")
    parser.add_argument("--limit", type=int, default=None, help="Maximum number of rows to publish.")
    parser.add_argument(
        "--interval",
        type=float,
        default=settings.publish_interval_seconds,
        help="Delay between messages in seconds.",
    )
    args = parser.parse_args()

    if not settings.sensor_csv_path.exists():
        raise FileNotFoundError(
            f"CSV not found: {settings.sensor_csv_path}. Run `python scripts/generate_sample_data.py` first."
        )

    producer = Producer({"bootstrap.servers": settings.kafka_bootstrap_servers})
    print(f"Publishing {settings.sensor_csv_path} to topic={settings.sensor_topic}")

    with settings.sensor_csv_path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        for index, row in enumerate(reader):
            if args.limit is not None and index >= args.limit:
                break
            reading = SensorReading(
                device_id=row["device_id"],
                temperature=float(row["temperature"]),
                humidity=float(row["humidity"]),
                battery=float(row["battery"]) if row.get("battery") else None,
                measured_at=row["measured_at"],
            )
            payload = reading.model_dump(mode="json")
            producer.produce(
                settings.sensor_topic,
                key=reading.device_id,
                value=json.dumps(payload).encode("utf-8"),
                callback=delivery_report,
            )
            producer.poll(0)
            time.sleep(args.interval)

    producer.flush()


if __name__ == "__main__":
    main()
