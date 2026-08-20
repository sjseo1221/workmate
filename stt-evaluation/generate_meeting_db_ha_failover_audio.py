"""
generate_meeting_db_ha_failover_audio.py
백엔드/인프라 팀 회의(DB 스케일아웃, Read Replica, Failover 자동화) 샘플 음성 생성 스크립트

Workmate AI의 회의 분석(M3)·회의 검색(M4) 테스트용 샘플 데이터입니다.
이번 회의는 숫자로 된 절차(헬스체크 3초, 복구 12초 등)와 담당자별
Action Item이 명확히 구분되어 있어서, Action Item 추출(M3.4~M3.5)
테스트에 특히 유용합니다.

⚠️ 등장하는 인물명(서선정/박민우/강태성), 수치(12초 복구 등)는
   전부 가상의 샘플 데이터입니다.

⚠️ gTTS는 단일 목소리만 지원합니다. 화자 3명의 대사를 한 목소리로
   순서대로 이어 읽습니다 — 화자 분리(diarization) 검증에는 쓸 수 없고,
   STT 인식률·회의 요약·Action Item 추출 테스트에만 사용하세요.

사용법:
    pip install gTTS pydub
    python generate_meeting_db_ha_failover_audio.py
"""

from pathlib import Path

from gtts import gTTS
from pydub import AudioSegment

OUTPUT_DIR = Path("audio/samples")
OUT_NAME = "meeting-db-ha-failover"

# 화자별 대사. 영문 약어/기호 표기는 gTTS가 자연스럽게 발음하도록
# 한글 음차로 풀어서 넣었습니다 (예: Failover -> 페일오버).
DIALOGUE = [
    ("서선정", "안녕하세요. 오늘 미팅은 다음 주 CBT를 앞두고 진행한 DB 스케일아웃 및 장애 복구 자동화 검증 결과를 공유드리고, 인프라 단과의 최종 연동 체크를 위해 요청드렸습니다."),
    ("박민우", "네, 선정 님. CBT 때 접속자가 한꺼번에 몰릴 텐데, DB 읽기 트래픽 분산 처리는 어떻게 구성을 완료하셨나요?"),
    ("서선정", "기존 싱글 프라이머리 구조에서 리드 레플리카, 읽기 전용 복제본 2대를 추가 구성했습니다. 트래픽의 70퍼센트 이상을 차지하는 캐릭터 상태 조회나 인벤토리 확인 같은 단순 리드 쿼리는 레플리카로 분산되도록 엔드포인트를 분리했습니다."),
    ("강태성", "레플리카 추가로 읽기 성능은 올라가겠네요. 그런데 애플리케이션 쪽 커넥션 풀 설정은 어떻게 재조정하셨나요? 복제본 늘어나면서 디비 커넥션 과부하가 생길 수 있거든요."),
    ("서선정",
     "네, 태성 님. 기존엔 프라이머리에만 커넥션이 집중돼서 맥스 커넥션에 간당간당했는데요. "
     "이번에 리드, 라이트 데이터소스를 완전히 분리했습니다. "
     "프라이머리, 쓰기 쪽은 맥시멈 풀 사이즈 30으로 설정해서 트랜잭션 점유 시간을 최적화했고, "
     "레플리카, 읽기 쪽은 각 인스턴스당 풀 사이즈 50으로 설정한 다음 라운드 로빈 방식으로 부하 분산했습니다. "
     "테스트 결과, 동시 접속자 수천 명 수준에서도 디비 커넥션 고갈 없이 안정적으로 유지되는 것을 확인했습니다."),
    ("박민우", "좋습니다. 만약에 라이브 중 프라이머리 디비가 다운되면 장애 복구, 페일오버는 어떻게 진행되나요?"),
    ("서선정",
     "그 부분 때문에 지난주에 자동 장애 복구 스크립트 검증을 진행했습니다. "
     "오케스트레이터와 브이아이피, 버추얼 아이피 스위칭 기반으로 스크립트를 짜두었는데요. "
     "프라이머리 강제 셧다운 테스트 시, 첫째 프라이머리 헬스체크 실패 감지에 3초가 걸리고, "
     "둘째 복제 지연, 리플리케이션 랙이 가장 적은 레플리카 1번을 새로운 프라이머리로 승격하고, "
     "셋째 브이아이피 재할당 및 애플리케이션 트래픽을 자동 전환합니다. "
     "전체 과정에서 서비스 중단 시간, 다운타임 약 12초 이내로 복구가 완료되는 것을 최종 검증했습니다."),
    ("강태성", "12초면 앱 재접속이나 타임아웃 재시도 로직으로 충분히 커버 가능한 수준이네요. 모니터링 알림 연동, 슬랙이랑 페이저듀티도 스크립트에 포함되어 있죠?"),
    ("서선정", "네, 장애 감지 시점과 승격 완료 시점에 즉시 인프라팀과 서버팀 채널로 알림이 발송되도록 웹훅 걸어두었습니다."),
    ("박민우", "수고 많으셨습니다. 스케일아웃이랑 에이치에이 구성까지 마무리됐으니 디비 쪽 CBT 준비는 거의 끝난 것 같네요."),
    ("서선정",
     "네, 그럼 잔여 항목 정리해서 공유드리겠습니다. "
     "첫째, 선정 님, 그러니까 제가 페일오버 매뉴얼 및 비상 연락망을 문서화해서 백엔드, 인프라팀에 공유하겠습니다. "
     "둘째, 태성 님은 CBT 오픈 당일 리드 레플리카 리소스, 씨피유와 아이오 모니터링 대시보드를 고정 배치해 주시면 됩니다. "
     "이상으로 미팅 마치겠습니다. 감사합니다!"),
]


