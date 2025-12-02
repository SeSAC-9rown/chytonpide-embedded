#!/usr/bin/env python3
"""
TTS 파일 생성 유틸리티

텍스트를 TTS로 변환하여 wav 파일로 저장합니다.
"""

import json
import sys
from pathlib import Path

# 상위 디렉토리를 sys.path에 추가
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

# .env 파일 경로 찾기 및 로드 (다른 파일들과 동일하게)
try:
    from dotenv import load_dotenv

    # config/.env 파일 경로 찾기
    config_path = parent_dir / "config" / ".env"
    if config_path.exists():
        load_dotenv(config_path)
    else:
        # 상위 디렉토리에서도 찾기
        parent_config = parent_dir.parent / "config" / ".env"
        if parent_config.exists():
            load_dotenv(parent_config)
        else:
            # 기본 경로
            load_dotenv()
except ImportError:
    print(
        "경고: python-dotenv가 설치되지 않았습니다. .env 파일이 로드되지 않을 수 있습니다."
    )
except Exception as e:
    print(f"경고: .env 파일 로드 중 오류: {e}")

# SuperTone TTS import
try:
    # 1. tts 패키지에서 import 시도
    from tts.superton_tts import SupertonTTS
except ImportError:
    try:
        # 2. 상대 경로로 시도
        import importlib.util

        tts_file_path = parent_dir / "tts" / "superton_tts.py"
        if tts_file_path.exists():
            spec = importlib.util.spec_from_file_location("superton_tts", tts_file_path)
            tts_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(tts_module)
            SupertonTTS = tts_module.SupertonTTS
        else:
            raise ImportError(
                f"tts/superton_tts.py를 찾을 수 없습니다: {tts_file_path}"
            )
    except Exception as e:
        print(f"❌ SupertonTTS를 import할 수 없습니다: {e}")
        print(f"   현재 디렉토리: {current_dir}")
        print(f"   상위 디렉토리: {parent_dir}")
        sys.exit(1)


# ============================================================================
# TTS 파라미터 설정 (현재 코드와 동일하게)
# ============================================================================

# 기본 파라미터 (일반 대화)
DEFAULT_PARAMS = {
    "language": "ko",
    "style": "neutral",
    "pitch_shift": 0,
    "speed": 1,
    "pitch_variance": 1,
}

# 슬픈 톤 파라미터
SAD_PARAMS = {
    "language": "ko",
    "style": "sad",
    "pitch_shift": -10,
    "speed": 1,
    "pitch_variance": 1,
}


# ============================================================================
# TTS 파일 생성 함수
# ============================================================================


def generate_tts_file(text, output_dir=None, filename=None, params=None):
    """텍스트를 TTS로 변환하여 wav 파일로 저장

    Args:
        text: 변환할 텍스트
        output_dir: 출력 디렉토리 (None이면 utils/audio 사용)
        filename: 파일명 (None이면 텍스트의 첫 20자를 사용)
        params: TTS 파라미터 (None이면 DEFAULT_PARAMS 사용)

    Returns:
        저장된 파일 경로 또는 None
    """
    if params is None:
        params = DEFAULT_PARAMS

    # 출력 디렉토리 설정 (기본값: utils/audio)
    if output_dir is None:
        output_dir = current_dir / "audio"
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # 파일명 생성
    if filename is None:
        # 텍스트에서 안전한 파일명 생성
        # 규칙: 텍스트의 첫 20자를 사용, 안전하지 않은 문자(한글, 특수문자 등)는 언더스코어로 변환
        # 영문자, 숫자, 공백, 하이픈, 언더스코어만 유지
        safe_text = "".join(
            c if c.isalnum() or c in (" ", "-", "_") else "_" for c in text[:20]
        ).strip()
        # 공백을 언더스코어로 변환하고, 연속된 언더스코어 정리
        safe_text = "_".join(safe_text.split())
        if not safe_text:  # 빈 문자열이면 기본값 사용
            safe_text = "output"
        filename = f"{safe_text}.wav"
    elif not filename.endswith(".wav"):
        filename = f"{filename}.wav"

    filepath = output_path / filename

    # TTS 생성
    try:
        tts = SupertonTTS()
        print(f"📝 텍스트: {text}")
        print("🎤 TTS 생성 중...", end=" ", flush=True)

        audio_data = tts.generate(
            text=text,
            language=params["language"],
            style=params["style"],
            output_format="wav",
            pitch_shift=params["pitch_shift"],
            speed=params["speed"],
            pitch_variance=params["pitch_variance"],
        )

        if audio_data:
            # 파일 저장
            with open(filepath, "wb") as f:
                f.write(audio_data)

            file_size = filepath.stat().st_size / 1024  # KB
            print(f"✅ 완료 ({file_size:.1f} KB)")
            print(f"💾 저장됨: {filepath}\n")
            return str(filepath)
        else:
            print("❌ 실패 (TTS 생성 실패)")
            return None

    except Exception as e:
        print(f"❌ 오류: {e}")
        import traceback

        traceback.print_exc()
        return None


