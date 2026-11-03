"""
generate_meeting_bm_revamp_audio.py
사업/데이터/기획 협업 회의(1주년 업데이트 BM 개편, 프리미엄 패스·천장 이월) 샘플 음성 생성 스크립트

Workmate AI의 회의 분석(M3)·회의 검색(M4) 테스트용 샘플 데이터입니다.
지금까지와 달리 ARPU, LTV 등 비즈니스/데이터 지표 용어가 등장하고,
"단기 리스크(매출 감소 우려) vs 장기 이득(잔존율 상승)"이라는
트레이드오프 논증 구조를 가진 회의입니다. 회의 요약이 이런 논증
구조(우려 제기 → 반박 근거 → 최종 승인)를 순서대로 보존하는지
테스트하기 좋습니다.

⚠️ 등장 인물은 역할명(사업 실장/데이터 분석가/기획 팀장/PD)으로
   표기됩니다. 가격("3만 3천 원"), 비율("80%") 등은 전부 가상의
   샘플 데이터입니다.

⚠️ gTTS는 단일 목소리만 지원합니다. 화자 4명의 대사를 한 목소리로
   순서대로 이어 읽습니다 — 화자 분리(diarization) 검증에는 쓸 수 없고,
   STT 인식률·회의 요약·근거 검색 테스트에만 사용하세요.

사용법:
    pip install gTTS pydub
    python generate_meeting_bm_revamp_audio.py
"""

from pathlib import Path

from gtts import gTTS
from pydub import AudioSegment

OUTPUT_DIR = Path("audio/samples")
OUT_NAME = "meeting-bm-revamp"

DIALOGUE = [
    ("사업 실장", "다음 달 1주년 업데이트의 핵심은 매출 반등입니다. 기존 월정액이랑 패키지 구조로는 에이알피유, 가입자당 평균 매출이 정체되어 있어서, 헤비 유저와 라이트 유저를 동시에 저격할 수 있는 신규 비엠이 필요합니다. 데이터 분석가님, 유저 지출 패턴 분석 결과 좀 공유해 주세요."),
    ("데이터 분석가", "소과금 유저는 1만 원대 패키지 구매율이 80퍼센트로 압도적이지만, 무과금에서 소과금으로 넘어오는 장벽이 높습니다. 반면 헤비 유저는 픽업 캐릭터 6돌파, 최대 강화까지 평균 80만 원 이상 쓰는데, 천장 이월 시스템이 없어서 이탈률이 최근 늘었습니다."),
    ("기획 팀장", "그래서 이번에 슈퍼 프리미엄 패스를 도입하려고 합니다. 기존 패스 보상에 더해 전용 코스튬이랑 매일 재화를 주고, 가격은 3만 3천 원으로 잡았습니다. 그리고 헤비 유저를 위해 다음 시즌부터는 픽업 천장 횟수가 다음 가챠로 50퍼센트 이월되도록 시스템을 뜯어고칠 계획입니다."),
    ("PD", "천장 이월은 매출에 단기적으로 타격이 없겠습니까?"),
    ("데이터 분석가", "당장 1주에서 2주는 매출이 주춤할 수 있으나, 과금 스트레스가 줄어들면서 3개월 잔존율이 올라가기 때문에 엘티브이, 고객 생애 가치 관점에서는 무조건 이득입니다."),
    ("사업 실장", "좋습니다. 기획안대로 가되, 1주년 방송 일자에 맞춰서 패스 혜택을 크게 체감할 수 있도록 마케팅 문구 잘 뽑아주세요."),
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
    """화자 라벨 포함 원본 대사 + 논증 구조·결정 사항을 별도 텍스트로 저장."""
    gt_path = OUTPUT_DIR / f"{OUT_NAME}.ground_truth.txt"
    with open(gt_path, "w", encoding="utf-8") as f:
        f.write("=== 대사 (화자 라벨 포함) ===\n")
        for speaker, line in DIALOGUE:
            f.write(f"[{speaker}] {line}\n")

        f.write("\n=== 회의 핵심 요약 ===\n")
        f.write("- 배경: ARPU 정체로 신규 BM 필요\n")
        f.write("- 데이터: 소과금 유저는 1만 원대 패키지 구매율 80%, "
                 "무과금→소과금 전환 장벽 높음 / 헤비 유저는 평균 80만 원+ 지출하나 "
                 "천장 이월 부재로 이탈률 증가\n")
        f.write("- 신규 BM안: '슈퍼 프리미엄 패스'(3만 3천 원, 전용 코스튬+매일 재화), "
                 "픽업 천장 횟수 50% 이월 시스템\n")
        f.write("- 우려(PD): 천장 이월이 단기 매출에 타격 줄 수 있음\n")
        f.write("- 반박(데이터 분석가): 1~2주 단기 매출 감소 있으나, "
                 "3개월 잔존율 상승으로 LTV 관점 이득\n")
        f.write("- 최종 결정(사업 실장): 기획안 승인, 1주년 방송 일정에 맞춰 마케팅 준비\n")

        f.write("\n=== Action Item ===\n")
        f.write("1. 담당자: 기획팀 / 내용: 슈퍼 프리미엄 패스 및 천장 이월 시스템 구현 준비 "
                 "(구체적 기한 미명시, '다음 시즌부터' 적용)\n")
        f.write("2. 담당자: 명시 안 됨(마케팅 담당 추정) / 내용: 1주년 방송 일자에 맞춘 "
                 "패스 혜택 마케팅 문구 준비 (구체적 기한 미명시)\n")

        f.write("\n=== 참고 — 이 샘플의 특징 ===\n")
        f.write("비즈니스/데이터 지표(ARPU, LTV) 용어가 등장하고,\n")
        f.write("'우려 제기 → 반박 근거 → 승인'이라는 논증 구조를 가진 회의입니다.\n")
        f.write("회의 요약이 이 논증 순서(단기 리스크 vs 장기 이득)를 보존하는지,\n")
        f.write("Action Item에서 담당자가 불명확한 항목(2번)을 억지로 특정 인물에게\n")
        f.write("배정하지 않는지 확인하는 용도로 유용합니다.\n")
    print(f"✅ 정답 텍스트(화자 라벨 + 논증 구조 + Action Item) 저장: {gt_path}")
    return gt_path


def main():
    print("1주년 업데이트 BM 개편 회의 샘플 생성 시작\n")
    wav_path = synthesize()
    gt_path = save_ground_truth()

    print("\n이 샘플의 특징:")
    print("  - ARPU, LTV 등 비즈니스 지표 용어 등장")
    print("  - '우려 제기 → 반박 근거 → 승인' 논증 구조 회의")
    print("  - Action Item 중 담당자가 불명확한 항목 포함 (환각 방지 테스트용)")
    print(f"\n생성된 파일:\n  오디오: {wav_path}\n  정답 텍스트: {gt_path}")
    print("\n주의: 단일 목소리 합성이라 화자 분리 테스트에는 쓸 수 없습니다.")


if __name__ == "__main__":
    main()
