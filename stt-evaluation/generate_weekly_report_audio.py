"""
generate_weekly_report_audio.py
게임개발 회사 주간 업무보고 샘플 음성 생성 스크립트

Workmate AI의 "주간 보고서" Skill(M2) 테스트/데모용 샘플 데이터입니다.
가상의 게임개발 회사 클라이언트 개발자가 본인 업무를 구두로 보고하는
상황을 가정한 대본을 gTTS로 합성해 WAV로 저장합니다.

⚠️ 등장하는 인물명, 프로젝트명, 스프린트 번호, 버그 ID 등은 전부 가상의
   샘플 데이터이며 실제 회사/인물과 무관합니다.

사용법:
    pip install gTTS pydub
    (ffmpeg 필요: winget install ffmpeg 후 새 터미널)
    python generate_weekly_report_audio.py
"""

from pathlib import Path

from gtts import gTTS
from pydub import AudioSegment

OUTPUT_DIR = Path("audio/samples")

# 게임개발 회사 클라이언트 개발자의 주간 업무보고 대본
# - 완료: 이번 주에 끝낸 작업
# - 진행중: 아직 진행 중인 작업
# - 이슈: 막힌 부분/버그
# - 다음주 계획: 다음 주 예정 작업
# Workmate AI의 "완료/진행/지연/이슈/다음 주 계획" 분류 로직 테스트에
# 맞춰 각 카테고리가 자연스러운 구어체로 섞여 있습니다.
WEEKLY_REPORT_SCRIPT = """
안녕하세요, 이번 주 업무보고 드리겠습니다.

먼저 완료된 작업부터 말씀드리면, 캐릭터 인벤토리 UI 리팩토링을 이번 주에 마무리했습니다.
기존에 아이템 슬롯이 60개 이상일 때 프레임 드랍이 있었는데,
오브젝트 풀링 적용해서 해결했고, 어제 QA 빌드에 반영했습니다.

그리고 지난주에 이슈였던 로그인 오류 건도 원인을 찾아서 수정했습니다.
특정 브라우저에서 토큰 갱신 타이밍이 꼬이는 문제였고,
재현 케이스 다섯 개 전부 확인 완료했습니다.

진행 중인 작업으로는, 길드 시스템 서버 API 작업이 한 70퍼센트 정도 진행됐습니다.
길드 가입, 탈퇴, 권한 관리까지는 끝났고, 길드 창고 기능이 아직 남아있습니다.
이 부분은 기획팀이랑 창고 슬롯 개수를 다시 협의해야 해서, 오늘 오후에 미팅 잡혀 있습니다.

이슈 사항으로는, 신규 던전 콘텐츠에서 몬스터 스폰이 간헐적으로 두 배로 뜨는 버그가 있는데,
아직 재현 조건을 완전히 못 잡았습니다. 로그 분석은 계속하고 있고,
서버팀 도움 받아서 다음 주 초까지는 원인 파악할 예정입니다.

그리고 결제 모듈 최적화 작업은 우선순위가 밀려서 이번 주는 손을 못 댔습니다.
다음 스프린트로 이월하는 게 맞을 것 같습니다.

다음 주 계획 말씀드리면, 길드 창고 기능 마무리하고,
몬스터 스폰 버그 픽스하고, QA팀이랑 같이 회귀 테스트 진행할 예정입니다.
그리고 목요일에 신규 시즌 콘텐츠 기획 리뷰 미팅이 잡혀 있어서 그것도 준비하겠습니다.

이상입니다. 질문 있으시면 말씀해 주세요.
"""


def synthesize(text: str, out_name: str = "weekly-report-sample") -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    tmp_mp3 = OUTPUT_DIR / f"{out_name}.mp3"
    out_wav = OUTPUT_DIR / f"{out_name}.wav"

    print("음성 합성 중...")
    tts = gTTS(text=text.strip(), lang="ko")
    tts.save(str(tmp_mp3))

    print("WAV로 변환 중 (16kHz, mono)...")
    audio = AudioSegment.from_mp3(str(tmp_mp3))
    audio = audio.set_frame_rate(16000).set_channels(1)
    audio.export(str(out_wav), format="wav")

    tmp_mp3.unlink()
    print(f"✅ 저장 완료: {out_wav}")
    return out_wav


def main():
    out_path = synthesize(WEEKLY_REPORT_SCRIPT)
    print("\n이 음성은 게임개발 회사 주간 업무보고 샘플 데이터입니다.")
    print("등장하는 인물/프로젝트/버그 ID는 전부 가상입니다.")
    print(f"\n생성된 파일: {out_path}")
    print("STT/회의 분석 파이프라인 테스트에 바로 사용하실 수 있습니다.")


if __name__ == "__main__":
    main()
