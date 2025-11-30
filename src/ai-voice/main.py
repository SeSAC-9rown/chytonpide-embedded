import os
import sys
import io

# 한글 출력 깨짐 방지 (Python 3.7.3 호환)
# sys.stdout.reconfigure는 Python 3.7+에서 지원되지만, 더 안전한 방법 사용
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except (AttributeError, ValueError):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
else:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 경로 설정 (servo 패키지처럼)
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from dotenv import load_dotenv

# 상대 경로로 import 시도
try:
    from core.chipi_brain import ChipiBrain
    from tts.tts_engine import AzureTTS
except ImportError:
    # 절대 경로로 시도
    try:
        from src.core.chipi_brain import ChipiBrain
        from src.tts.tts_engine import AzureTTS
    except ImportError:
        # 직접 import 시도 (같은 디렉토리)
        from chipi_brain import ChipiBrain
        from tts_engine import AzureTTS

def main():
    load_dotenv()
    
    device_serial = os.environ.get("DEVICE_SERIAL")
    if not device_serial:
        print("⚠️ DEVICE_SERIAL 없음")

    print("\n============== ⚡ 치피(Chipi) 고속 모드 시작 ==============")
    
    try:
        print("🧠 두뇌(LLM) 연결 중...", end=" ", flush=True)
        brain = ChipiBrain()
        print("✅ 완료")

        print("👄 입/귀(TTS) 연결 중...", end=" ", flush=True)
        tts = AzureTTS()
        print("✅ 완료")
        
        chipi_params = {
            "voice": "ko-KR-SeoHyeonNeural",
            "style": "cheerful",
            "style_degree": 2.0,
            "pitch": 15,  
            "rate": 30
        }

        tts.speak("준비됐어! 말 걸어줘!", chipi_params)

        while True:
            # 1. 듣기
            user_text = tts.listen()
            
            if not user_text:
                continue 

            # 종료 체크
            if any(word in user_text for word in ["종료", "그만", "꺼져"]):
                tts.speak("안녕!", chipi_params)
                break

            # 2. 생각하기
            print("🧠 생각하는 중...", end=" ", flush=True)
            brain.add_msg(user_text)
            ai_response = brain.wait_run(ai_name='chipi', device_serial=device_serial)
            print("✅ 완료", flush=True)
            
            if not ai_response:
                tts.speak("미안, 다시 말해줄래?", chipi_params)
                continue

            # 3. 말하기
            # print(f"🤖 답변: {ai_response}") # 로그 너무 길면 주석 처리
            tts.speak(ai_response, chipi_params)

    except Exception as e:
        print(f"\n❌ 오류: {e}")
        import traceback
        traceback.print_exc()
        input("종료하려면 엔터...")

if __name__ == "__main__":
    main()