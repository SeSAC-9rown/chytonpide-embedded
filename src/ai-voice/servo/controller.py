#!/usr/bin/env python3
"""
서보 모터 제어 모듈

Google AIY Voice Bonnet을 사용한 SG90 서보 모터 제어를 위한 재사용 가능한 모듈입니다.
"""

from time import sleep

from aiy.pins import PIN_B
from gpiozero import Servo

# SG90 서보 모터 펄스 폭 설정 (초 단위)
MIN_PULSE_WIDTH = 0.0005  # 500 마이크로초 (최소 각도)
MAX_PULSE_WIDTH = 0.0019  # 1900 마이크로초 (최대 각도)

# 기본 중립 각도
NEUTRAL_ANGLE = 90


class ServoController:
    """서보 모터 제어 클래스"""

    def __init__(
        self,
        pin=PIN_B,
        min_pulse=MIN_PULSE_WIDTH,
        max_pulse=MAX_PULSE_WIDTH,
        neutral_angle=NEUTRAL_ANGLE,
    ):
        """
        서보 컨트롤러 초기화

        Args:
            pin: 사용할 GPIO 핀 (PIN_A, PIN_B, PIN_C, PIN_D 중 선택)
            min_pulse: 최소 펄스 폭 (초)
            max_pulse: 최대 펄스 폭 (초)
            neutral_angle: 중립 각도 (기본값: 90도)
        """
        self.pin = pin
        self.neutral_angle = neutral_angle
        self.current_angle = neutral_angle
        self.servo = Servo(pin, min_pulse_width=min_pulse, max_pulse_width=max_pulse)

        # 초기 위치를 중립으로 설정
        self.move_to_angle(neutral_angle, delay=0.5)

    def _angle_to_value(self, angle):
        """
        각도(0~180)를 서보 값(-1.0~1.0)으로 변환

        Args:
            angle: 각도 (0~180)

        Returns:
            서보 값 (-1.0~1.0)
        """
        angle = max(0, min(180, angle))
        return (angle / 90.0) - 1.0

    def move_to_angle(self, angle, delay=0.5):
        """
        서보 모터를 지정한 각도로 이동

        Args:
            angle: 이동할 각도 (0~180)
            delay: 이동 후 대기 시간 (초)
        """
        value = self._angle_to_value(angle)
        self.servo.value = value
        self.current_angle = angle
        sleep(delay)

    def move_to_neutral(self, delay=0.5):
        """
        서보 모터를 중립 위치로 이동

        Args:
            delay: 이동 후 대기 시간 (초)
        """
        self.move_to_angle(self.neutral_angle, delay)

    def sweep(self, start_angle, end_angle, step=1, delay=0.02):
        """
        서보 모터를 부드럽게 스위핑

        Args:
            start_angle: 시작 각도 (0~180)
            end_angle: 끝 각도 (0~180)
            step: 각도 증가/감소 폭
            delay: 각 단계 사이의 지연 시간 (초)
        """
        if start_angle < end_angle:
            # 앞으로 스위핑
            for angle in range(start_angle, end_angle + 1, step):
                self.move_to_angle(angle, delay=0)
                sleep(delay)
        else:
            # 뒤로 스위핑
            for angle in range(start_angle, end_angle - 1, -step):
                self.move_to_angle(angle, delay=0)
                sleep(delay)
        self.current_angle = end_angle

    def shake_smooth(
        self, min_angle, max_angle, repeat=1, step=2, delay=0.02, return_to_neutral=True
    ):
        """
        두 각도 사이를 부드럽게 왔다갔다 하는 동작 (흔들기)

        Args:
            min_angle: 최소 각도 (0~180)
            max_angle: 최대 각도 (0~180)
            repeat: 반복 횟수
            step: 각도 증가/감소 폭 (작을수록 부드러움, 기본값: 2)
            delay: 각 단계 사이의 지연 시간 (초, 작을수록 빠름, 기본값: 0.02)
            return_to_neutral: 완료 후 중립 위치로 복귀할지 여부 (기본값: True)
        """
        for i in range(repeat):
            # 최소 각도에서 최대 각도로
            self.sweep(min_angle, max_angle, step=step, delay=delay)
            # 최대 각도에서 최소 각도로
            self.sweep(max_angle, min_angle, step=step, delay=delay)

        if return_to_neutral:
            self.move_to_neutral(delay=0.5)

    def plant_shake(self, repeat=5, min_angle=45, max_angle=135, step=2, delay=0.02):
        """
        화분 흔들기 동작: 90도 -> (45도 -> 135도) x N회 -> 90도

        Args:
            repeat: 반복 횟수 (기본값: 5)
            min_angle: 최소 각도 (기본값: 45)
            max_angle: 최대 각도 (기본값: 135)
            step: 각도 증가/감소 폭 (기본값: 2, 작을수록 부드러움)
            delay: 각 단계 사이의 지연 시간 (초, 기본값: 0.02)
        """
        # 중립 위치로 이동
        self.move_to_neutral(delay=0.5)

        # 부드럽게 흔들기
        self.shake_smooth(
            min_angle=min_angle,
            max_angle=max_angle,
            repeat=repeat,
            step=step,
            delay=delay,
            return_to_neutral=True,
        )

    def cleanup(self):
        """리소스 정리"""
        try:
            self.move_to_neutral(delay=0.5)
            self.servo.value = None
            self.servo.close()
        except Exception:
            pass
