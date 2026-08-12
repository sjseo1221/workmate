"""Generate 20 Korean gTTS cases for STT pipeline evaluation."""
from __future__ import annotations

import json
from pathlib import Path

from gtts import gTTS


ROOT = Path(__file__).parent
AUDIO = ROOT / "audio" / "pilot"
CASES = ROOT / "cases" / "synthetic_cases_20.jsonl"
TEXTS = [
    ("QA 빌드", "QA 빌드 검토 회의입니다. 오늘 오후까지 QA 빌드 결과를 공유합니다."),
    ("로그인 오류", "로그인 오류를 재현했습니다. 내일 오전까지 원인을 분석합니다."),
    ("캐릭터 밸런스", "신규 캐릭터 밸런스를 검토하고 금요일까지 수치를 확정합니다."),
    ("서버 재시작", "테스트 서버 재시작 절차를 문서화하고 담당자에게 공유합니다."),
    ("회귀 테스트", "회귀 테스트는 8월 12일 QA 빌드 기준으로 진행합니다."),
    ("스토어 심사", "스토어 심사 제출 전 개인정보 문구를 다시 확인합니다."),
    ("메모리 누수", "메모리 누수 원인을 프로파일링하고 다음 주 월요일에 결과를 보고합니다."),
    ("트레일러", "게임 트레일러 영상과 음원을 각각 검수합니다."),
    ("배포 자동화", "배포 자동화 스크립트를 적용하고 실패 로그를 확인합니다."),
    ("결제 오류", "결제 오류 로그를 수집해 운영팀에 전달합니다."),
    ("저사양", "저사양 기기에서 그림자 품질을 낮추고 프레임을 측정합니다."),
    ("번역", "한국어와 영어 번역을 검수하고 오탈자를 수정합니다."),
    ("네트워크 지연", "네트워크 지연을 측정하고 핑이 높은 구간을 표시합니다."),
    ("튜토리얼", "튜토리얼 이탈률을 확인하고 첫 번째 퀘스트를 개선합니다."),
    ("로그", "서버 로그를 30일 동안 보관하고 접근 권한을 제한합니다."),
    ("안드로이드 빌드", "안드로이드 빌드를 생성하고 테스트 기기에 설치합니다."),
    ("iOS", "iOS 배포 인증서 만료일을 확인하고 갱신 일정을 등록합니다."),
    ("공지", "업데이트 공지를 작성하고 기획팀 검토를 요청합니다."),
    ("크래시", "크래시 리포트를 분석해 재현 조건과 우선순위를 정합니다."),
    ("출시 체크리스트", "출시 체크리스트를 점검하고 미완료 항목을 담당자에게 배정합니다."),
]


def main() -> None:
    AUDIO.mkdir(parents=True, exist_ok=True)
    rows = []
    for index, (must_include, text) in enumerate(TEXTS, 1):
        case_id = f"synthetic-{index:03d}"
        path = AUDIO / f"{case_id}.mp3"
        print(f"[{index}/{len(TEXTS)}] {case_id}")
        gTTS(text=text, lang="ko").save(str(path))
        rows.append({"case_id": case_id, "audio": f"audio/pilot/{path.name}", "language": "ko", "must_include": [must_include], "forbidden": ["출시 완료"], "expected_speaker_count": None})
    CASES.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n", encoding="utf-8")
    print(f"Wrote {len(rows)} cases to {CASES}")


if __name__ == "__main__":
    main()
