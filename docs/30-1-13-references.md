# W1-13 — 참조 자료

> [30-1-w1-contract-snapshot.md](30-1-w1-contract-snapshot.md) §13의 상세 문서.

"무엇을 참조하는가"가 아니라 **"어디를 왜 읽는가"** 를 기록한다.

## 1. 설계 근거 문서

### 30-langgraph-migration-plan.md

| 절 | 읽는 이유 |
| --- | --- |
| §1-4 | "계약 스냅샷이 유일한 회귀 안전망이다" — W1의 존재 이유 |
| §4 D2 | 확정 결정(스냅샷 선추출) |
| §4 D1 | D1=B가 `test_contract.py`를 감시선에서 제외시킨 경위 |
| §5 W1 | 단계 정의와 시한 제약 |
| §9-7 | "스냅샷 대비 의도적 변경 외 차이 없음" — W9 완료 조건 |

### 96-workmate-langgraph-target-architecture.md

| 절 | 읽는 이유 |
| --- | --- |
| §11-6 | "Provider 일부 실패는 사용 가능한 결과와 `warnings`를 보존한다" — 부분 실패 케이스(W1-R4)의 근거 |
| §5.1~5.5 | Skill별 실패 경로 — 어떤 케이스를 만들어야 하는지의 단서 |

W1은 96번 문서를 **구현 기준이 아니라 케이스 선정 단서**로 쓴다. 스냅샷은 목표 설계가 아니라 현재
동작을 기록하기 때문이다.

## 2. 코드 참조 — 무엇을 측정하는가

### 2.1 측정 대상의 정의

