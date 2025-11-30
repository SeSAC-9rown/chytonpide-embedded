# 서보 모터 제어 모듈

Google AIY Voice Bonnet을 사용한 SG90 서보 모터 제어를 위한 Python 모듈입니다.

## 구조

```
servo/
├── __init__.py          # 패키지 초기화 및 export
├── controller.py        # ServoController 클래스 (핵심 모듈)
├── examples/            # 예제 프로그램들
│   ├── plant_shaker.py         # 화분 흔들기 예제
│   ├── test_servo.py           # 기본 테스트 예제
│   └── test_servo_degree.py    # 대화형 각도 제어 예제
└── README.md            # 이 파일
```

## 설치

Voice Bonnet 시스템 이미지에 필요한 라이브러리가 기본적으로 포함되어 있습니다.
만약 없다면:

```bash
sudo apt-get update
sudo apt-get install python3-gpiozero
```

## 사용 방법

### 기본 사용법

```python
from servo import ServoController

# 서보 컨트롤러 생성
controller = ServoController()

# 특정 각도로 이동
controller.move_to_angle(90)

# 화분 흔들기 동작: 90도 -> (45도 <-> 135도) x 5회 -> 90도
controller.plant_shake(repeat=5)

# 리소스 정리
controller.cleanup()
```

### 예제 실행

```bash
# 화분 흔들기 예제
sudo python3 servo/examples/plant_shaker.py

# 기본 테스트 예제
sudo python3 servo/examples/test_servo.py

# 대화형 각도 제어 예제
sudo python3 servo/examples/test_servo_degree.py
```

## API 문서

### ServoController 클래스

#### 초기화

```python
ServoController(
    pin=PIN_B,                    # GPIO 핀 (기본값: PIN_B)
    min_pulse=0.0005,             # 최소 펄스 폭 (초)
    max_pulse=0.0019,             # 최대 펄스 폭 (초)
    neutral_angle=90              # 중립 각도 (기본값: 90도)
)
```

#### 주요 메서드

- `move_to_angle(angle, delay=0.5)`: 지정한 각도로 이동
- `move_to_neutral(delay=0.5)`: 중립 위치(90도)로 이동
- `sweep(start_angle, end_angle, step=1, delay=0.02)`: 부드럽게 스위핑
- `shake_smooth(min_angle, max_angle, repeat=1, step=2, delay=0.02, return_to_neutral=True)`: 두 각도 사이를 반복
- `plant_shake(repeat=5, min_angle=45, max_angle=135, step=2, delay=0.02)`: 화분 흔들기 동작
- `cleanup()`: 리소스 정리

## 연결 방법

- **빨간선(VCC)**: Voice Bonnet의 5V 핀
- **검은선(GND)**: Voice Bonnet의 GND 핀
- **주황/노란선(Signal)**: Voice Bonnet의 PIN_B (또는 PIN_A, PIN_C, PIN_D)

## 주의사항

- **반드시 sudo 권한으로 실행해야 합니다**
- 각 서보 모델마다 특성이 다를 수 있으므로 `MIN_PULSE_WIDTH`와 `MAX_PULSE_WIDTH` 값을 조정할 수 있습니다
