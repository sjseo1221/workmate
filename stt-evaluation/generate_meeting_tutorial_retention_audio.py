"""
generate_meeting_tutorial_retention_audio.py
기획/아트/개발 협업 회의(CBT 튜토리얼 이탈률 데이터 분석, 개선 방향) 샘플 음성 생성 스크립트

Workmate AI의 회의 분석(M3)·회의 검색(M4) 테스트용 샘플 데이터입니다.
지금까지 만든 샘플이 전부 백엔드/인프라 도메인이었던 것과 달리,
이번엔 기획·아트·클라이언트가 섞인 "데이터 기반 의사결정" 회의라서
Action Item이 명확한 문장으로 안 끊기고 "다음 단계 논의"로 흐르는
케이스입니다. 요약·근거 추출이 실제 회의처럼 애매한 지점을
어떻게 처리하는지 테스트하기 좋습니다.

⚠️ 등장 인물은 이름 대신 직무명(PM/기획팀장/AD/개발자)으로만 표기됩니다.
   프로젝트명("프로젝트 X"), 수치(완료율 68% 등)는 전부 가상의
   샘플 데이터입니다.

⚠️ gTTS는 단일 목소리만 지원합니다. 화자 4명의 대사를 한 목소리로
   순서대로 이어 읽습니다 — 화자 분리(diarization) 검증에는 쓸 수 없고,
   STT 인식률·회의 요약·근거 검색 테스트에만 사용하세요.

사용법:
    pip install gTTS pydub
    python generate_meeting_tutorial_retention_audio.py
"""

from pathlib import Path

from gtts import gTTS
from pydub import AudioSegment

OUTPUT_DIR = Path("audio/samples")
OUT_NAME = "meeting-tutorial-retention"

DIALOGUE = [
    ("PM", "다들 오셨죠. 오늘 미팅은 지난주에 시작된 프로젝트 엑스 CBT 튜토리얼 구간 데이터 복기 및 개선점 도출 건입니다. 데이터 먼저 공유해 드리면, 튜토리얼 1에서 3 완료율이 목표치인 85퍼센트에 못 미치는 68퍼센트로 나왔습니다. 이탈 지점이 생각보다 이른 편인데, 기획팀에서 원인 분석해 주신 내용 공유 가능할까요?"),
    ("기획팀장", "네, 이탈 로그를 쪼개보니 1-2 전투 종료 후 나오는 장비 강화 강제 튜토리얼 섹션에서 가장 많이 떨어져 나갔습니다. 플레이어가 스킵도 못 하는 상태에서 유아이 가이드 화살표만 연속으로 일곱 번 클릭해야 하는 구조인데요. 가스라이팅 수준의 강제 동선 때문에 초반 흐름, 페이싱이 끊기는 게 주요 원인으로 파악됐습니다."),
    ("AD", "저도 그 부분 동의해요. 그리고 튜토리얼 연출 때 대사창 텍스트가 너무 길어서 몰입감을 해칩니다. 라이트 유저들은 글이 세 줄만 넘어가도 바로 화면 아무 데나 연타하거든요. 일러스트랑 컷신 연출을 살리려면 대사 연출을 대폭 줄이고 보이스 지원이랑 연출 템포를 훨씬 타이트하게 잡아야 합니다."),
    ("개발자", "연출이랑 튜토리얼 동선 줄이는 건 클라이언트 쪽에서 바로 반영 가능합니다. 다만 기획팀에 여쭤보고 싶은 게, 강제 튜토리얼을 빼면 유저들이 강화 시스템을 안 거치고 1-4 보스전에 진입할 텐데, 난이도 불쾌감 문제는 괜찮을까요?"),
    ("기획팀장", "그래서 방식을 바꾸려고 합니다. 1-2 끝나고 강제로 강화 창으로 끌고 가는 게 아니라, 1-3 진입 전에 자연스럽게 승리 보상으로 강화된 무기를 지급하고, 첫 번째 실패 시점에 가이드 메시지 팝업을 띄우는 자율형 튜토리얼로 변경할 생각입니다."),
    ("PM", "좋네요. 그럼 개선 방향성을 정리해 보겠습니다."),
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
    """화자 라벨 포함 원본 대사 + 요약/미결 항목을 별도 텍스트로 저장."""
    gt_path = OUTPUT_DIR / f"{OUT_NAME}.ground_truth.txt"
    with open(gt_path, "w", encoding="utf-8") as f:
        f.write("=== 대사 (화자 라벨 포함) ===\n")
        for speaker, line in DIALOGUE:
            f.write(f"[{speaker}] {line}\n")

        f.write("\n=== 회의 핵심 요약 (근거 검색 테스트용 키워드) ===\n")
        f.write("- 데이터: 튜토리얼 1~3 완료율 68% (목표 85% 미달)\n")
        f.write("- 원인1: 장비 강화 강제 튜토리얼(스킵 불가, 7회 연속 클릭)에서 이탈 집중\n")
        f.write("- 원인2: 대사창 텍스트 과다로 몰입감 저하 (AD팀 지적)\n")
        f.write("- 우려사항: 강제 튜토리얼 제거 시 1-4 보스전 난이도 불쾌감 리스크 (개발자 제기)\n")
        f.write("- 개선방향: 강제 강화 튜토리얼 → '자율형 튜토리얼'로 전환 "
                 "(승리 보상으로 무기 지급 + 실패 시 가이드 팝업)\n")

        f.write("\n=== 명시적 Action Item 없음 — 회의가 결론 확정 전에 종료됨 ===\n")
        f.write("이 회의는 'PM: 그럼 개선 방향성을 정리해 보겠습니다'로 끝나며,\n")
        f.write("담당자·기한이 명시된 Action Item이 아직 나오지 않은 상태입니다.\n")
        f.write("Workmate AI의 Action Item 추출 로직이 이런 경우 "
                 "'미결/후속 논의 필요'로 정확히 구분하는지 확인하는 용도로 쓰기 좋습니다.\n")
    print(f"✅ 정답 텍스트(화자 라벨 + 요약) 저장: {gt_path}")
    return gt_path


def main():
    print("CBT 튜토리얼 이탈률 분석 회의 샘플 생성 시작\n")
    wav_path = synthesize()
    gt_path = save_ground_truth()

    print("\n이 샘플의 특징:")
    print("  - 지금까지의 백엔드/인프라 도메인과 다른 기획·아트·클라이언트 협업 회의")
    print("  - 회의가 결론 확정 전에 끝나서, 명시적 Action Item이 '없는' 케이스")
    print("  - Action Item 추출 로직이 '없음'을 정확히 판단하는지 테스트하기 좋음")
    print(f"\n생성된 파일:\n  오디오: {wav_path}\n  정답 텍스트: {gt_path}")
    print("\n주의: 단일 목소리 합성이라 화자 분리 테스트에는 쓸 수 없습니다.")


if __name__ == "__main__":
    main()