| 위치 | 읽는 이유 |
| --- | --- |
| [registry.py:41-54](../workmate-agent/app/workflows/registry.py#L41) | `WorkflowResult` 8개 필드 — 스냅샷 `expected`의 스키마 |
| [registry.py:20-39](../workmate-agent/app/workflows/registry.py#L20) | `WorkflowRequest` — 케이스 `request`의 스키마 |
| [runtime.py:66-82](../workmate-agent/app/a2a/runtime.py#L66) | 공개 Skill 11개 — 커버리지 목표 |

### 2.2 비결정 값의 출처

정규화 규칙을 정하려면 어디서 비결정 값이 나오는지 알아야 한다.

| 위치 | 비결정 값 |
| --- | --- |
| [priority.py:109](../workmate-agent/app/workflows/priority.py#L109) | `calculated_at = datetime.now(timezone.utc)` |
| [priority.py:112](../workmate-agent/app/workflows/priority.py#L112) | `priority_snapshot_id = str(uuid4())` |
| [daily_briefing.py:145-149](../workmate-agent/app/workflows/daily_briefing.py#L145) | `as_of` 미지정 시 `datetime.now()` → 날짜 경계 |
| [daily_briefing.py:180](../workmate-agent/app/workflows/daily_briefing.py#L180) | `provider_freshness["email"] = now().isoformat()` |
| [runtime.py:249](../workmate-agent/app/a2a/runtime.py#L249) | `Artifact(artifact_id=str(uuid4()))` — W4 이후 관련 |

### 2.3 주입 지점 — 운영 코드를 안 고치고 Fake를 넣는 방법

| 위치 | 주입 파라미터 |
| --- | --- |
| [daily_briefing.py:132-136](../workmate-agent/app/workflows/daily_briefing.py#L132) | `provider_factory`, `repositories` |
| [meetings.py:216-220](../workmate-agent/app/workflows/meetings.py#L216) | `analyzer`, storage, stt |
| [meetings.py:377-381](../workmate-agent/app/workflows/meetings.py#L377) | `repository`, `embedding_provider`, `answer_service` |
| [weekly_report.py:223-228](../workmate-agent/app/workflows/weekly_report.py#L223) | `client`(LLM), `meeting_repository` |
| [priority.py:80-89](../workmate-agent/app/workflows/priority.py#L80) | `_repositories()` — 환경변수로 경로 지정 |

**이 지점들이 있어서 W1-R5(운영 코드 무수정)가 가능하다.** 없었다면 W1 자체가 어려웠을 것이다.

### 2.4 실사용 배경이 담긴 주석

케이스 우선순위를 정하는 단서다. 이 주석들이 가리키는 시나리오는 실제로 사용자를 막았던 경로다.

| 위치 | 배경 |
| --- | --- |
| [daily_briefing.py:176-180](../workmate-agent/app/workflows/daily_briefing.py#L176) | `category:primary` 필터 — 2026-08-16 프로모션 메일 혼입 |
| [daily_briefing.py:195-203](../workmate-agent/app/workflows/daily_briefing.py#L195) | 본문 보강 — 100건 전부 "읽지 않은 메일 신호"만 보이던 문제 |
| [daily_briefing.py:210-218](../workmate-agent/app/workflows/daily_briefing.py#L210) | LLM 관련성 판정 — 2026-08-17 광고 메일 노출 |
| [daily_briefing.py:299-306](../workmate-agent/app/workflows/daily_briefing.py#L299) | `data=` 누락으로 프론트가 `null`만 읽던 문제 |
| [assistant_router.py:282-292](../workmate-agent/app/workflows/assistant_router.py#L282) | DNS 간헐 실패 재시도 — 2026-08-19 |
| [priority.py:145-148](../workmate-agent/app/workflows/priority.py#L145) | `data=` 채우는 이유 |

## 3. 테스트 참조 — 시나리오의 출처

W1-T1에서 전수 조사할 대상이다. 각 파일에서 얻을 것을 적는다.

| 테스트 | 줄 | 얻을 것 |
| --- | --- | --- |
| [test_priority_workflow.py](../workmate-agent/tests/test_priority_workflow.py) | 88 | 사용자 격리, 2회 실행 `unchanged`, Schema 검증 |
| [test_daily_briefing.py](../workmate-agent/tests/test_daily_briefing.py) | 446 | **부분 실패 시나리오의 보고** — Gmail·Calendar 장애, 본문 보강 실패 |
| [test_assistant_router.py](../workmate-agent/tests/test_assistant_router.py) | 1,019 | 라우팅·확인·컨텍스트 해소·`confirmed_skill_id` 재요청 |
| [test_assistant_skills.py](../workmate-agent/tests/test_assistant_skills.py) | 314 | 보조 5종의 입력·출력 |
| [test_meeting_workflows.py](../workmate-agent/tests/test_meeting_workflows.py) | 313 | 분석·검색, 근거 검증 실패 |
| [test_weekly_report_generation.py](../workmate-agent/tests/test_weekly_report_generation.py) | 152 | 정상 요약 |
| [test_weekly_report_provider_failure.py](../workmate-agent/tests/test_weekly_report_provider_failure.py) | 104 | LLM 실패 시 부분 결과 |
| [test_weekly_source_link.py](../workmate-agent/tests/test_weekly_source_link.py) | 234 | `blocked` → `unresolved_issues` |
| [test_contract.py](../workmate-agent/tests/test_contract.py) | 399 | 공개 계약 검증 방식(Schema 검증 패턴) |

### 3.1 Fixture 자산

| 파일 | 내용 | W1에서의 용도 |
| --- | --- | --- |
| [work_domain.py](../workmate-agent/tests/fixtures/work_domain.py) | `task_fixture()`, `sync_state_fixture()`, `OWNER_USER_ID`, `OTHER_USER_ID`, `FIXTURE_TIME` | Task·동기화 Fixture. **사용자 격리 시나리오가 이미 이 값으로 작성돼 있다** |
| [fake_r2.py](../workmate-agent/tests/fixtures/fake_r2.py) | `FakeR2Storage` | `analyze_meeting` |
| [fake_realtime_stt.py](../workmate-agent/tests/fixtures/fake_realtime_stt.py) | `FakeRealtimeSttSession`, `fake_realtime_session_factory()` | `analyze_meeting` STT |

`work_domain.py`의 Docstring이 중요한 전례를 담고 있다.

> 운영 코드나 운영 DB 초기화에는 import하지 않는다. 모든 값은 계약 테스트의 사용자 격리·중복·Soft
> Delete 시나리오를 재현하기 위한 **비밀정보 없는 값**이다.

W1의 새 Fixture도 같은 규칙을 따른다(W1-R8).

## 4. 개발 규칙

### AGENTS.md

| 규칙 | W1에서의 적용 |
| --- | --- |
| API Key·Token·Presigned URL을 Git에 저장하지 않음 | W1-R8, W1-V7 |
| 실패한 테스트를 삭제하거나 우회하지 않음 | [30-1-11](30-1-11-rollback.md) §3.2 |
| 기대값 완화를 해결 방법으로 인정하지 않음 | W1-R9(기록 모드 보호) |
| 관련 없는 파일을 함께 정리하지 않음 | W1은 `tests/contracts/`만 건드린다 |
| 구현 결과가 생기기 전에 빈 `result.md`를 만들지 않음 | W1-T11 |
| 커밋 하나에 논리적 변경 하나 | [30-1-6](30-1-6-wbs.md) §2 커밋 분할 |

## 5. 선후 단계 문서

| 문서 | W1과의 관계 |
| --- | --- |
| [30-0](30-0-w0-baseline.md) | 기준 Commit `8043c1e`와 테스트 환경의 출처 |
| [30-0](30-0-w0-baseline.md) §10.1 | W0에서 커밋한 2건이 스냅샷 값에 영향 |
| [30-2-3](30-2-3-entry-criteria.md) | W2가 W1에 거는 조건(W2-E1) |
| [30-3-3](30-3-3-entry-criteria.md) | **W3이 W1에 거는 조건(W3-E1)** — 가장 강한 제약 |
| [30-3-5](30-3-5-design.md) §3 | 숨은 부작용 — 스냅샷이 못 잡는 항목 |
| [30-6](30-6-w6-interrupt-resume.md) | 의도적 변경의 대상 |
| [30-7](30-7-w7-legacy-removal.md) | **스냅샷 재작성 기한** |
| [30-9](30-9-w9-docs-evidence.md) §5.3 | diff 분류 — W1 자료가 근거 |

## 6. 외부 문서

| 자료 | 확인할 내용 |
| --- | --- |
| `unittest` 서브테스트 | 케이스별 독립 실패 보고(`subTest`) |
| `json` 직렬화 | `sort_keys=True`, `ensure_ascii=False` — 기존 구현과 동일하게 |
| `tempfile` | 케이스별 저장소 격리 |
| `unittest.mock.patch` | 주입 지점이 없는 경우의 Fake 삽입 |

**골든 파일 테스트(golden file / approval testing)** 개념이 W1의 방법론적 배경이다. 관련 자료를
참고하되, 이 프로젝트의 제약(정규화 금지 목록, 기록 모드 보호)이 우선한다.

## 7. 이 문서 묶음

| 문서 | 대응 절 |
| --- | --- |
| [30-1-1](30-1-1-document-info.md) | §1 문서 정보·용어·시한 제약 |
| [30-1-2](30-1-2-scope.md) | §2 목적, 문제 정의, 범위, 보장하지 않는 것 |
| [30-1-3](30-1-3-entry-criteria.md) | §3 선행 조건, Skill별 준비물 |
| [30-1-4](30-1-4-requirements.md) | §4 요구사항 W1-R1~R10 |
| [30-1-5](30-1-5-design.md) | §5 설계 — 스키마, 하네스, 정규화, 결정 W1-D1~D5 |
| [30-1-6](30-1-6-wbs.md) | §6 작업 분해 W1-T1~T11 |
| [30-1-7](30-1-7-verification.md) | §7 검증 설계 W1-V1~V9 |
| [30-1-8](30-1-8-traceability.md) | §8 추적성, 케이스×Skill 매트릭스 |
| [30-1-9](30-1-9-exit-criteria.md) | §9 완료 정의, 조건부 완료 |
| [30-1-10](30-1-10-risks.md) | §10 위험 등록부 W1-K1~K9 |
| [30-1-11](30-1-11-rollback.md) | §11 롤백·중단·재개, 재작성 기한 |
| [30-1-12](30-1-12-handoff.md) | §12 후행 단계에 넘기는 것 |
| [30-1-13](30-1-13-references.md) | §13 참조 (이 문서) |
