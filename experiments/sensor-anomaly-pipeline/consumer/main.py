from __future__ import annotations

import json
import signal
from typing import Any

from confluent_kafka import Consumer, Producer
from pydantic import ValidationError

from common.config import settings
from common.schemas import AnomalyEvent, SensorReading
from common.storage import SensorStorage
from consumer.detectors import IsolationForestDetector, RuleBasedDetector


running = True


def _shutdown(_signum: int, _frame: Any) -> None:
    global running
    running = False


def publish_anomaly(producer: Producer, event: AnomalyEvent) -> None:
    payload = event.model_dump(mode="json")
    producer.produce(
        settings.anomaly_topic,
        key=event.device_id,
        value=json.dumps(payload).encode("utf-8"),
    )


def main() -> None:
    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    storage = SensorStorage(settings.database_path)
    rule_detector = RuleBasedDetector()
    model_detector = IsolationForestDetector()

    consumer = Consumer(
        {
            "bootstrap.servers": settings.kafka_bootstrap_servers,
            "group.id": settings.kafka_consumer_group_id,
            "auto.offset.reset": "earliest",
            "enable.auto.commit": True,
        }
    )
    producer = Producer({"bootstrap.servers": settings.kafka_bootstrap_servers})
    consumer.subscribe([settings.sensor_topic])

    print(f"Consuming topic={settings.sensor_topic}")
    try:
        while running:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print(f"Kafka error: {msg.error()}")
                continue

            try:
                payload = json.loads(msg.value().decode("utf-8"))
                reading = SensorReading.model_validate(payload)
            except (json.JSONDecodeError, UnicodeDecodeError, ValidationError) as exc:
                print(f"Invalid message skipped: {exc}")
                continue

            reading_id = storage.insert_reading(reading)
            events = rule_detector.detect(reading, reading_id)
            if events or settings.emit_uncorroborated_model_anomalies:
                events.extend(model_detector.detect(reading, reading_id))

            for event in events:
                storage.insert_anomaly(event)
                publish_anomaly(producer, event)
                print(f"anomaly {event.anomaly_type} device={event.device_id} reason={event.reason}")
            producer.poll(0)
    finally:
        producer.flush(5)
        consumer.close()


if __name__ == "__main__":
    main()
