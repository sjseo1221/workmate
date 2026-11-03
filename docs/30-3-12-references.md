# W3-12 — 참조 자료

> [30-3-w3-skill-subgraphs.md](30-3-w3-skill-subgraphs.md) §12의 상세 문서.

"무엇을 참조하는가"가 아니라 **"어디를 왜 읽는가"** 를 기록한다.

## 1. 설계 근거 문서

### 96-workmate-langgraph-target-architecture.md

W3 노드 분해의 1차 출처다. **§5와 §6이 W3의 설계도**다.

| 절 | 읽는 이유 | 대응 Skill |
| --- | --- | --- |
| §5.1 Daily Briefing | 병렬 팬아웃/팬인 구조, Warning Edge | `daily_briefing` |
| §5.2 Priority | 노드 순서, Gmail 노드 없음, LLM 미개입 | `rank_priorities` |
| §5.3 Weekly Report | LLM과 Domain의 책임 분리, 부분 결과 | `weekly_report` |
| §5.4 Meeting Analysis | 근거 검증 → 저장 순서, 색인 실패 격리 | `analyze_meeting` |
| §5.5 Meeting Search | 근거 부족이 정상 완료 Edge인 것 | `search_meetings` |
| §6 Assistant Router | 노드 구성과 확인 흐름 시퀀스 | `assistant_ask` |
| §11 불변식 | 식별자 보존(2), `user_id` 범위(3), 결정적 규칙(4·5), 부분 실패(6), interrupt 이전 상태 불변(7) | 전체 |

**주의** 96번은 가정형 목표다. W3 구현과 다르면 **구현에 맞춰 문서를 고친다**(W9). 단 §11 불변식은
설계 원칙이므로 구현을 맞춘다.

### 30-langgraph-migration-plan.md

| 절 | 읽는 이유 |
| --- | --- |
| §1-2 | "호환보다 구조 정합성 우선" — 단, W3은 **동작을 바꾸지 않는 단계**라는 점과 함께 읽는다 |
| §1-6 | 결정적 규칙의 소유권 |
| §2.1 | 교체 대상 표 — Skill 12개, 지연 import 재귀 |
| §5 W3 | 단계 정의 |

### 30-1-w1-contract-snapshot.md

W3의 수용 기준이 여기서 온다.

| 절 | 읽는 이유 |
| --- | --- |
| §5.2 | 스냅샷 스키마 — `expected` 8개 필드가 대조 대상 |
| §5.4 | 정규화 규칙 — 무엇이 비교되지 않는지 |
| §5.5 | **한계** — LLM Fake 기준이므로 프롬프트·모델 응답 변화는 못 잡는다 |
| §11 | 중단 기준 — 스냅샷을 못 만든 Skill의 처리 |

## 2. 코드 참조 — Skill별

### 2.1 `rank_priorities`

