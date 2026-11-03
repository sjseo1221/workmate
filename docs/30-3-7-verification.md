# W3-7 — 검증 설계

> [30-3-w3-skill-subgraphs.md](30-3-w3-skill-subgraphs.md) §7의 상세 문서.

## 1. 검증 목록

| ID | 검증 항목 | 대상 요구사항 | 방법 | 판정 기준 |
| --- | --- | --- | --- | --- |
| W3-V1 | 스냅샷 대조 | W3-R2, R11 | 계약 스냅샷 | 전건 PASS |
| W3-V2 | Skill별 단위 테스트 | W3-R1 | 신규 테스트 | PASS |
| W3-V3 | `user_id` 범위 | W3-R3 | 혼입 시나리오 | 타 사용자 데이터 미포함 |
| W3-V4 | 결정성 | W3-R2 | 2회 실행 | 동일 출력 |
| W3-V5 | 부분 실패 | W3-R5 | 장애 주입 | 부분 결과 + `warnings` |
| W3-V6 | 병렬 정합성 | W3-R6 | 동시 경고 | 누적, 유실 없음 |
| W3-V7 | LLM 책임 경계 | W3-R4 | 경로 검사 | LLM 미개입 |
| W3-V8 | Mock 부재 | W3-R8 | 결과 검사 | `mock=True` 없음 |
| W3-V9 | Subgraph 독립성 | W3-R7 | import 검사 | Skill 간 직접 import 없음 |
| W3-V10 | 기존 테스트 | 전체 | 회귀 실행 | 실패 0 |
| W3-V11 | **숨은 부작용** | W3-R10 | DB 직접 검증 | 부작용 유지 확인 |

## 2. 검증 케이스 상세

### W3-V1 — 스냅샷 대조

Skill별로 수행한다. 대조 대상은 `WorkflowResult` 8개 필드 전부다.

| Skill | 케이스 | 특히 확인할 것 |
| --- | --- | --- |
| `rank_priorities` | basic, second_run_unchanged, empty_tasks | `changes[].change_type`, `score_breakdown` 5개 하위 필드 |
| `daily_briefing` | all_sources_ok, gmail_unavailable, calendar_unavailable | `warnings` 내용·순서, `summary` 문자열, `source_refs` 중복 제거 |
| `weekly_report` | llm_ok, provider_failure | 분류 4종, `PLAN_CANDIDATE_REJECTED` 경고 |
| `analyze_meeting` | transcript_present, missing_source | 색인 실패 시 경고만 남고 분석은 유지 |
| `search_meetings` | grounded, insufficient_evidence | warning의 `code`·`retryable`이 `grounded`에 따라 갈리는지 |
| 보조 5종 | 각 1~2건 | `text`·`markdown` 문자열 포맷 |
| `assistant_ask` | direct_reply, routes_to_skill, requires_confirmation | **`pending_action` 구조가 그대로인지**(W3-R11) |

**차이 처리 순서**

```
1. 이식 오류        → 구현 수정
2. 정규화 누락      → W1 정규화 보완, 이유 기록
3. 의도적 변경      → W3에서는 원칙적으로 없어야 한다. 있으면 증빙 기록 + 보고
```

**금지:** 스냅샷 기대값을 새 구현에 맞춰 수정(`AGENTS.md` 기대값 완화 금지).

### W3-V2 — Skill별 단위 테스트

스냅샷이 "결과 전체"를 보는 반면, 단위 테스트는 **노드 단위 동작**을 본다.

| 대상 | 케이스 예 |
| --- | --- |
| 개별 노드 | 입력 State → 출력 부분 갱신이 기대대로인가 |
| Edge 조건 | `manage_tasks`의 `action` 4분기가 올바른 노드로 가는가 |
| 노드 순서 | `rank_priorities`에서 `load_previous_snapshot`이 `save_snapshot`보다 먼저 실행되는가 |
| 오류 전파 | `ValueError`가 삼켜지지 않고 올라오는가(422 매핑 유지) |

### W3-V3 — `user_id` 범위 (보안)

**모든 Skill에 대해 수행한다.** 예외 없다.

| 케이스 | 방법 | 기대 |
| --- | --- | --- |
| V3-1 | 타 사용자 Task·Meeting을 섞은 Fixture | 결과에 미포함 |
| V3-2 | Soft Delete된 데이터 포함 | 결과에 미포함 |
| V3-3 | 조회 노드가 `state["user_id"]`를 쓰는지 코드 검사 | 하드코딩 없음 |
| V3-4 | `assistant_ask`가 하위 Skill에 `user_id`를 전달하는지 | 전달됨 |

**V3-4가 중요하다.** Meta Skill이 하위 Skill을 호출할 때 `user_id`를 누락하면 권한 범위가 사라진다.

### W3-V4 — 결정성

| 케이스 | 방법 | 기대 |
| --- | --- | --- |
| V4-1 | 같은 입력으로 2회 실행 | 정규화 필드 제외 동일 |
| V4-2 | 병렬 노드가 있는 `daily_briefing` | 실행 순서와 무관하게 동일 결과 |

**V4-2 주의:** 병렬 노드의 경고 **순서**는 보장되지 않는다. 스냅샷 대조 시 `warnings`를 순서 비의존
비교로 다룰지 결정해야 한다(W1 정규화 규칙과 연동).

### W3-V5 — 부분 실패

[30-3-5](30-3-5-design.md) §7의 실패 파급 규칙표를 그대로 검증한다.

