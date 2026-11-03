"""
generate_meeting_schedule_scope_cut_audio.py
경영진 소집 회의(CBT 일정 지연 원인 점검, 스코프 축소 결정) 샘플 음성 생성 스크립트

Workmate AI의 회의 분석(M3)·회의 검색(M4) 테스트용 샘플 데이터입니다.
지금까지의 회의들과 달리 최상위 의사결정자(제작이사)가 실무진 두 파트
(전투 기획 vs 클라이언트)의 갈등을 듣고 **하향식으로 강하게 결론을
내리는** 구조입니다. 특히 마지막 발화에 지시가 두 개(기획팀 지시,
PM 지시) 겹쳐 있어서, 한 화자의 한 발화 안에 서로 다른 담당자에게
가는 Action Item을 정확히 분리해내는지 테스트하기 좋습니다.

⚠️ 등장 인물은 역할명(제작이사/PM/전투 기획 파트장/클라이언트 팀장)
   으로 표기됩니다. 등장하는 상황은 전부 가상의 샘플 데이터입니다.

⚠️ gTTS는 단일 목소리만 지원합니다. 화자 4명의 대사를 한 목소리로
   순서대로 이어 읽습니다 — 화자 분리(diarization) 검증에는 쓸 수 없고,
   STT 인식률·회의 요약·Action Item 분리 추출 테스트에만 사용하세요.

사용법:
    pip install gTTS pydub
    python generate_meeting_schedule_scope_cut_audio.py
"""

from pathlib import Path

from gtts import gTTS
from pydub import AudioSegment

OUTPUT_DIR = Path("audio/samples")
OUT_NAME = "meeting-schedule-scope-cut"

DIALOGUE = [
    ("제작이사", "연말 CBT 일정 못 맞추면 내년 상반기 투자 심사 다 날아갑니다. 지금 전투 파트에서 타격감 개선 작업 때문에 일정이 밀린다는 소리가 들리는데 현 상황 정확히 짚어봅시다. PM, 일정 어디가 구멍 났나요?"),
    ("PM", "전투 기획 파트에서 신규 캐릭터 콤보 시스템의 연계 동작 스펙을 계속 수정하면서 클라이언트 구현이 2주 이상 밀렸습니다. 이대로 가면 CBT 빌드 통합 작업을 할 시간이 안 나옵니다."),
    ("전투 기획 파트장", "액션 게임 생명은 타격감인데, 지금 프레임 단위로 판정을 안 잡으면 유저들이 모션이 뻣뻣하다고 바로 욕합니다. 퀄리티 포기 못 합니다."),
    ("클라이언트 팀장", "기획서가 매번 바뀌니까 코드를 엎는 게 더 문제예요. 완벽한 콤보 시스템을 만들려다가 게임 전체가 터지게 생겼습니다. 이번 CBT 때는 복잡한 연계기는 빼고 기본 공격 3타랑 궁극기만 확실하게 다듬는 마이너스 스코프, 기능 축소 전략으로 가야 합니다."),
    ("제작이사", "팀장 말 맞습니다. 완벽주의 버리세요. CBT는 핵심 루프가 잘 돌아가는지 검증하는 게 목적이지 완성품을 내는 자리가 아닙니다. 기획은 당장 이번 주까지 구현 가능한 스펙만 남기고 전부 나이스 투 해브, 추후 개발로 내리세요. PM은 남은 기능 기준으로 다시 간트차트 짜서 보고하세요."),
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
    """화자 라벨 포함 원본 대사 + 분리된 Action Item 정답을 별도 텍스트로 저장."""
    gt_path = OUTPUT_DIR / f"{OUT_NAME}.ground_truth.txt"
    with open(gt_path, "w", encoding="utf-8") as f:
        f.write("=== 대사 (화자 라벨 포함) ===\n")
        for speaker, line in DIALOGUE:
            f.write(f"[{speaker}] {line}\n")

        f.write("\n=== 회의 핵심 요약 ===\n")
        f.write("- 문제: 전투 기획의 콤보 시스템 스펙 반복 수정으로 클라이언트 구현 2주 이상 지연,\n")
        f.write("  CBT 빌드 통합 일정에 차질\n")
        f.write("- 대립: 전투 기획 파트장(타격감 퀄리티 우선) vs 클라이언트 팀장(스코프 축소 필요)\n")
        f.write("- 결정(제작이사): 클라이언트 팀장 안 채택, 스코프 축소로 진행\n")

        f.write("\n=== 기대 Action Item (정답) — 한 발화 안에 담당자가 다른 지시 2개 ===\n")
        f.write("1. 담당자: 전투 기획 파트(파트장) / 내용: 이번 주까지 구현 가능한 스펙만 남기고 "
                 "나머지는 'Nice-to-have(추후 개발)'로 하향 조정 / 기한: 이번 주\n")
        f.write("2. 담당자: PM / 내용: 축소된 스펙 기준으로 간트차트 재작성 후 보고 / 기한: 명시 안 됨\n")

        f.write("\n=== 참고 — 이 샘플의 특징 ===\n")
        f.write("제작이사의 마지막 한 발화 안에 서로 다른 담당자(기획팀, PM)에게\n")
        f.write("가는 지시가 연달아 들어 있습니다. Action Item 추출이 이걸 하나로\n")
        f.write("뭉뚱그리지 않고 담당자별로 정확히 2개로 분리해내는지가 핵심\n")
        f.write("테스트 포인트입니다. 또한 '타격감 포기 못 합니다' 같은 반대 의견은\n")
        f.write("최종 결정에서 기각됐으므로 Action Item으로 잘못 추출되면 안 됩니다.\n")
    print(f"✅ 정답 텍스트(화자 라벨 + 분리된 Action Item) 저장: {gt_path}")
    return gt_path


def main():
    print("CBT 일정 지연 대응(스코프 축소) 회의 샘플 생성 시작\n")
    wav_path = synthesize()
    gt_path = save_ground_truth()

    print("\n이 샘플의 특징:")
    print("  - 하향식 의사결정 구조 (경영진이 실무진 대립을 듣고 결론)")
    print("  - 한 발화에 담당자가 다른 지시 2개가 섞여 있음 (분리 추출 테스트)")
    print("  - 기각된 반대 의견(전투 기획 파트장)이 Action Item으로 오추출되면 안 됨")
    print(f"\n생성된 파일:\n  오디오: {wav_path}\n  정답 텍스트: {gt_path}")
    print("\n주의: 단일 목소리 합성이라 화자 분리 테스트에는 쓸 수 없습니다.")


if __name__ == "__main__":
    main()
