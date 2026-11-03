"""
generate_meeting_character_art_review_audio.py
아트/마케팅 협업 회의(지스타 시연용 캐릭터 원화 검수, 글로벌 디자인 방향성) 샘플 음성 생성 스크립트

Workmate AI의 회의 분석(M3)·회의 검색(M4) 테스트용 샘플 데이터입니다.
지금까지의 백엔드/인프라/기획 회의와 달리, 정량 데이터 없이
"의견 대립 → 상위 의사결정자의 최종 조율"로 끝나는 크리에이티브
디렉션 회의입니다. Action Item이 명시적 업무 지시가 아니라
"이 방향으로 진행" 수준의 방향성 합의로 끝나는 케이스라,
Action Item 추출이 이런 경우 무리하게 세부 업무를 지어내지 않고
방향성 합의로 정확히 요약하는지 테스트하기 좋습니다.

⚠️ 등장 인물은 이름 대신 역할명(총괄 PD/AD/원화 파트장/마케팅 팀장)
   으로 표기됩니다. 캐릭터명("카렌") 등은 전부 가상의 샘플 데이터입니다.

⚠️ gTTS는 단일 목소리만 지원합니다. 화자 4명의 대사를 한 목소리로
   순서대로 이어 읽습니다 — 화자 분리(diarization) 검증에는 쓸 수 없고,
   STT 인식률·회의 요약·근거 검색 테스트에만 사용하세요.

사용법:
    pip install gTTS pydub
    python generate_meeting_character_art_review_audio.py
"""

from pathlib import Path

from gtts import gTTS
from pydub import AudioSegment

OUTPUT_DIR = Path("audio/samples")
OUT_NAME = "meeting-character-art-review"

DIALOGUE = [
    ("총괄 PD", "오늘 모인 건 다음 달 글로벌 지스타 시연용으로 나갈 핵심 캐릭터 3종 원화 검수 때문입니다. AD님, 전반적인 채색 톤이랑 라인업 피드백 설명 부탁드립니다."),
    ("AD", "지난 1차 에프지티에서 서구권 유저 비중을 늘려야 한다는 피드백을 반영해서, 이번 2차 캐릭터들은 채도를 살짝 낮추고 실루엣의 명암 대비를 강하게 주었습니다. 특히 메인 히어로인 카렌은 복장 노출도를 줄이고 밀리터리 디테일을 강화했습니다."),
    ("원화 파트장", "밀리터리 디테일을 올리다 보니 아시아권 서브컬처 유저들이 좋아하는 화려한 장신구나 애니메이션 특유의 감성이 조금 죽었다는 내부 의견도 있습니다. 너무 무거워진 게 아닌가 걱정되네요."),
    ("마케팅 팀장", "제 생각엔 오히려 좋습니다. 북미, 유럽 시장에서는 너무 전형적인 미소녀풍보다 유니크한 택티컬 디자인이 트위터나 레딧에서 바이럴되기 훨씬 유리해요. 단, 일본 시장 마케팅을 위해 일러스트레이터 특전 스킨 정도는 나중에 따로 준비해야 할 것 같습니다."),
    ("총괄 PD", "마케팅 의견에 동의합니다. 글로벌 원빌드로 가려면 지금 택티컬 방향성을 유지하는 게 맞아요. 대신 인게임 에스디 캐릭터나 로비 일러스트레이터 표정 베리에이션에서 서브컬처 특유의 매력을 살리는 방향으로 가죠. 이대로 진행합시다."),
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
    """화자 라벨 포함 원본 대사 + 방향성 합의(Action Item과 성격이 다름)를 별도 텍스트로 저장."""
    gt_path = OUTPUT_DIR / f"{OUT_NAME}.ground_truth.txt"
    with open(gt_path, "w", encoding="utf-8") as f:
        f.write("=== 대사 (화자 라벨 포함) ===\n")
        for speaker, line in DIALOGUE:
            f.write(f"[{speaker}] {line}\n")

        f.write("\n=== 회의 핵심 요약 ===\n")
        f.write("- 안건: 지스타 시연용 핵심 캐릭터 3종 원화 검수\n")
        f.write("- 변경: 서구권向 피드백 반영해 채도 낮춤, 명암 대비 강화, "
                 "메인 캐릭터 '카렌' 노출도 축소·밀리터리 디테일 강화\n")
        f.write("- 우려(원화 파트장): 아시아 서브컬처 감성 약화 걱정\n")
        f.write("- 반론(마케팅 팀장): 서구권 바이럴에는 유리, 일본 시장은 별도 특전 스킨으로 대응\n")
        f.write("- 최종 결정(총괄 PD): 택티컬 방향성 유지, 서브컬처 매력은 "
                 "SD 캐릭터·로비 일러스트 표정 베리에이션에서 보완\n")

        f.write("\n=== Action Item — 이번 회의는 세부 업무 지시가 아닌 '방향성 합의'입니다 ===\n")
        f.write("담당자·기한이 명시된 전통적 Action Item은 없고, 아래처럼\n")
        f.write("방향성 결정 사항으로 요약되는 것이 정확한 처리입니다:\n")
        f.write("1. 확정: 캐릭터 원화 방향성 — 택티컬/밀리터리 디자인 유지 (전체 팀 합의)\n")
        f.write("2. 향후 검토: 일본 시장向 일러스트레이터 특전 스킨 별도 제작 (담당·기한 미정, 마케팅팀 제안)\n")
        f.write("3. 향후 검토: SD 캐릭터·로비 일러스트 표정 베리에이션으로 서브컬처 감성 보완 "
                 "(담당·기한 미정, 총괄 PD 제안)\n")

        f.write("\n=== 참고 — 이 샘플의 특징 ===\n")
        f.write("정량 데이터나 구체적 기한 없이 '의견 대립 → 상위 결정자 조율'로 끝나는\n")
        f.write("크리에이티브 디렉션 회의입니다. Action Item 추출 로직이 이런 경우\n")
        f.write("존재하지 않는 담당자·기한을 억지로 지어내지 않고, '방향성 합의'와\n")
        f.write("'향후 검토 필요'를 구분해서 처리하는지 확인하는 용도로 유용합니다.\n")
    print(f"✅ 정답 텍스트(화자 라벨 + 방향성 합의 요약) 저장: {gt_path}")
    return gt_path


def main():
    print("지스타 시연용 캐릭터 원화 검수 회의 샘플 생성 시작\n")
    wav_path = synthesize()
    gt_path = save_ground_truth()

    print("\n이 샘플의 특징:")
    print("  - 정량 데이터 없이 의견 대립 → 상위 결정자 조율로 끝나는 크리에이티브 회의")
    print("  - '전통적 Action Item(담당자+기한)'이 아니라 '방향성 합의' 형태")
    print("  - Action Item 추출이 없는 정보를 지어내지 않는지 테스트하기 좋음")
    print(f"\n생성된 파일:\n  오디오: {wav_path}\n  정답 텍스트: {gt_path}")
    print("\n주의: 단일 목소리 합성이라 화자 분리 테스트에는 쓸 수 없습니다.")


if __name__ == "__main__":
    main()
