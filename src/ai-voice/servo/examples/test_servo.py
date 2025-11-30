#!/usr/bin/env python3
"""
Google AIY Voice Bonnet이 장착된 Raspberry Pi Zero WH에서 SG90 서보 모터 제어 예제 코드

Voice Bonnet의 전용 MCU를 통해 GPIO 확장 핀을 사용하여 서보 모터를 제어합니다.
Voice Bonnet의 GPIO 핀은 Raspberry Pi의 CPU를 사용하지 않고도 더 정밀한 PWM 제어를 제공합니다.

연결 방법:
- 빨간선(VCC): Voice Bonnet의 5V 핀
- 검은선(GND): Voice Bonnet의 GND 핀
- 주황/노란선(Signal): Voice Bonnet의 PIN_B (또는 PIN_A, PIN_C, PIN_D 사용 가능)

필요한 라이브러리:
Voice Bonnet 시스템 이미지에 기본적으로 포함되어 있습니다.
만약 없다면:
sudo apt-get update
sudo apt-get install python3-gpiozero
"""

import sys
import os

# 현재 파일의 절대 경로: ~/chytonpide/servo/examples/test_servo.py
current_file = os.path.abspath(__file__)
# examples 디렉토리: ~/chytonpide/servo/examples/
examples_dir = os.path.dirname(current_file)
# servo 디렉토리: ~/chytonpide/servo/
servo_dir = os.path.dirname(examples_dir)
# servo의 부모 디렉토리: ~/chytonpide/
parent_dir = os.path.dirname(servo_dir)

# ~/chytonpide/를 Python 경로에 추가하여 servo 패키지를 찾을 수 있게 함
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from servo import ServoController


def main():
    """메인 함수"""
    controller = None

    try:
        print("Voice Bonnet 서보 모터 초기화 중...")
        print("PIN_B를 사용하여 서보 모터를 제어합니다.")

        # 서보 컨트롤러 생성
        controller = ServoController()
        print("서보 모터 준비 완료!")

        # 초기화 대기
        from time import sleep

        sleep(1)

        # 예제 1: 기본 동작 (최소, 중립, 최대 위치)
        print("\n=== 예제 1: 기본 동작 ===")
        controller.move_to_angle(180, delay=1.0)
        print("최대 위치(180도)로 이동 완료")

        controller.move_to_angle(90, delay=1.0)
        print("중립 위치(90도)로 이동 완료")

        controller.move_to_angle(0, delay=1.0)
        print("최소 위치(0도)로 이동 완료")

        controller.move_to_angle(90, delay=1.0)
        print("중립 위치(90도)로 복귀 완료")

        # 예제 2: 특정 각도로 이동
        print("\n=== 예제 2: 특정 각도로 이동 ===")
        angles = [0, 45, 90, 135, 180, 90]
        for angle in angles:
            print(f"{angle}도로 이동 중...")
            controller.move_to_angle(angle, delay=1.0)

        sleep(1)

        # 예제 3: 부드러운 스위핑 (0도 -> 180도 -> 0도)
        print("\n=== 예제 3: 부드러운 스위핑 ===")
        print("0도에서 180도로 이동...")
        controller.sweep(0, 180, step=1, delay=0.02)

        sleep(0.5)

        print("180도에서 0도로 이동...")
        controller.sweep(180, 0, step=1, delay=0.02)

        sleep(1)

        # 예제 4: 연속 반복
        print("\n=== 예제 4: 연속 반복 (5회) ===")
        for i in range(5):
            print(f"반복 {i+1}/5")
            controller.shake_smooth(0, 180, repeat=1, step=2, delay=0.01, return_to_neutral=False)

        # 중립 위치로 복귀
        print("\n중립 위치(90도)로 복귀...")
        controller.move_to_neutral(delay=1.0)

        print("\n프로그램 완료!")

    except KeyboardInterrupt:
        print("\n프로그램이 중단되었습니다.")
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback

        traceback.print_exc()
    finally:
        if controller is not None:
            print("\n정리 중...")
            controller.cleanup()
            print("정리 완료.")


if __name__ == "__main__":
    main()