| Skill | 주입 | 기대 |
| --- | --- | --- |
| `daily_briefing` | Gmail 장애 | 일정·우선순위는 정상, `GOOGLE_PROVIDER_UNAVAILABLE` 경고 |
| `daily_briefing` | Calendar 장애 | 메일·우선순위 정상 + 경고 |
| `daily_briefing` | **Gmail·Calendar 동시 장애** | 우선순위만 + **경고 2건** |
| `daily_briefing` | 메일 본문 보강 실패 | **경고 없음**, 자리표시자로 폴백 |
| `daily_briefing` | LLM 관련성 판정 실패 | **경고 없음**, 모든 메일 통과 |
| `daily_briefing` | Task 저장소 장애 | **전체 실패** |
| `weekly_report` | LLM 실패 | 부분 결과 + `LLM_PROVIDER_UNAVAILABLE` |
| `analyze_meeting` | 색인 실패 | 분석 결과 유지 + 재시도 가능 경고 |
| `analyze_meeting` | 근거 검증 실패 | **전체 실패, 저장되지 않음** |
| `search_meetings` | LLM 실패 | 근거 나열 답변 + `LLM_PROVIDER_UNAVAILABLE` |
| `search_meetings` | 회의 날짜 누락 | **전체 실패** |

**"경고 없음" 케이스가 특히 중요하다.** 개선 의도로 경고를 추가하면 스냅샷이 깨진다.

### W3-V6 — 병렬 정합성

| 케이스 | 방법 | 기대 |
| --- | --- | --- |
| V6-1 | Gmail·Calendar 동시 실패 | 경고 2건 모두 보존 |
| V6-2 | 세 소스 정상 | 결과가 순차 실행과 동일 |
| V6-3 | 실행 시간 | 순차 대비 단축(느슨한 확인) |

V6-1이 W2 Reducer의 첫 실전 검증이다. Reducer가 없으면 `InvalidUpdateError`로 실행 자체가 실패한다.

### W3-V7 — LLM 책임 경계

| 케이스 | 방법 | 기대 |
| --- | --- | --- |
| V7-1 | `rank_priorities` Subgraph의 노드 목록 검사 | LLM 노드 없음 |
| V7-2 | 점수 계산 경로 검사 | `rank_tasks()` Domain 호출만 |
| V7-3 | `weekly_report`에서 LLM 응답을 조작해 분류를 바꾸려 시도 | 분류·`source_refs`가 LLM 응답에 영향받지 않음 |
| V7-4 | `search_meetings`의 근거 ID 출처 | 검색 결과에서 옴, LLM 생성 아님 |

**V7-3의 방법:** LLM Fake가 분류 필드를 포함한 응답을 반환해도 결과의 분류가 바뀌지 않아야 한다.

### W3-V8 — Mock 부재

| 케이스 | 방법 | 기대 |
| --- | --- | --- |
| V8-1 | 11개 Skill 결과의 `mock` 필드 | 전부 `False` |
| V8-2 | `app/graph/skills/` 내 고정 샘플 반환 검사 | 없음 |

### W3-V9 — Subgraph 독립성

```
grep -rn "from app.graph.skills" app/graph/skills/
```

기대: 출력 없음(Skill 간 직접 import 없음). `assistant_ask`의 하위 Skill 실행은 주입 핸들을 통한다.

### W3-V10 — 기존 테스트

```
WORKMATE_TEST_DATABASE_URL="postgresql://postgres:postgres@127.0.0.1:55432/workmate_test" \
  uv run python -m unittest discover -s tests -v
```

| 항목 | 기대 |
| --- | --- |
| 기존 440건 | 전부 통과 — **W3 시점에도 `app/workflows/`는 살아 있다** |
| W1 스냅샷 | 전건 PASS |
| W2·W3 신규 | 전부 통과 |
| SKIP | 0 |

### W3-V11 — 숨은 부작용 (전용 검증)

스냅샷으로 검출되지 않는 항목이므로 별도로 확인한다.

| 케이스 | 방법 | 기대 |
| --- | --- | --- |
| V11-1 | `daily_briefing` 실행 후 우선순위 Snapshot 테이블 조회 | **행이 생성됨**(W3-D1: 부작용 유지) |
| V11-2 | `daily_briefing` 2회 실행 후 `rank_priorities` 호출 | `changes`가 부작용을 반영 |
| V11-3 | `analyze_meeting` 근거 검증 실패 시 저장소 조회 | 분석·후보가 저장되지 않음 |
| V11-4 | `assistant_ask`의 확인 대기 상태에서 저장소 조회 | 외부 상태 변경 없음(96번 §11-7) |

**V11-4는 W6의 선행 확인이기도 하다.** W3의 `build_pending_action_reply` 경로에서 이미 외부 상태가
바뀌고 있다면, W6에서 `interrupt`로 바꿔도 불변식이 깨진 채로 남는다.

## 3. 검증 실행 순서

```
Skill 하나 완료마다:
  1. W3-V2  노드 단위 테스트
  2. W3-V1  해당 Skill 스냅샷 대조
  3. W3-V3  user_id 범위
  4. W3-V4  결정성

daily_briefing 완료 시 추가:
  5. W3-V5, V6, V11

전체 완료 시:
  6. W3-V7, V8, V9
  7. W3-V10 전체 회귀
```

## 4. 판정 규칙

- 검증은 **PASS / FAIL** 두 값. Skill 단위로 판정한다
- 한 Skill이 FAIL이면 그 Skill만 미완료이며, 다른 Skill은 계속 진행할 수 있다 — 단
  `assistant_ask`는 하위 Skill이 전부 PASS여야 착수 가능
- W3-V3(보안)·W3-V11(부작용)은 **Skill 하나라도 FAIL이면 W3 전체를 미완료**로 본다

## 5. 참조

- [30-3-4](30-3-4-requirements.md) — 검증 대상 요구사항
- [30-3-5](30-3-5-design.md) §7 — 실패 파급 규칙표
- [30-1](30-1-w1-contract-snapshot.md) — 스냅샷 구조
