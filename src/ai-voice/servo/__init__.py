"""
서보 모터 제어 패키지

Google AIY Voice Bonnet을 사용한 SG90 서보 모터 제어를 위한 모듈입니다.

사용 예시:
    from servo import ServoController
    
    controller = ServoController()
    controller.move_to_angle(90)
    controller.plant_shake(repeat=5)
    controller.cleanup()
"""

from .controller import ServoController, MIN_PULSE_WIDTH, MAX_PULSE_WIDTH, NEUTRAL_ANGLE

__all__ = ['ServoController', 'MIN_PULSE_WIDTH', 'MAX_PULSE_WIDTH', 'NEUTRAL_ANGLE']