| 위치 | 읽는 이유 |
| --- | --- |
| [priority.py:90-158](../workmate-agent/app/workflows/priority.py#L90) | `execute()` 전체 흐름 |
| [priority.py:100](../workmate-agent/app/workflows/priority.py#L100) | `load_previous_snapshot`이 저장보다 먼저인 이유 |
| [priority.py:123](../workmate-agent/app/workflows/priority.py#L123) | `save_all()` — 숨은 부작용의 근원 |
| [priority.py:48-79](../workmate-agent/app/workflows/priority.py#L48) | `_changes()` 변화 판정 |
| [app/domain/priority.py](../workmate-agent/app/domain/priority.py) | `rank_tasks()` — 점수의 소유자. **재구현 금지** |

### 2.2 `daily_briefing`

| 위치 | 읽는 이유 |
| --- | --- |
| [daily_briefing.py:141-190](../workmate-agent/app/workflows/daily_briefing.py#L141) | 날짜 경계 계산, Gmail 조회와 첫 번째 실패 정책 |
| [daily_briefing.py:195-208](../workmate-agent/app/workflows/daily_briefing.py#L195) | 메일 본문 보강 — **병렬 + 조용한 실패 무시**. 주석에 배경 |
| [daily_briefing.py:210-235](../workmate-agent/app/workflows/daily_briefing.py#L210) | LLM 관련성 판정 — 실패 시 전부 통과 |
| [daily_briefing.py:236-248](../workmate-agent/app/workflows/daily_briefing.py#L236) | Calendar 조회 |
| [daily_briefing.py:139, 238](../workmate-agent/app/workflows/daily_briefing.py#L139) | **`rank_priorities` Workflow 호출** — W3-D1의 대상 |
| [daily_briefing.py:254-262](../workmate-agent/app/workflows/daily_briefing.py#L254) | 등록된 Task 대조 규칙 |
| [daily_briefing.py:288-296](../workmate-agent/app/workflows/daily_briefing.py#L288) | `summary` 고정 템플릿, `source_refs` 중복 제거 |
| [daily_briefing.py:118](../workmate-agent/app/workflows/daily_briefing.py#L118) | `_warning()` — `WarningState` 구조의 원본 |

**주석을 반드시 읽는다.** 이 파일의 주석은 2026-08-15~17 실사용 중 발견된 문제의 기록이다. 주석이
설명하는 동작을 바꾸면 그때 고친 문제가 재발한다.

### 2.3 `weekly_report`

| 위치 | 읽는 이유 |
| --- | --- |
| [weekly_report.py:223-295](../workmate-agent/app/workflows/weekly_report.py#L223) | 전체 흐름. **빌더가 아니라 핸들러 자체** |
| [weekly_report.py:55-80](../workmate-agent/app/workflows/weekly_report.py#L55) | `_call_llm_with_retry` — **2회, 429·5xx 포함**. `assistant_router`와 다른 정책 |
| [weekly_report.py:82-125](../workmate-agent/app/workflows/weekly_report.py#L82) | `validate_next_week_plans` — 근거 검증 |
| [weekly_classification.py](../workmate-agent/app/workflows/weekly_classification.py) | 분류·링크 Domain 함수. W7에서 `app/domain/`으로 이동 |

### 2.4 `analyze_meeting` / `search_meetings`

| 위치 | 읽는 이유 |
| --- | --- |
| [meetings.py:216-320](../workmate-agent/app/workflows/meetings.py#L216) | 분석 흐름, 근거 검증 → 저장 순서 |
| [meetings.py:330-367](../workmate-agent/app/workflows/meetings.py#L330) | `_transcribe_source_audio` — STT 경로 |
| [meetings.py:159-215](../workmate-agent/app/workflows/meetings.py#L159) | `_index_meeting_chunks` — 실패 격리 |
| [meetings.py:377-467](../workmate-agent/app/workflows/meetings.py#L377) | 검색 흐름, RRF 중복 제거 |
| [meetings.py:444-453](../workmate-agent/app/workflows/meetings.py#L444) | warning 분류 — `grounded` 여부로 갈림(커밋 `8043c1e`) |
| [meeting_answer.py](../workmate-agent/app/meeting_answer.py) | LLM 답변 + 근거 나열 폴백 |

### 2.5 보조 Skill 5종

| 위치 | 읽는 이유 |
| --- | --- |
| [assistant_skills.py:63-173](../workmate-agent/app/workflows/assistant_skills.py#L63) | `read_email` |
| [assistant_skills.py:174-198](../workmate-agent/app/workflows/assistant_skills.py#L174) | `get_meeting_analysis` |
| [assistant_skills.py:199-225](../workmate-agent/app/workflows/assistant_skills.py#L199) | `review_action_items` — `action_item_api` 호출 |
| [assistant_skills.py:226-292](../workmate-agent/app/workflows/assistant_skills.py#L226) | `review_proposal` — `proposal_api._review()` 호출 |
| [assistant_skills.py:293-387](../workmate-agent/app/workflows/assistant_skills.py#L293) | `manage_tasks` — 4분기, `task_api` 호출 |

**공통 패턴:** 전부 지연 import로 REST 모듈 함수를 호출한다. 그 모듈들은 **W3 범위 밖**이다.

### 2.6 `assistant_ask`

| 위치 | 읽는 이유 |
| --- | --- |
| [assistant_router.py:771-916](../workmate-agent/app/workflows/assistant_router.py#L771) | `assistant_ask_workflow()` 전체 |
| [assistant_router.py:221-243](../workmate-agent/app/workflows/assistant_router.py#L221) | **`_requires_confirmation()`** — 확인 대상 4종. 변경 금지 |
| [assistant_router.py:632-699](../workmate-agent/app/workflows/assistant_router.py#L632) | `route()` — LLM 라우팅 |
| [assistant_router.py:700-747](../workmate-agent/app/workflows/assistant_router.py#L700) | `phrase_answer()` — 결과 문장화 |
| [assistant_router.py:525-597](../workmate-agent/app/workflows/assistant_router.py#L525) | `_resolve_context_reference()` — "그 회의", "2번" 해소 |
| [assistant_router.py:794-816](../workmate-agent/app/workflows/assistant_router.py#L794) | `confirmed_skill_id` 재요청 경로 |
| [assistant_router.py:869-876](../workmate-agent/app/workflows/assistant_router.py#L869) | `pending_action` 반환 — W6 교체 대상 |
| [assistant_router.py:881-891](../workmate-agent/app/workflows/assistant_router.py#L881) | Registry 재호출 — W3-D2로 대체 |
| [assistant_router.py:917-940](../workmate-agent/app/workflows/assistant_router.py#L917) | `_offer_to_add_action_items_as_tasks()` |

## 3. 테스트 참조

기존 테스트는 **시나리오의 출처**다. W1 케이스 선정과 W3 단위 테스트 설계에 재사용한다.

| 테스트 | 읽는 이유 |
| --- | --- |
| [test_priority_workflow.py](../workmate-agent/tests/test_priority_workflow.py) | 사용자 범위·결정성·Snapshot 변화·Schema 검증 패턴 |
| [test_daily_briefing.py](../workmate-agent/tests/test_daily_briefing.py) | 부분 실패 시나리오의 전거 |
| [test_assistant_router.py](../workmate-agent/tests/test_assistant_router.py) | 1,019줄. 라우팅·확인·컨텍스트 해소 케이스 |
| [test_meeting_workflows.py](../workmate-agent/tests/test_meeting_workflows.py) | 분석·검색 시나리오 |
| [test_weekly_report_provider_failure.py](../workmate-agent/tests/test_weekly_report_provider_failure.py) | LLM 실패 시 부분 결과 |
| [test_weekly_source_link.py](../workmate-agent/tests/test_weekly_source_link.py) | `blocked` → `unresolved_issues` 규칙 |
| [tests/fixtures/](../workmate-agent/tests/fixtures/) | Fake Adapter·STT·R2 — W3 테스트에서 재사용 |

## 4. 개발 규칙

### AGENTS.md

| 규칙 | W3에서의 적용 |
| --- | --- |
| 모든 조회에 `user_id` 조건 적용 | W3-R3, W3-V3 |
| 우선순위 점수는 결정적으로 계산 | W3-R4 |
| LLM이 Task 순위·근거 ID를 만들지 않음 | W3-R4, W3-V7 |
| 외부 Provider 장애 시 부분 결과와 `warnings` | W3-R5 |
| 운영 경로에 Mock 금지 | W3-R8, W3-V8 |
| FastAPI Route에 업무 규칙 금지 | 보조 Skill이 호출하는 REST 모듈은 범위 밖이지만 원칙은 유지 |
| 공개 함수에 한글 Docstring | W3-R9 |
| 실패한 테스트 삭제·우회 금지 | [30-3-11](30-3-11-rollback.md) §3.2 |
| 기존 Schema·API 계약 임의 변경 금지 | W3은 응답 모양을 바꾸지 않는다 |

## 5. 선후 단계 문서

| 문서 | W3과의 관계 |
| --- | --- |
| [30-1](30-1-w1-contract-snapshot.md) | 수용 기준의 출처. W3-E1 |
| [30-2](30-2-w2-graph-foundation.md) | State·어댑터·LLM 경계 제공. W3-E2·E3 |
| [30-2-5](30-2-5-design.md) §5.2 | **재시도 정책 불일치** — `weekly_report` 이식 시 주의 |
| [30-2-5](30-2-5-design.md) §5.3 | `email_action_items` 교체 제외 — `daily_briefing`이 그대로 호출 |
| [30-4](30-4-w4-root-graph.md) | Subgraph 합성. W3-R7이 전제 |
| [30-6](30-6-w6-interrupt-resume.md) | `build_pending_action_reply` 노드 교체 |
| [30-8](30-8-w8-retry-observability.md) | 부작용 노드 목록·실패 파급 규칙표를 전달받음 |
| [30-9](30-9-w9-docs-evidence.md) | W3에서 발견한 사실을 상위 문서에 반영 |

## 6. 외부 문서

| 자료 | 확인할 내용 |
| --- | --- |
| LangGraph — Subgraph | 상위/하위 State 공유 규칙, 컴파일된 Graph를 노드로 사용하는 방법 |
| LangGraph — 병렬 실행 | superstep, 팬아웃/팬인, 동시 갱신과 Reducer |
| LangGraph — 조건부 Edge | `add_conditional_edges`와 path map (`manage_tasks` 4분기) |

## 7. 이 문서 묶음

| 문서 | 대응 절 |
| --- | --- |
| [30-3-1](30-3-1-document-info.md) | §1 문서 정보·용어·대상 Skill 목록 |
| [30-3-2](30-3-2-scope.md) | §2 목적과 범위, 분해 기준, 설계 원칙 4종 |
| [30-3-3](30-3-3-entry-criteria.md) | §3 선행 조건, 부분 착수 규칙 |
| [30-3-4](30-3-4-requirements.md) | §4 요구사항 W3-R1~R11 |
| [30-3-5](30-3-5-design.md) | §5 설계 — 노드 분해, 숨은 부작용, 설계 결정 W3-D1~D5 |
| [30-3-6](30-3-6-wbs.md) | §6 작업 분해 W3-T0~T9 |
| [30-3-7](30-3-7-verification.md) | §7 검증 설계 W3-V1~V11 |
| [30-3-8](30-3-8-traceability.md) | §8 추적성 매트릭스, Skill×요구사항 |
| [30-3-9](30-3-9-exit-criteria.md) | §9 완료 정의, Skill별 판정 |
| [30-3-10](30-3-10-risks.md) | §10 위험 등록부 W3-K1~K10 |
| [30-3-11](30-3-11-rollback.md) | §11 롤백·중단·재개 |
| [30-3-12](30-3-12-references.md) | §12 참조 (이 문서) |
