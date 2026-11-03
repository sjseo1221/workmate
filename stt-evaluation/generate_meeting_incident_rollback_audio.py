"""
generate_meeting_incident_rollback_audio.py
긴급 장애 대응 회의(길드 레이드 랭킹 포인트 마이너스 이슈, 롤백/점검) 샘플 음성 생성 스크립트

Workmate AI의 회의 분석(M3)·회의 검색(M4) 테스트용 샘플 데이터입니다.
지금까지의 정기 회의와 달리 "긴급 소집 → 원인 진단 → 해결책 → 정확한
시각이 박힌 실행 계획"으로 흘러가는 인시던트 대응 회의입니다.
"15시 30분", "16시 30분"처럼 구체적 시각이 여러 번 등장해서,
Action Item의 기한(시각) 추출 정확도를 테스트하기 특히 좋습니다.

⚠️ 등장 인물은 이름 대신 역할명(PM/서버 리드/클라이언트 리드/QA 리드)
   으로만 표기됩니다. 수치·시각은 전부 가상의 샘플 데이터입니다.

⚠️ gTTS는 단일 목소리만 지원합니다. 화자 4명의 대사를 한 목소리로
   순서대로 이어 읽습니다 — 화자 분리(diarization) 검증에는 쓸 수 없고,
   STT 인식률·회의 요약·Action Item(특히 시각) 추출 테스트에만
   사용하세요.

사용법:
    pip install gTTS pydub
    python generate_meeting_incident_rollback_audio.py
"""

from pathlib import Path

from gtts import gTTS
from pydub import AudioSegment

OUTPUT_DIR = Path("audio/samples")
OUT_NAME = "meeting-incident-rollback"

DIALOGUE = [
    ("PM", "긴급하게 모시게 된 이유는 아시다시피 방금 종료된 길드 레이드 정산에서 점수가 마이너스로 출력되는 크리티컬 이슈 때문입니다. 현재 유저 커뮤니티 민심이 최악인데, 서버 리드분 현상 파악 어디까지 되었나요?"),
    ("서버 리드", "디비 트랜잭션 처리 과정에서 동시 접속자 쏠림으로 인해 랭킹 포인트 계산 쿼리가 꼬였습니다. 데이터 유실은 없고 로그 상 정확한 원래 점수 복구는 가능한 상태입니다."),
    ("클라이언트 리드", "클라 단에서는 서버가 주는 에러 코드를 정상적으로 파싱 못 해서 로딩 화면에서 무한 멈춤 현상이 발생하고 있습니다. 클라 패치 없이 서버 데이터만 만지면 해결되는 건가요?"),
    ("서버 리드", "네, 데이터 정합성 맞추고 롤백 스크립트 돌리면 클라 패치 없이 해결됩니다. 다만 서버를 1시간 정도 내려야 합니다."),
    ("QA 리드", "롤백 대상 데이터 검증하는 데 최소 30분은 걸립니다. 서버 오픈 전에 스테이징 환경에서 샘플 계정 5개 잡고 보상 지급 상태랑 랭킹 순위 정확히 일치하는지 무조건 확인해야 합니다."),
    ("PM", "좋습니다. 지금 시각 15시니까 15시 30분부터 1시간 동안 긴급 점검 공지 올리고 서버 내립니다. QA는 점검 시작과 동시에 검증 데이터 준비해 주시고, 16시 30분 정각 오픈 목표로 달립시다."),
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
    """화자 라벨 포함 원본 대사 + Action Item(시각 포함) 정답을 별도 텍스트로 저장."""
    gt_path = OUTPUT_DIR / f"{OUT_NAME}.ground_truth.txt"
    with open(gt_path, "w", encoding="utf-8") as f:
        f.write("=== 대사 (화자 라벨 포함) ===\n")
        for speaker, line in DIALOGUE:
            f.write(f"[{speaker}] {line}\n")

        f.write("\n=== 회의 핵심 요약 ===\n")
        f.write("- 이슈: 길드 레이드 정산 랭킹 포인트가 마이너스로 표시되는 크리티컬 버그\n")
        f.write("- 원인: 동시 접속 쏠림으로 랭킹 포인트 계산 쿼리 트랜잭션 꼬임 (데이터 유실 없음)\n")
        f.write("- 부수 증상: 클라이언트가 서버 에러 코드를 못 받아 로딩 화면 무한 멈춤\n")
        f.write("- 해결책: 서버 데이터 롤백 스크립트 실행 (클라 패치 불필요)\n")

        f.write("\n=== 기대 Action Item (정답, 시각 포함) ===\n")
        f.write("1. 담당자: PM / 내용: 긴급 점검 공지 게시 / 시각: 15시\n")
        f.write("2. 담당자: 서버 리드 / 내용: 서버 다운 및 롤백 스크립트 실행 / 시각: 15시 30분 ~ 16시 30분 (1시간)\n")
        f.write("3. 담당자: QA 리드 / 내용: 스테이징 환경에서 샘플 계정 5개 보상·랭킹 정합성 검증 "
                 "/ 시각: 점검 시작(15시 30분)과 동시에 착수, 최소 30분 소요\n")
        f.write("4. 담당자: 전체 / 내용: 서버 재오픈 / 시각: 16시 30분 정각 목표\n")

        f.write("\n=== 참고 — 이 샘플의 특징 ===\n")
        f.write("정기 회의가 아닌 '긴급 소집형' 인시던트 대응 회의입니다.\n")
        f.write("절대 시각(15시, 15시 30분, 16시 30분)이 여러 번 등장하므로,\n")
        f.write("Action Item의 기한을 상대 표현('다음 주 월요일')이 아니라\n")
        f.write("절대 시각으로 정확히 추출하는지 확인하는 용도로 특히 유용합니다.\n")
    print(f"✅ 정답 텍스트(화자 라벨 + Action Item + 요약) 저장: {gt_path}")
    return gt_path


def main():
    print("긴급 장애 대응 회의 샘플 생성 시작\n")
    wav_path = synthesize()
    gt_path = save_ground_truth()

    print("\n이 샘플의 특징:")
    print("  - 긴급 소집형 인시던트 대응 회의 (정기 회의와 다른 어조·속도감)")
    print("  - 절대 시각(15:00, 15:30, 16:30)이 다수 등장 — 시각 기반 Action Item 추출 테스트에 적합")
    print("  - 4개 부서(PM/서버/클라이언트/QA)가 각자 역할별 Action Item을 가짐")
    print(f"\n생성된 파일:\n  오디오: {wav_path}\n  정답 텍스트: {gt_path}")
    print("\n주의: 단일 목소리 합성이라 화자 분리 테스트에는 쓸 수 없습니다.")


if __name__ == "__main__":
    main()
