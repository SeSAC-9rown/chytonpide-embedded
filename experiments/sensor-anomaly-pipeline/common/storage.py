from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from collections.abc import Iterator
from typing import Any

from common.schemas import AnomalyEvent, SensorReading


class SensorStorage:
    def __init__(self, database_path: Path):
        self.database_path = database_path
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.database_path)
        conn.row_factory = sqlite3.Row
        return conn

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        conn = self.connect()
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _init_db(self) -> None:
        with self.connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS sensor_readings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_id TEXT NOT NULL,
                    temperature REAL NOT NULL,
                    humidity REAL NOT NULL,
                    battery REAL,
                    measured_at TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS anomaly_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_id TEXT NOT NULL,
                    reading_id INTEGER,
                    anomaly_type TEXT NOT NULL,
                    anomaly_score REAL,
                    reason TEXT NOT NULL,
                    measured_at TEXT NOT NULL,
                    detected_at TEXT NOT NULL,
                    FOREIGN KEY(reading_id) REFERENCES sensor_readings(id)
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_readings_device_time ON sensor_readings(device_id, measured_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_anomalies_device_time ON anomaly_events(device_id, detected_at)")

    def insert_reading(self, reading: SensorReading) -> int:
        with self.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO sensor_readings (device_id, temperature, humidity, battery, measured_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    reading.device_id,
                    reading.temperature,
                    reading.humidity,
                    reading.battery,
                    reading.measured_at.isoformat(),
                ),
            )
            return int(cursor.lastrowid)

    def insert_anomaly(self, event: AnomalyEvent) -> int:
        with self.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO anomaly_events
                    (device_id, reading_id, anomaly_type, anomaly_score, reason, measured_at, detected_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.device_id,
                    event.reading_id,
                    event.anomaly_type,
                    event.anomaly_score,
                    event.reason,
                    event.measured_at.isoformat(),
                    event.detected_at.isoformat(),
                ),
            )
            return int(cursor.lastrowid)

    def get_recent_readings(self, limit: int = 100, device_id: str | None = None) -> list[dict[str, Any]]:
        query = "SELECT * FROM sensor_readings"
        params: list[Any] = []
        if device_id:
            query += " WHERE device_id = ?"
            params.append(device_id)
        query += " ORDER BY measured_at DESC LIMIT ?"
        params.append(limit)
        with self.connection() as conn:
            return [dict(row) for row in conn.execute(query, params)]

    def get_recent_anomalies(self, limit: int = 100, device_id: str | None = None) -> list[dict[str, Any]]:
        query = "SELECT * FROM anomaly_events"
        params: list[Any] = []
        if device_id:
            query += " WHERE device_id = ?"
            params.append(device_id)
        query += " ORDER BY detected_at DESC LIMIT ?"
        params.append(limit)
        with self.connection() as conn:
            return [dict(row) for row in conn.execute(query, params)]