def load_answers_from_json(json_path):
    """JSON 파일에서 답변 리스트 로드

    Args:
        json_path: JSON 파일 경로 (Path 또는 str)

    Returns:
        답변 문자열 리스트

    Raises:
        FileNotFoundError: 파일을 찾을 수 없을 때
        json.JSONDecodeError: JSON 파싱 오류
    """
    json_path = Path(json_path)

    if not json_path.exists():
        raise FileNotFoundError(f"JSON 파일을 찾을 수 없습니다: {json_path}")

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # JSON 형식: 배열 또는 {"answers": [...]}
    if isinstance(data, list):
        answers = data
    elif isinstance(data, dict) and "answers" in data:
        answers = data["answers"]
    else:
        raise ValueError(
            "잘못된 JSON 형식입니다. 배열 또는 {'answers': [...]} 형식이어야 합니다."
        )

    # 문자열 리스트로 변환
    result = []
    for item in answers:
        if isinstance(item, str):
            result.append(item)
        elif isinstance(item, dict) and "text" in item:
            result.append(item["text"])
        else:
            print(f"⚠️  항목을 건너뜁니다: {item}")

    return result


def generate_from_list(answers, output_dir=None):
    """답변 목록을 TTS 파일로 변환

    Args:
        answers: 답변 문자열 리스트
        output_dir: 출력 디렉토리 (None이면 utils/audio 사용)

    Returns:
        생성된 파일 경로 리스트
    """
    if output_dir is None:
        output_dir = current_dir / "audio"
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    generated_files = []

    print("🎬 TTS 파일 생성 시작...\n")
    print(f"📁 출력 디렉토리: {output_path.absolute()}\n")

    for i, answer in enumerate(answers, 1):
        if not isinstance(answer, str):
            print(f"⚠️  항목 {i}: 문자열이 아니어서 건너뜀")
            continue

        print(f"[{i}/{len(answers)}] 처리 중...")

        # TTS 파일 생성
        filename = f"a_{i:02d}.wav"
        # 답변에 슬픈 키워드가 있으면 슬픈 톤 사용
        sad_keywords = ["힘들", "슬프", "아픔", "우울", "죽고", "절망"]
        a_params = None
        if any(keyword in answer for keyword in sad_keywords):
            a_params = SAD_PARAMS
            print("   📌 슬픈 톤으로 변경")

        filepath = generate_tts_file(
            answer, output_dir=output_dir, filename=filename, params=a_params
        )
        if filepath:
            generated_files.append(filepath)

        print()

    print(f"✅ 총 {len(generated_files)}개 파일 생성 완료!\n")
    return generated_files


# ============================================================================
# 메인 함수
# ============================================================================


def main():
    """메인 함수"""
    import argparse

    parser = argparse.ArgumentParser(description="TTS 파일 생성")
    parser.add_argument(
        "--text",
        type=str,
        help="단일 텍스트를 TTS로 변환",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="출력 디렉토리 (기본값: utils/audio)",
    )
    parser.add_argument(
        "--filename",
        type=str,
        help="단일 파일일 때 사용할 파일명",
    )
    parser.add_argument(
        "--file",
        type=str,
        help="JSON 파일에서 답변 리스트를 읽어 모두 TTS로 변환",
    )

    args = parser.parse_args()

    # 단일 텍스트 변환
    if args.text:
        generate_tts_file(args.text, output_dir=args.output, filename=args.filename)
        return

    # JSON 파일에서 답변 리스트 읽어서 변환
    if args.file:
        try:
            json_path = Path(args.file)
            # 상대 경로인 경우 utils 디렉토리 기준으로 확인
            if not json_path.is_absolute():
                # 현재 디렉토리에서 찾기
                if not json_path.exists():
                    # utils 디렉토리에서 찾기
                    json_path = current_dir / json_path
                    if not json_path.exists():
                        # 상위 디렉토리에서도 찾기
                        json_path = parent_dir / args.file
            answers = load_answers_from_json(json_path)
            print(f"📄 JSON 파일에서 {len(answers)}개의 답변을 로드했습니다.\n")
            generate_from_list(answers, output_dir=args.output)
        except FileNotFoundError as e:
            print(f"❌ 오류: {e}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"❌ JSON 파싱 오류: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"❌ 오류: {e}")
            import traceback

            traceback.print_exc()
            sys.exit(1)
        return

    # 인터랙티브 모드
    print("=== TTS 파일 생성 유틸리티 ===\n")
    print("사용법:")
    print("  1. 단일 텍스트 변환: --text '텍스트'")
    print("  2. JSON 파일에서 변환: --file input.json")
    print("  3. 인터랙티브 모드: (현재 모드)\n")

    output_dir_input = input(
        "출력 디렉토리 (기본값: utils/audio, 엔터: 기본값): "
    ).strip()
    output_dir = output_dir_input if output_dir_input else None

    while True:
        print("\n" + "=" * 50)
        text = input("변환할 텍스트 입력 (종료: quit): ").strip()

        if text.lower() in ["quit", "exit", "q"]:
            break

        if not text:
            continue

        # 슬픈 키워드 확인
        sad_keywords = ["힘들", "슬프", "아픔", "우울", "죽고", "절망"]
        use_sad = any(keyword in text for keyword in sad_keywords)

        params = SAD_PARAMS if use_sad else DEFAULT_PARAMS
        if use_sad:
            print("📌 슬픈 톤으로 생성합니다.")

        filename = input("파일명 (엔터: 자동 생성): ").strip() or None

        generate_tts_file(text, output_dir=output_dir, filename=filename, params=params)


if __name__ == "__main__":
    main()
