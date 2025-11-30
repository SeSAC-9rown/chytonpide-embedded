#!/usr/bin/env python3
"""
터미널에서 각도를 입력받아 SG90 서보 모터를 제어하는 대화형 스크립트

Google AIY Voice Bonnet이 장착된 Raspberry Pi Zero WH에서 사용합니다.

연결 방법:
- 빨간선(VCC): Voice Bonnet의 5V 핀
- 검은선(GND): Voice Bonnet의 GND 핀
- 주황/노란선(Signal): Voice Bonnet의 PIN_B

사용 방법:
sudo python3 test_servo_degree.py

터미널에서 각도(0~180)를 입력하면 해당 각도로 서보 모터가 이동합니다.
종료하려면 'q', 'quit', 또는 Ctrl+C를 누르세요.

필요한 라이브러리:
Voice Bonnet 시스템 이미지에 기본적으로 포함되어 있습니다.
"""

import sys
import os

# 현재 파일의 절대 경로: ~/chytonpide/servo/examples/test_servo_degree.py
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


def print_help():
    """도움말 메시지 출력"""
    print("\n=== 사용 가능한 명령어 ===")
    print("  각도 (0~180): 해당 각도로 서보 모터 이동")
    print("  min 또는 0: 최소 위치로 이동")
    print("  mid 또는 90: 중립 위치로 이동")
    print("  max 또는 180: 최대 위치로 이동")
    print("  help 또는 h: 이 도움말 표시")
    print("  q 또는 quit: 프로그램 종료")
    print("=" * 30)


def parse_input(user_input):
    """
    사용자 입력을 파싱하여 각도 또는 명령어를 반환

    Args:
        user_input: 사용자 입력 문자열

    Returns:
        (명령 타입, 값) 튜플
        명령 타입: 'angle', 'min', 'mid', 'max', 'help', 'quit', 'invalid'
    """
    user_input = user_input.strip().lower()

    # 종료 명령
    if user_input in ['q', 'quit', 'exit']:
        return 'quit', None

    # 도움말
    if user_input in ['help', 'h', '?']:
        return 'help', None

    # 특정 위치 명령
    if user_input in ['min', '0']:
        return 'min', None
    if user_input in ['mid', '90']:
        return 'mid', None
    if user_input in ['max', '180']:
        return 'max', None

    # 숫자 입력 시도
    try:
        angle = float(user_input)
        # 각도 범위 확인
        if 0 <= angle <= 180:
            return 'angle', int(angle)
        else:
            return 'invalid', f"각도는 0~180 사이여야 합니다. (입력: {angle})"
    except ValueError:
        return 'invalid', f"잘못된 입력입니다: {user_input}"


def main():
    """메인 함수"""
    controller = None
    current_angle = None

    try:
        print("=" * 50)
        print("Voice Bonnet 서보 모터 각도 제어 프로그램")
        print("=" * 50)
        print("초기화 중...")

        # 서보 컨트롤러 생성
        controller = ServoController()
        print("서보 모터 준비 완료!")
        print("PIN_B를 사용하여 서보 모터를 제어합니다.")

        # 초기 위치를 중립(90도)으로 설정
        print("\n초기 위치(90도)로 이동 중...")
        controller.move_to_neutral()
        current_angle = 90

        print_help()
        print("\n현재 위치: 90도")
        print("각도를 입력하세요 (0~180, 'help' 도움말, 'q' 종료):")

        # 대화형 루프
        while True:
            try:
                user_input = input("\n> ").strip()

                if not user_input:
                    continue

                cmd_type, value = parse_input(user_input)

                if cmd_type == 'quit':
                    print("\n프로그램을 종료합니다.")
                    break

                elif cmd_type == 'help':
                    print_help()

                elif cmd_type == 'min':
                    print("최소 위치(0도)로 이동 중...")
                    controller.move_to_angle(0)
                    current_angle = 0
                    print(f"현재 위치: {current_angle}도")

                elif cmd_type == 'mid':
                    print("중립 위치(90도)로 이동 중...")
                    controller.move_to_neutral()
                    current_angle = 90
                    print(f"현재 위치: {current_angle}도")

                elif cmd_type == 'max':
                    print("최대 위치(180도)로 이동 중...")
                    controller.move_to_angle(180)
                    current_angle = 180
                    print(f"현재 위치: {current_angle}도")

                elif cmd_type == 'angle':
                    angle = value
                    print(f"{angle}도로 이동 중...")
                    controller.move_to_angle(angle)
                    current_angle = angle
                    print(f"현재 위치: {current_angle}도")

                elif cmd_type == 'invalid':
                    print(f"오류: {value}")
                    print("다시 입력하세요. ('help' 입력 시 도움말 확인)")

            except EOFError:
                # Ctrl+D 입력 시
                print("\n프로그램을 종료합니다.")
                break
            except KeyboardInterrupt:
                # Ctrl+C 입력 시
                print("\n\n프로그램을 종료합니다.")
                break

    except KeyboardInterrupt:
        print("\n프로그램이 중단되었습니다.")
    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback

        traceback.print_exc()
    finally:
        # 서보 모터 해제
        print("\n정리 중...")
        if controller is not None:
            try:
                # 중립 위치로 복귀
                if current_angle != 90:
                    print("중립 위치(90도)로 복귀 중...")
                    controller.move_to_neutral(delay=0.5)
                controller.cleanup()
            except Exception as e:
                print(f"정리 중 오류 (무시 가능): {e}")
        print("정리 완료.")


if __name__ == "__main__":
    main()