def synthesize() -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    tmp_mp3 = OUTPUT_DIR / f"{OUT_NAME}.mp3"
    out_wav = OUTPUT_DIR / f"{OUT_NAME}.wav"

    full_text = " ".join(line for _, line in DIALOGUE)

    print("음성 합성 중...")
    tts = gTTS(text=full_text, lang="ko")
    tts.save(str(tmp_mp3))

    print("WAV로 변환 중 (16kHz, mono)...")
    audio = AudioSegment.from_mp3(str(tmp_mp3))
    audio = audio.set_frame_rate(16000).set_channels(1)
    audio.export(str(out_wav), format="wav")

    tmp_mp3.unlink()
    print(f"✅ 저장 완료: {out_wav}")
    return out_wav


def save_ground_truth() -> Path:
    """화자 라벨 포함 원본 대사 + Action Item 정답을 별도 텍스트로 저장."""
    gt_path = OUTPUT_DIR / f"{OUT_NAME}.ground_truth.txt"
    with open(gt_path, "w", encoding="utf-8") as f:
        f.write("=== 대사 (화자 라벨 포함) ===\n")
        for speaker, line in DIALOGUE:
            f.write(f"[{speaker}] {line}\n")

        f.write("\n=== 기대 Action Item (정답) ===\n")
        f.write("1. 담당자: 서선정 / 내용: Failover 매뉴얼 및 비상 연락망 문서화, 백엔드·인프라팀 공유\n")
        f.write("2. 담당자: 강태성 / 내용: CBT 오픈 당일 Read Replica 리소스(CPU/I/O) 모니터링 대시보드 고정 배치\n")
    print(f"✅ 정답 텍스트(화자 라벨 + Action Item) 저장: {gt_path}")
    return gt_path


def main():
    print("DB 스케일아웃/장애복구(HA) 회의 샘플 생성 시작\n")
    wav_path = synthesize()
    gt_path = save_ground_truth()

    print("\n포함된 기술 용어 (STT 인식률 확인용):")
    print("  Read Replica, Connection Pool, Max Connection, Round-Robin,")
    print("  Failover, VIP, Replication Lag, Downtime, Webhook")
    print("\n포함된 Action Item (추출 정확도 확인용):")
    print("  - 서선정: Failover 매뉴얼·비상 연락망 문서화")
    print("  - 강태성: CBT 당일 모니터링 대시보드 고정 배치")
    print(f"\n생성된 파일:\n  오디오: {wav_path}\n  정답 텍스트: {gt_path}")
    print("\n주의: 단일 목소리 합성이라 화자 분리 테스트에는 쓸 수 없습니다.")


if __name__ == "__main__":
    main()
