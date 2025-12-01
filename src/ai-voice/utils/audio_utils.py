#!/usr/bin/env python3
"""
오디오 파일 재생 유틸리티

공통 오디오 재생 함수들을 제공합니다.
"""

import logging
import os
import subprocess

logger = logging.getLogger(__name__)

# AIY Projects play_wav import 시도
try:
    from aiy.voice.audio import play_wav

    HAS_AIY_AUDIO = True
except ImportError:
    HAS_AIY_AUDIO = False


def play_intro_audio(tts=None, trigger_words=None, use_trigger_word=None):
    """intro.wav 파일 재생

    Args:
        tts: TTS 객체 (파일을 찾을 수 없거나 재생 실패 시 대체용)
        trigger_words: 트리거 단어 리스트 (대체용)
        use_trigger_word: 트리거 단어 사용 여부 (대체용)
    """
    # 현재 파일의 위치를 기준으로 경로 찾기
    current_file = os.path.abspath(__file__)
    utils_dir = os.path.dirname(current_file)
    ai_voice_dir = os.path.dirname(utils_dir)

    intro_paths = [
        # utils/audio/intro.wav (현재 디렉토리 기준)
        os.path.join(utils_dir, "audio", "intro.wav"),
        # ai-voice 디렉토리 기준
        os.path.join(ai_voice_dir, "utils", "audio", "intro.wav"),
        # 절대 경로 (라즈베리파이 기본 경로)
        "/home/pi/chytonpide/src/ai-voice/utils/audio/intro.wav",
        os.path.expanduser("~/chytonpide/src/ai-voice/utils/audio/intro.wav"),
    ]

    intro_file = None
    for path in intro_paths:
        abs_path = os.path.abspath(os.path.expanduser(path))
        if os.path.exists(abs_path):
            intro_file = abs_path
            break

    if not intro_file:
        logger.warning("intro.wav 파일을 찾을 수 없습니다. TTS로 대체합니다.")
        # 파일을 찾을 수 없으면 기본 안내 음성 재생
        if tts:
            if use_trigger_word and trigger_words:
                main_trigger = trigger_words[0] if trigger_words else "치피"
                if hasattr(tts, "speak"):
                    # SupertonTTS
                    tts.speak(
                        f"안녕하세요! 저는 {main_trigger}입니다. 대화하고 싶을 때 저를 불러주세요.",
                        language="ko",
                        style="neutral",
                    )
                elif hasattr(tts, "synthesize"):
                    # AzureSpeechRESTTTS
                    tts.synthesize(
                        f"안녕하세요! 저는 {main_trigger}입니다. 트리거 단어를 말씀해주세요."
                    )
            else:
                if hasattr(tts, "speak"):
                    tts.speak(
                        "안녕하세요! 저는 치피입니다. 말씀해주세요.",
                        language="ko",
                        style="neutral",
                    )
                elif hasattr(tts, "synthesize"):
                    tts.synthesize("안녕하세요! 저는 치피입니다. 말씀해주세요.")
        return

    try:
        logger.info(f"intro.wav 재생: {intro_file}")
        # AIY Projects play_wav 또는 aplay 사용
        if HAS_AIY_AUDIO:
            play_wav(intro_file)
        else:
            subprocess.run(["aplay", "-q", intro_file], check=True)
        logger.debug("intro.wav 재생 완료")
    except Exception as e:
        logger.error(f"intro.wav 재생 오류: {e}", exc_info=True)
        # 재생 실패 시 TTS로 대체
        if tts:
            if use_trigger_word and trigger_words:
                main_trigger = trigger_words[0] if trigger_words else "치피"
                if hasattr(tts, "speak"):
                    tts.speak(
                        f"안녕하세요! 저는 {main_trigger}입니다. 대화하고 싶을 때 저를 불러주세요.",
                        language="ko",
                        style="neutral",
                    )
                elif hasattr(tts, "synthesize"):
                    tts.synthesize(
                        f"안녕하세요! 저는 {main_trigger}입니다. 트리거 단어를 말씀해주세요."
                    )
            else:
                if hasattr(tts, "speak"):
                    tts.speak(
                        "안녕하세요! 저는 치피입니다. 말씀해주세요.",
                        language="ko",
                        style="neutral",
                    )
                elif hasattr(tts, "synthesize"):
                    tts.synthesize("안녕하세요! 저는 치피입니다. 말씀해주세요.")
