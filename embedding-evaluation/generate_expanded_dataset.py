from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

from run_eval import load_jsonl, validate_inputs


ROOT = Path(__file__).resolve().parent


SPECS = [
    ("exact_entity", "안티치트 연동 회의", "안티치트 SDK는 4.7.2 버전으로 고정한다.", "안티치트 SDK 버전은 무엇으로 정했어?", "안티치트 SDK 4.6.9는 호환성 문제로 사용하지 않기로 했다."),
    ("exact_entity", "시즌 운영 회의", "시즌 9 시작일은 9월 3일 오전 10시로 확정했다.", "시즌 9는 언제 시작해?", "시즌 8 종료일은 9월 2일 자정으로 정리했다."),
    ("exact_entity", "릴리스 회의", "QA 검증 빌드는 2.14.0-rc3으로 배포한다.", "이번 QA 검증 빌드 번호가 뭐야?", "이전 QA 빌드 2.14.0-rc2는 폐기했다."),
    ("exact_entity", "정기 점검 회의", "정기 점검은 8월 21일 오전 2시에 시작한다.", "8월 정기 점검 시작 시각은?", "예비 점검 창은 8월 22일 오전 3시다."),
    ("exact_entity", "그래픽 API 회의", "Vulkan 시험 브랜치는 graphics/vulkan-beta를 사용한다.", "Vulkan 시험 브랜치 이름이 뭐야?", "graphics/vulkan-old 브랜치는 더 이상 사용하지 않는다."),
    ("exact_entity", "크래시 대응 회의", "로비 크래시 추적 티켓은 GAME-4821이다.", "로비 크래시 티켓 번호 알려줘.", "상점 멈춤 티켓 GAME-4710도 별도로 추적한다."),
    ("exact_entity", "현지화 회의", "출시 시점 지원 언어는 총 12개로 결정했다.", "출시 지원 언어는 몇 개야?", "음성 더빙은 4개 언어만 지원한다."),
    ("exact_entity", "콘솔 인증 회의", "플레이스테이션 인증 제출일은 10월 5일이다.", "플레이스테이션 인증은 언제 제출해?", "엑스박스 인증 자료는 10월 7일에 전달한다."),
    ("semantic_paraphrase", "길드 매칭 회의", "길드전 상대는 ELO 점수와 지역을 함께 사용해 배정한다.", "길드전 상대를 고르는 기준이 뭐야?", "친선전 상대는 무작위로 선택한다."),
    ("semantic_paraphrase", "서버 증설 회의", "서버 사용률이 70퍼센트를 넘으면 자동으로 인스턴스를 늘린다.", "서버를 자동 증설하는 기준 부하는 얼마야?", "서버 사용률 40퍼센트에서는 현 상태를 유지한다."),
    ("semantic_paraphrase", "초반 이탈 분석", "튜토리얼 이탈은 장비 강화 안내가 나오는 4단계에서 가장 높다.", "신규 이용자가 가장 많이 나가는 튜토리얼 구간은?", "튜토리얼 2단계 이동 안내는 이탈률이 낮았다."),
    ("semantic_paraphrase", "저장 데이터 보안 회의", "세이브 데이터는 AES-256 방식으로 암호화한다.", "사용자 저장 파일 보호에 어떤 암호화를 써?", "전송 구간은 TLS 설정을 별도로 적용한다."),
    ("semantic_paraphrase", "몬스터 스폰 회의", "필드 정예 몬스터는 처치 후 45초 뒤에 다시 등장한다.", "정예 몬스터를 잡은 뒤 다시 나오기까지 얼마나 걸려?", "일반 몬스터 재등장 간격은 20초다."),
    ("semantic_paraphrase", "음성 채팅 회의", "음성 채팅 잡음 제거에는 RNNoise를 적용한다.", "보이스 채팅 배경 소음을 줄이는 기술은 뭐야?", "음성 코덱은 Opus를 계속 사용한다."),
    ("semantic_paraphrase", "아이템 복구 정책", "잘못 지급된 아이템은 지급 시점부터 24시간 이내에 롤백한다.", "오지급 아이템을 되돌릴 수 있는 시간 범위는?", "계정 정지 이의 신청은 7일 동안 받는다."),
    ("semantic_paraphrase", "보스 밸런스 회의", "레이드 보스는 체력이 30퍼센트 이하가 되면 광폭화한다.", "레이드 보스가 분노 상태로 바뀌는 체력 조건은?", "보스 체력 50퍼센트에는 추가 몬스터만 등장한다."),
    ("mixed_terms", "렌더링 성능 회의", "60 FPS 목표의 Frame Pacing 예산은 16.6ms로 잡는다.", "60 FPS Frame Pacing budget이 얼마야?", "30 FPS 모드의 프레임 간격은 33.3ms다."),
    ("mixed_terms", "리소스 배포 회의", "Hotfix 리소스는 resource_patch_0815 번들로 배포한다.", "이번 Hotfix resource bundle 이름은?", "정규 패치 번들은 resource_main_0820이다."),
    ("mixed_terms", "매치메이킹 정책", "장기 미접속 사용자의 MMR decay는 14일 뒤부터 적용한다.", "MMR decay가 시작되는 inactive 기간은?", "랭크 보상 수령 기간은 7일이다."),
    ("mixed_terms", "셰이더 성능 회의", "Shader Cache warmup은 로딩 화면에서 3초 동안 수행한다.", "Shader Cache warmup 시간은 얼마나 잡았어?", "런타임 셰이더 컴파일 제한은 1초다."),
    ("mixed_terms", "CDN 운영 회의", "긴급 패치 뒤 CDN purge는 배포 완료 후 5분 안에 실행한다.", "배포 후 CDN purge SLA는?", "정기 캐시 갱신은 매일 자정에 실행한다."),
    ("mixed_terms", "Telemetry 정책 회의", "Telemetry opt-out 설정은 환경설정의 개인정보 메뉴에 둔다.", "Telemetry opt-out 메뉴 위치가 어디야?", "그래픽 진단 정보는 고객지원 메뉴에서 확인한다."),
    ("action_item", "인벤토리 오류 회의", "박지훈이 8월 14일까지 인벤토리 아이템 복제 오류를 수정한다.", "인벤토리 복제 오류 담당자와 기한은?", "최민수는 인벤토리 정렬 개선안을 다음 회의에 공유한다."),
    ("action_item", "부하 테스트 회의", "이서연이 내일 오후까지 부하 테스트 결과 보고서를 갱신한다.", "부하 테스트 보고서 후속 작업은 누가 언제까지 해?", "김태호는 다음 달 성능 테스트 계획을 검토한다."),
    ("action_item", "등급 심의 회의", "김하늘이 8월 18일까지 게임물 등급 심의 자료를 제출한다.", "등급 심의 자료 제출 담당자와 마감일은?", "법무팀은 개인정보 문구를 별도로 확인한다."),
    ("action_item", "수익화 검토 회의", "최유진이 금요일까지 수익화 지표 시트를 수정한다.", "수익화 지표 시트 수정 후속 업무는?", "사업팀은 다음 분기 가격 정책을 추후 논의한다."),
    ("metadata_filter", "월요일 빌드 회의", "A팀 QA 빌드는 8월 25일에 배포한다.", "A팀 QA 빌드 배포일은?", "B팀 QA 빌드는 8월 27일에 배포한다."),
    ("metadata_filter", "전투팀 회의", "김전투가 신규 보스 패턴 검수를 8월 28일까지 맡는다.", "김전투가 맡은 보스 검수 기한은?", "이기획은 보스 보상표를 다음 주에 검토한다."),
    ("metadata_filter", "8월 운영 회의", "8월 29일 이벤트 서버를 사전 오픈한다.", "8월 운영 회의에서 정한 이벤트 서버 오픈일은?", "7월 운영 회의에서는 이벤트 서버 일정을 확정하지 못했다."),
    ("metadata_filter", "클라이언트 A 회의", "클라이언트 A의 메모리 점검은 9월 1일까지 완료한다.", "클라이언트 A 메모리 점검 마감은?", "클라이언트 B의 메모리 점검은 9월 4일까지 진행한다."),
]


