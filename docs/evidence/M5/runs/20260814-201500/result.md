# Orchestrator 채팅 Skill 라우팅 연동 검수 결과

## 배경

다른 팀원이 개발한 `AI-agent_game_platform` Orchestrator에 Workmate를 UI로
연동하는 작업 중 Orchestrator `Workmate AI` 채팅 경로가 `skill_id`를 고르지
못하고 항상 `daily_briefing`을 고정으로 보내는 문제를 발견했다. Orchestrator
저장소는 읽기 전용 제약이 있어 Workmate 쪽 `m51_legacy_adapter.py`에서
해결했다.

## 기본 정보

- 실행 ID: `20260814-201500`
- 상태: 완료
- 검수 방식: 단위 테스트 + Docker Compose E2E (수동 실행, 사용자 승인 하에 Docker 기동)

## 변경 범위

Workmate 저장소만 수정했다. Orchestrator(`AI-agent_game_platform`) 저장소는
수정하지 않았다.

- `tools/m51_legacy_adapter.py`
  - `_infer_skill`: 회의 검색/분석을 먼저 구분하도록 키워드 판정을 다시
    작성하고 중복 정의를 제거했다(기존 코드는 동일 함수가 두 번 정의되어
    뒤쪽 정의가 앞쪽을 덮어썼다).
  - Orchestrator 채팅 경로가 보내는 `{skill_id: "daily_briefing", message}`
    고정 요청만 재판정 대상으로 삼고, `payload` 필드가 함께 오는 구조화
    `/api/tasks` 호출은 그대로 존중한다(`_is_orchestrator_chat_default`).
  - `search_meetings`의 `query`, `analyze_meeting`의 `meeting_id`를 사용자
    문장에서 채운다. `meeting_id`는 문장에 UUID가 있을 때만 사용하고
    추측으로 만들어내지 않는다.
  - 필수 payload가 비어 있으면 upstream 호출 전에 `400 INVALID_ARGUMENT`로
    거른다(기존에는 upstream이 `INTERNAL: unknown exception`으로 실패해
    원인이 드러나지 않았다).
- `app/a2a/runtime.py`
  - `_artifact_parts`: `markdown` 없이 `data`만 있는 Workflow 결과(현재
    `search_meetings`, `analyze_meeting`)에도 `text/plain` Part를 함께
    실었다. `text` 필드만 읽는 Client(Orchestrator의 `a2a_client.
    _extract_answer`)가 구조화 결과를 빈 응답으로 보는 문제의 근본 원인이었다.
    Workmate 공개 데이터 계약을 바꾸지 않고 Part를 하나 추가하는 하위 호환
    변경이다.

## 단위 테스트

| 대상 | 결과 |
| --- | --- |
| `tests/test_m51_legacy_adapter.py` (신규 5건 포함 9건) | PASS |
| `tests/test_contract.py` (신규 2건 포함) | PASS |
| `tests/` 전체 | 141 passed, 10 skipped, 0 failed |

## Compose E2E

Docker Desktop을 사용자가 직접 기동한 뒤 검증했다.

- 구성: `docker-compose.workmate-local.yml` + `docker-compose.smoke-8011.yml`
- 서비스: `main-agent`, `workmate-adapter`, `workmate-agent`, `postgres` 모두 기동/healthy
- 검증: `AI-agent_game_platform`의 `POST /api/chats/Workmate AI/reply`에 실제
  사용자 문장을 그대로 보내 응답을 확인했다.

| 시나리오 | 입력 | 결과 |
| --- | --- | --- |
| `daily_briefing` | "오늘 뭐부터 해야 해?" | PASS - HTTP 200, 실제 Task Fixture 반영 |
| `rank_priorities` | "오늘 우선순위 Top 3 알려줘" | PASS - HTTP 200 |
| `weekly_report` | "이번 주 업무 보고 만들어줘" | PASS - HTTP 200, Markdown 보고서 |
| `search_meetings` | "QA 빌드 일정은 어느 회의에서 결정됐어?" | PASS - HTTP 200, `runtime.py` 수정 전에는 응답이 비어 있었음 |
| `analyze_meeting` (UUID 포함) | "회의 00000000-0000-0000-0000-000000000101 분석해줘" | PASS - HTTP 200, `runtime.py` 수정 전에는 응답이 비어 있었음 |
| `analyze_meeting` (UUID 없음) | "지난 회의 요약해줘" | PASS - HTTP 400 `meeting_id` 필요 안내 (의도된 동작) |

- Secret·Token 로그 비노출: PASS (`docker logs`에서 `team5-test-token`,
  `sk-` 패턴 미검출)
- 검증 후 `docker compose down`으로 컨테이너 정리 완료

## 실행 조건

- 사용자 Fixture: `00000000-0000-0000-0000-000000000001`
- 회의 Fixture: `00000000-0000-0000-0000-000000000101`
- Workmate 호스트 포트: 임시 `8011:8001` override (기존 M5.3-04와 동일 우회)
- `EMBEDDING_API_KEY`/`OPENAI_API_KEY`는 세션 환경변수로만 주입, 파일·로그에
  저장하지 않았다.

## 알려진 한계

- `analyze_meeting`은 채팅 문장에 회의 UUID가 있어야 동작한다. 사용자가
  회의를 고르는 UI(회의 목록 클릭 → `meeting_id` 전달)는 이번 범위에
  포함하지 않았다.
- `user_id`는 어댑터가 고정 Fixture 값을 채운다. Orchestrator가 인증된
  사용자를 전달하지 않기 때문이며, `M51_ADAPTER_DEFAULT_USER_ID`로 바꿀 수
  있게만 해두었다.
- Orchestrator 프론트엔드(대시보드 패널, Task 목록 등)의 실데이터 연동은
  이번 범위에 포함하지 않았다.

## 승인

- latest_run_id: 20260814-201500
- latest_run_status: PASS
- reviewer: 사용자 승인 하에 자동 검증 명령 실행
