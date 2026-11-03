"""
generate_meeting_story_faction_design_audio.py
스토리/시스템/아트 기획 회의(신규 이벤트 세력 '무명회' 설계) 샘플 음성 생성 스크립트

Workmate AI의 회의 분석(M3)·회의 검색(M4) 테스트용 샘플 데이터입니다.
지금까지의 회의들과 달리 업무 진행 상황이나 의사결정이 아니라
"게임 세계관·캐릭터·시스템 설계 내용" 자체가 회의의 본론입니다.
Action Item(누가 언제 뭘 할지)이 아니라 콘텐츠 설계 스펙(세력 관계,
영향력 시스템, 분기 결말 조건)이 핵심 정보라서, 회의 검색(M4)이
"연화가 누구야?", "무명회 영향력이 오르는 조건이 뭐야?" 같은
세계관/스펙 질문에 정확히 답하는지 테스트하기 좋습니다.

⚠️ 등장 인물은 역할명(기획팀장/스토리 기획자/시스템 기획자/
   아트 디렉터)으로 표기됩니다. 등장하는 세력명("무명회"), 인물명
   ("연화", "홍길동", "전우치")은 전부 가상의 샘플 데이터입니다.

⚠️ gTTS는 단일 목소리만 지원합니다. 화자 4명의 대사를 한 목소리로
   순서대로 이어 읽습니다 — 화자 분리(diarization) 검증에는 쓸 수 없고,
   STT 인식률·설계 스펙 추출·회의 검색 테스트에만 사용하세요.

사용법:
    pip install gTTS pydub
    python generate_meeting_story_faction_design_audio.py
"""

from pathlib import Path

from gtts import gTTS
from pydub import AudioSegment

OUTPUT_DIR = Path("audio/samples")
OUT_NAME = "meeting-story-faction-design"

DIALOGUE = [
    ("기획팀장", "홍길동과 전우치 세력 사이에 무명회를 신규 이벤트 세력으로 추가합시다. 연화는 무명회의 중심인물이며, 어느 한쪽에도 속하지 않습니다."),
    ("스토리 기획자", "무명회는 두 세력의 충돌로 피해를 입은 이들이 만든 비밀 조직입니다. 연화는 홍길동과 전우치 모두 명분 아래 세력을 넓히고 있다고 보고, 플레이어에게 누구의 편인지보다 누구를 위한 선택인지를 묻습니다."),
    ("시스템 기획자", "플레이어가 홍길동의 의뢰를 수행하면 홍길동 영향력이, 전우치의 비밀 의뢰를 수행하면 전우치 영향력이 상승합니다. 무명회의 구호와 중재 임무를 수행하면 무명회 영향력이 상승하고, 두 세력의 충돌을 완화하는 특별 루트가 열립니다."),
    ("아트 디렉터", "연화는 흰 연꽃과 붉은 실을 상징으로 사용하겠습니다. 첫 등장에서는 두 세력의 충돌 속에서 주민을 대피시키며 무명회의 존재를 보여줍니다."),
    ("기획팀장", "결말은 세 갈래로 갑시다. 홍길동 또는 전우치 영향력이 높으면 무명회는 각 세력에 편입되고, 무명회 영향력이 충분하면 연화가 두 세력과 동등한 협약을 맺는 독립 결말로 이어집니다."),
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
    """화자 라벨 포함 원본 대사 + 설계 스펙(질의응답 테스트용)을 별도 텍스트로 저장."""
    gt_path = OUTPUT_DIR / f"{OUT_NAME}.ground_truth.txt"
    with open(gt_path, "w", encoding="utf-8") as f:
        f.write("=== 대사 (화자 라벨 포함) ===\n")
        for speaker, line in DIALOGUE:
            f.write(f"[{speaker}] {line}\n")

        f.write("\n=== 회의 핵심 요약 ===\n")
        f.write("- 결정: 홍길동/전우치 세력 사이에 신규 이벤트 세력 '무명회' 추가\n")
        f.write("- 중심인물: 연화 (무명회 소속, 특정 세력에 속하지 않음)\n")
        f.write("- 세계관 설정: 무명회는 두 세력 충돌로 피해 입은 이들이 만든 비밀 조직\n")
        f.write("- 시스템: 홍길동 의뢰→홍길동 영향력 상승 / 전우치 비밀 의뢰→전우치 영향력 상승 / "
                 "무명회 구호·중재 임무→무명회 영향력 상승 및 특별 루트 개방\n")
        f.write("- 아트: 연화 상징은 흰 연꽃과 붉은 실, 첫 등장은 세력 충돌 중 주민 대피 장면\n")
        f.write("- 결말 분기(3갈래): (1) 홍길동 영향력 높음→무명회 홍길동에 편입 "
                 "(2) 전우치 영향력 높음→무명회 전우치에 편입 "
                 "(3) 무명회 영향력 충분→연화가 두 세력과 동등 협약을 맺는 독립 결말\n")

        f.write("\n=== 질의응답 테스트용 예상 질문·정답 (M4 회의 검색용) ===\n")
        f.write("Q: 연화는 누구야? → A: 무명회의 중심인물이며 어느 세력에도 속하지 않음\n")
        f.write("Q: 무명회 영향력은 어떻게 올라? → A: 무명회의 구호·중재 임무 수행 시 상승\n")
        f.write("Q: 무명회의 상징은? → A: 흰 연꽃과 붉은 실\n")
        f.write("Q: 독립 결말의 조건은? → A: 무명회 영향력이 충분할 때, "
                 "연화가 두 세력과 동등한 협약을 맺음\n")

        f.write("\n=== 참고 — 이 샘플의 특징 ===\n")
        f.write("업무 진행 상황이 아니라 '게임 세계관·캐릭터·시스템 설계 내용' 자체가\n")
        f.write("본론인 회의입니다. 전통적 Action Item(담당자+기한)은 없고, 대신\n")
        f.write("세력 관계·영향력 시스템·분기 결말 조건 같은 콘텐츠 스펙이 핵심 정보입니다.\n")
        f.write("M4(회의 검색)가 이런 세계관 질문에 정확한 근거로 답하는지 테스트하는\n")
        f.write("용도로 특히 유용합니다.\n")
    print(f"✅ 정답 텍스트(화자 라벨 + 설계 스펙 + 예상 질의응답) 저장: {gt_path}")
    return gt_path


def main():
    print("신규 이벤트 세력 스토리 기획 회의 샘플 생성 시작\n")
    wav_path = synthesize()
    gt_path = save_ground_truth()

    print("\n이 샘플의 특징:")
    print("  - 업무 진행이 아닌 '세계관/시스템 설계 내용' 자체가 본론")
    print("  - Action Item이 아니라 콘텐츠 스펙(세력, 영향력, 결말 분기)이 핵심 정보")
    print("  - M4(회의 검색)의 세계관 질의응답 테스트에 특화된 샘플")
    print(f"\n생성된 파일:\n  오디오: {wav_path}\n  정답 텍스트: {gt_path}")
    print("\n주의: 단일 목소리 합성이라 화자 분리 테스트에는 쓸 수 없습니다.")


if __name__ == "__main__":
    main()
