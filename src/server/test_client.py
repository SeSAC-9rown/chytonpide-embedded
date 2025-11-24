"""
간단한 테스트 클라이언트 스크립트
서버가 정상 작동하는지 확인하기 위한 테스트 코드
"""
import requests
import time
import random

SERVER_URL = "http://localhost:8000"


def test_health_check():
    """Health check 엔드포인트 테스트"""
    print("Testing health check...")
    try:
        response = requests.get(f"{SERVER_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_sensor_data(temperature=None, humidity=None, device_id="test-device"):
    """센서 데이터 전송 테스트"""
    if temperature is None:
        temperature = round(random.uniform(20.0, 30.0), 2)
    if humidity is None:
        humidity = round(random.uniform(40.0, 80.0), 2)
    
    data = {
        "temperature": temperature,
        "humidity": humidity,
        "device_id": device_id
    }
    
    print(f"\nSending sensor data: {data}")
    try:
        response = requests.post(f"{SERVER_URL}/sensor/data", json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    print("=" * 50)
    print("Citonphyde Sensor Server Test Client")
    print("=" * 50)
    
    # Health check
    if not test_health_check():
        print("\n❌ Health check failed. Is the server running?")
        print("Run: python main.py")
        return
    
    print("\n✅ Health check passed!")
    
    # 단일 센서 데이터 전송
    print("\n" + "=" * 50)
    print("Testing single sensor data transmission...")
    test_sensor_data(25.5, 60.0, "ESP32-S3-001")
    
    # 여러 번 데이터 전송 (시뮬레이션)
    print("\n" + "=" * 50)
    print("Simulating multiple sensor readings...")
    for i in range(5):
        print(f"\n--- Reading {i+1}/5 ---")
        test_sensor_data(device_id=f"ESP32-S3-{i+1:03d}")
        time.sleep(1)
    
    print("\n" + "=" * 50)
    print("✅ All tests completed!")


if __name__ == "__main__":
    main()

