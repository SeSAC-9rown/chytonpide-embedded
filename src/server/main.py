from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import uvicorn

app = FastAPI(title="Citonphyde Sensor Server", version="1.0.0")


class SensorData(BaseModel):
    temperature: float
    humidity: float
    device_id: str = "unknown"
    timestamp: str = None


@app.get("/")
async def root():
    return {
        "message": "Citonphyde Sensor Server",
        "status": "running",
        "endpoints": {
            "POST /sensor/data": "Send sensor data (temperature, humidity)",
            "GET /health": "Health check"
        }
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.post("/sensor/data")
async def receive_sensor_data(data: SensorData):
    """
    SHT31 센서 데이터를 받는 엔드포인트
    
    Request Body:
    {
        "temperature": 25.5,
        "humidity": 60.0,
        "device_id": "ESP32-S3-001",
        "timestamp": "2024-01-01T12:00:00" (optional)
    }
    """
    # 타임스탬프가 없으면 서버에서 생성
    if not data.timestamp:
        data.timestamp = datetime.now().isoformat()
    
    # 로그 출력
    print("=" * 50)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 센서 데이터 수신")
    print(f"  Device ID: {data.device_id}")
    print(f"  온도: {data.temperature:.2f} °C")
    print(f"  습도: {data.humidity:.2f} %")
    print(f"  Timestamp: {data.timestamp}")
    print("=" * 50)
    
    # 응답 반환
    return {
        "status": "success",
        "message": "Sensor data received",
        "received_data": {
            "device_id": data.device_id,
            "temperature": data.temperature,
            "humidity": data.humidity,
            "timestamp": data.timestamp
        }
    }


if __name__ == "__main__":
    print("Starting Citonphyde Sensor Server...")
    print("Server will be available at http://localhost:8000")
    print("API docs available at http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)

