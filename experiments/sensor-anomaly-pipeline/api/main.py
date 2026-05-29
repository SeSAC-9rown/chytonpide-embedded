from __future__ import annotations

import uvicorn
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from common.config import settings
from common.storage import SensorStorage


app = FastAPI(title="Sensor Anomaly API")
storage = SensorStorage(settings.database_path)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/readings/recent")
def recent_readings(limit: int = Query(default=100, ge=1, le=1000)) -> list[dict]:
    return storage.get_recent_readings(limit=limit)


@app.get("/anomalies/recent")
def recent_anomalies(limit: int = Query(default=100, ge=1, le=1000)) -> list[dict]:
    return storage.get_recent_anomalies(limit=limit)


@app.get("/devices/{device_id}/readings")
def device_readings(device_id: str, limit: int = Query(default=100, ge=1, le=1000)) -> list[dict]:
    return storage.get_recent_readings(limit=limit, device_id=device_id)


@app.get("/devices/{device_id}/anomalies")
def device_anomalies(device_id: str, limit: int = Query(default=100, ge=1, le=1000)) -> list[dict]:
    return storage.get_recent_anomalies(limit=limit, device_id=device_id)


if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)

