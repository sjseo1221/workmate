"""
generate_meeting_db_schema_audio.py
백엔드/DB 팀 회의(캐릭터 DB 스키마, 로그 테이블 파티셔닝) 샘플 음성 생성 스크립트

Workmate AI의 회의 분석(M3)·회의 검색(M4) 테스트용 샘플 데이터입니다.
기술 용어(Covering Index, Range Partitioning, DDL, DROP PARTITION,
Partition Pruning 등)가 많이 등장해서 STT 도메인 인식률 테스트에도
유용합니다.

⚠️ 등장하는 인물명(서선정/박민우/김도현), 수치(25% 개선 등)는
   전부 가상의 샘플 데이터입니다.

⚠️ gTTS는 단일 목소리만 지원합니다. 이 스크립트는 화자 3명의 대사를
   한 목소리로 순서대로 이어 읽습니다 — 실제 화자 분리(diarization)
   검증에는 쓸 수 없고, STT 인식률·회의 내용/Action Item 추출
   테스트에만 사용하세요.

사용법:
    pip install gTTS pydub
    python generate_meeting_db_schema_audio.py
"""

from pathlib import Path

from gtts import gTTS
from pydub import AudioSegment

OUTPUT_DIR = Path("audio/samples")
OUT_NAME = "meeting-db-schema-partitioning"

# 화자별 대사를 (화자, 대사) 튜플로 유지 — 나중에 화자 라벨이 필요하면
# 이 구조를 그대로 diarization 정답(ground truth)으로도 재사용 가능합니다.
DIALOGUE = [
    ("서선정", "안녕하세요, 다들 모여주셔서 감사합니다. 오늘 미팅에서는 이번 주 진행한 캐릭터 DB 스키마 작업 결과 공유랑, 다음 주 CBT 대비해서 로그 테이블 파티셔닝 구조 최종 확정짓으려고 합니다."),
    ("박민우", "네, 선정 님. 인벤토리 쪽 인덱싱 작업 끝나고 성능 테스트 돌려보셨다고 들었는데, 결과가 어떻게 나왔나요?"),
    ("서선정", "네, 기존 인벤토리랑 장비 테이블의 커버링 인덱스 재구성 작업을 진행했습니다. 인게임 유저가 늘어나면서 장비 교체나 인벤토리 전체 조회 시 아이오 병목이 좀 있었는데요, 튜닝 이후 복합 인덱스 순서를 유저 아이디, 아이템 타입, 슬롯 인덱스 구조로 재배치했습니다. 결과적으로 주요 조회 쿼리 레이턴시가 기존 대비 약 25퍼센트 개선됐습니다."),
    ("김도현", "클라이언트 입장에서도 인벤토리 창 열 때 프레임 드랍이나 딜레이 느껴지던 게 확 줄겠네요. 아주 좋습니다."),
    ("서선정", "고맙습니다. 그리고 두 번째 안건인 아이템 획득 소비 로그 테이블 파티셔닝 건인데요. CBT 오픈하면 하루에도 수천만 건 이상 로그가 쌓일 것으로 예상돼서, 월별 레인지 파티셔닝이 아닌 일별 파티셔닝으로 생성해 두었습니다."),
    ("박민우", "일별 파티셔닝이면 데이터가 너무 자잘하게 쪼개져서 관리 포인트가 늘어나지 않나요? 주 단위나 월 단위는 고려 안 해보셨나요?"),
    ("서선정", "월 단위로 가면 특정 이벤트 기간에 데이터가 급증했을 때 테이블 스캔 부담이 커집니다. 일별로 나누면 야간 배치 작업 시 한 달이 지난 옛날 로그 데이터 보관 기간이 만료되었을 때, 드롭 파티션 명령어로 디디엘 락 없이 1초 만에 깔끔하게 삭제할 수 있어서 운영 부담이 훨씬 적습니다."),
    ("김도현", "로그 조회 쿼리 날릴 때 조건절에 크리에이티드 앳 일자 조건 필수로 넣어야 파티셔닝 프루닝 이점이 살아나겠네요? 운영툴 개발팀에도 전달해야겠어요."),
    ("서선정", "맞습니다. 도현 님 말씀대로 날짜 검색 조건이 빠지면 전체 파티션을 다 뒤지게 되니까, 운영툴 API 쿼리 작성 시 크리에이티드 앳 범위를 반드시 세팅하도록 가이드 문서 작성해서 공유드리겠습니다."),
]


def synthesize() -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    tmp_mp3 = OUTPUT_DIR / f"{OUT_NAME}.mp3"
    out_wav = OUTPUT_DIR / f"{OUT_NAME}.wav"

    # 화자 표시 없이 대사만 이어붙여서 하나의 자연스러운 회의 음성으로 합성
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


def save_ground_truth():
    """화자 라벨이 붙은 원본 대사를 별도 텍스트 파일로 저장 (STT 정확도 채점용)."""
    gt_path = OUTPUT_DIR / f"{OUT_NAME}.ground_truth.txt"
    with open(gt_path, "w", encoding="utf-8") as f:
        for speaker, line in DIALOGUE:
            f.write(f"[{speaker}] {line}\n")
    print(f"✅ 정답 텍스트(화자 라벨 포함) 저장: {gt_path}")
    return gt_path


def main():
    print("DB 스키마/파티셔닝 회의 샘플 생성 시작\n")
    wav_path = synthesize()
    gt_path = save_ground_truth()

    print("\n포함된 기술 용어 (STT 인식률 확인용):")
    print("  Covering Index, Range Partitioning, I/O 병목, latency,")
    print("  DROP PARTITION, DDL, Partition Pruning, created_at")
    print(f"\n생성된 파일:\n  오디오: {wav_path}\n  정답 텍스트: {gt_path}")
    print("\n주의: 단일 목소리 합성이라 화자 분리 테스트에는 쓸 수 없습니다.")
    print("      STT 내용 인식률 / Action Item 추출 / 회의 검색 테스트에 사용하세요.")


if __name__ == "__main__":
    main()