UNANSWERABLE = [
    "닌텐도 스위치 출시일은 언제로 확정됐어?",
    "브라질 전용 서버는 언제 열어?",
    "VR 모드는 어떤 기기를 지원해?",
    "블록체인 NFT 아이템을 도입하기로 했어?",
    "유명 배우 컬래버레이션 일정 알려줘.",
    "아랍어 음성 더빙 담당 업체는 어디야?",
    "e스포츠 월드컵 총상금은 얼마야?",
    "macOS 앱스토어 심사 제출일은?",
    "확률형 아이템의 전설 등급 확률은 몇 퍼센트야?",
    "스팀덱 공식 인증을 언제 받았어?",
]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")


def main() -> None:
    corpus = load_jsonl(ROOT / "corpus" / "pilot_meeting_chunks.jsonl")
    cases = load_jsonl(ROOT / "cases" / "pilot_cases.jsonl")
    base_date = date(2026, 8, 11)

    for offset, (category, title, answer, query, near) in enumerate(SPECS, 21):
        index = offset - 20
        meeting_id = f"meeting-expanded-{index:03d}"
        chunk_id = f"chunk-expanded-{index:03d}-answer"
        meeting_date = base_date + timedelta(days=index % 20)
        participant = f"user-expanded-{index % 7}"
        corpus.extend([
            {
                "meeting_chunk_id": chunk_id,
                "meeting_id": meeting_id,
                "meeting_title": title,
                "meeting_date": meeting_date.isoformat(),
                "participant_user_ids": [participant],
                "content": answer,
            },
            {
                "meeting_chunk_id": f"chunk-expanded-{index:03d}-near",
                "meeting_id": f"meeting-expanded-{index:03d}-near",
                "meeting_title": title + " 참고",
                "meeting_date": (meeting_date - timedelta(days=7)).isoformat(),
                "participant_user_ids": [f"user-expanded-{(index + 1) % 7}"],
                "content": near,
            },
        ])
        filters = {}
        if category == "metadata_filter":
            filters = {"meeting_ids": [meeting_id]}
        cases.append({
            "case_id": f"retrieval-{offset:03d}",
            "query": query,
            "relevant_chunk_ids": [chunk_id],
            "filters": filters,
            "category": category,
            "answerable": True,
        })

    systems = ["로그인", "퀘스트", "상점", "우편", "친구", "채팅", "파티", "길드", "전투", "캐릭터", "장비", "업적", "월드맵", "NPC", "던전", "레이드", "로비", "패치", "결제", "알림"]
    activities = ["로그 수집", "예외 처리", "화면 전환", "상태 동기화", "메모리 사용", "응답 코드", "권한 확인", "재접속", "데이터 검증", "캐시 갱신", "부하 분산", "접근성", "애니메이션", "사운드 출력", "번역 문구"]
    filler_count = 1000 - len(corpus)
    for index in range(filler_count):
        system = systems[index % len(systems)]
        activity = activities[(index // len(systems)) % len(activities)]
        corpus.append({
            "meeting_chunk_id": f"chunk-distractor-{index + 1:04d}",
            "meeting_id": f"meeting-distractor-{index // 4 + 1:04d}",
            "meeting_title": f"{system} 모듈 점검 {index // 4 + 1}",
            "meeting_date": (date(2026, 1, 1) + timedelta(days=index % 210)).isoformat(),
            "participant_user_ids": [f"user-distractor-{index % 12}"],
            "content": f"{system} 모듈의 {activity} 항목을 점검했고 테스트 묶음 D-{index + 1:04d}에서 특이사항이 없었다.",
        })

    for index, query in enumerate(UNANSWERABLE, 51):
        cases.append({
            "case_id": f"retrieval-{index:03d}",
            "query": query,
            "relevant_chunk_ids": [],
            "filters": {},
            "category": "unanswerable",
            "answerable": False,
        })

    if len(corpus) != 1000 or len(cases) != 60:
        raise RuntimeError(f"생성 개수 오류: Corpus {len(corpus)}, Case {len(cases)}")
    validate_inputs(corpus, cases)
    write_jsonl(ROOT / "corpus" / "expanded_meeting_chunks.jsonl", corpus)
    write_jsonl(ROOT / "cases" / "expanded_cases.jsonl", cases)
    print(f"Corpus {len(corpus)}개, Case {len(cases)}개 생성 및 검증 완료")


if __name__ == "__main__":
    main()
