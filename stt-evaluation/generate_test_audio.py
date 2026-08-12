"""
generate_test_audio.py
STT 파일럿 테스트용 합성 음성 생성 스크립트

pilot_cases.jsonl에 정의된 기대 문장을 포함하는 회의체 대화를
gTTS(Google TTS)로 합성해 audio/pilot/ 에 WAV로 저장합니다.

⚠️ 주의: 이 스크립트는 실제 회의 녹음을 아직 준비 못 했을 때
run_eval.py 파이프라인(호출 → 파싱 → 결과 저장)이 정상 동작하는지
먼저 확인하는 용도입니다.

합성 음성은 발음이 깨끗하고 화자가 1명(같은 목소리)이라
실제 STT 정확도 벤치마크로는 절대 쓰지 마세요.
파이프라인 검증이 끝나면 반드시 실제 회의 녹음으로 교체해야 합니다.

사용법:
    pip install gTTS pydub
    (ffmpeg 필요: https://ffmpeg.org/download.html 에서 설치 후 PATH 등록,
     또는 `winget install ffmpeg`)
    python generate_test_audio.py
"""

from pathlib import Path

from gtts import gTTS
from pydub import AudioSegment

OUTPUT_DIR = Path("audio/pilot")

# 각 케이스별 회의 대화 스크립트
# pilot_cases.jsonl의 기대 문장을 자연스러운 회의 흐름 안에 포함시켰습니다.
# meeting-001: "QA 빌드" 포함
# meeting-002: "로그인 오류", "내일 오전" 포함
CASES = {
    "meeting-001": """
        오늘 스프린트 회의 시작하겠습니다.
        지난주 진행 상황부터 공유해주세요.
        네, 이번 주에 QA 빌드를 새로 올렸습니다.
        테스트 서버에 배포까지 완료된 상태고요.
        QA 빌드 확인 결과는 언제쯤 받아볼 수 있을까요?
        오늘 오후까지 테스트팀에서 결과를 공유해주기로 했습니다.
        알겠습니다. 다음 안건으로 넘어가겠습니다.
    """,
    "meeting-002": """
        고객 문의사항 리뷰하겠습니다.
        어제부터 로그인 오류가 계속 접수되고 있습니다.
        로그인 오류 재현이 되시나요?
        네, 특정 브라우저에서만 재현이 됩니다.
        원인 파악은 언제까지 가능할까요?
        내일 오전까지 원인 분석을 완료하겠습니다.
        내일 오전 안에 결과 공유 부탁드립니다.
        네, 확인되는 대로 바로 보고드리겠습니다.
    """,
}


def synthesize(case_name: str, text: str) -> None:
    print(f"[{case_name}] 음성 합성 중...")
    tmp_mp3 = OUTPUT_DIR / f"{case_name}.mp3"
    out_wav = OUTPUT_DIR / f"{case_name}.wav"

    tts = gTTS(text=text.strip(), lang="ko")
    tts.save(str(tmp_mp3))

    # WAV로 변환 (16kHz, mono — STT에 권장되는 포맷)
    audio = AudioSegment.from_mp3(str(tmp_mp3))
    audio = audio.set_frame_rate(16000).set_channels(1)
    audio.export(str(out_wav), format="wav")

    tmp_mp3.unlink()  # 임시 mp3 삭제
    print(f"  → 저장 완료: {out_wav}")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for case_name, text in CASES.items():
        synthesize(case_name, text)

    print("\n모든 테스트 오디오 생성 완료.")
    print("이 오디오는 합성 음성입니다 — 파이프라인 동작 확인 후")
    print("실제 회의 녹음으로 반드시 교체하세요.")
    print("\n다음 실행:")
    print("  python run_eval.py --cases cases/pilot_cases.jsonl")


if __name__ == "__main__":
    main()