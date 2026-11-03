# W3 — Skill Subgraph 11개 재작성

> **이 문서는 요약과 색인이다.** 각 절의 상세는 아래 12개 문서에 있고, 두 문서가 충돌하면 상세
> 문서를 기준으로 한다.
>
> | 절 | 상세 문서 | 내용 |
> | --- | --- | --- |
> | §1 | [30-3-1](30-3-1-document-info.md) | 문서 정보·용어·대상 Skill 11개 |
> | §2 | [30-3-2](30-3-2-scope.md) | 목적과 범위, 분해 기준, 설계 원칙 4종 |
> | §3 | [30-3-3](30-3-3-entry-criteria.md) | 선행 조건, **부분 착수 규칙** |
> | §4 | [30-3-4](30-3-4-requirements.md) | 요구사항 W3-R1~R11 |
> | §5 | [30-3-5](30-3-5-design.md) | 설계 — Skill별 노드 분해, **숨은 부작용**, 결정 W3-D1~D5 |
> | §6 | [30-3-6](30-3-6-wbs.md) | 작업 분해 W3-T0~T9, `assistant_ask` 6분할 |
> | §7 | [30-3-7](30-3-7-verification.md) | 검증 설계 W3-V1~V11 |
> | §8 | [30-3-8](30-3-8-traceability.md) | 추적성 매트릭스, Skill×요구사항 |
> | §9 | [30-3-9](30-3-9-exit-criteria.md) | 완료 정의, Skill별 판정 |
> | §10 | [30-3-10](30-3-10-risks.md) | 위험 등록부 W3-K1~K10 |
> | §11 | [30-3-11](30-3-11-rollback.md) | 롤백·중단·재개, Skill 단위 롤백 |
> | §12 | [30-3-12](30-3-12-references.md) | 참조 자료와 읽을 지점 |
>
> **상세화 과정에서 추가된 것:** 요구사항 R10(숨은 부작용 보존)·R11(확인 흐름 동결), 검증
> V11(부작용 DB 직접 검증), 설계 결정 W3-D1~D5.

## 1. 문서 정보

| 항목 | 값 |
| --- | --- |
| 단계 | W3 |
| 상위 계획 | [30-langgraph-migration-plan.md](30-langgraph-migration-plan.md) §5 |
| 선행 단계 | [W2 Graph 골격](30-2-w2-graph-foundation.md) |
| 후행 단계 | [W4 Root Graph](30-4-w4-root-graph.md) |
| 상태 | 대기 |
| 비중 | **전체 전환에서 가장 큰 단계** (구현 약 2,600줄, 테스트 약 4,700줄 영향) |

## 2. 목적과 범위

### 2.1 목적

Skill별 단일 async 함수를 **노드로 분해한 Subgraph**로 재작성한다. 목표는 코드 이동이 아니라
"함수 안에 숨어 있던 중간 상태를 State로 드러내는 것"이다.

### 2.2 범위 내

- 공개 Skill 11개의 Subgraph 구현 (`app/graph/skills/`)
- Skill별 새 테스트 작성
- W1 스냅샷 대조

### 2.3 범위 외

- Root Graph 조립·라우팅 (W4)
- 진입점 교체 (W5) — W3 시점에는 아직 기존 Registry가 운영 경로다
- `interrupt` 도입 (W6) — `assistant_ask`의 확인 흐름은 W3에서 **기존 방식 그대로** 옮긴다
- `app/workflows/` 삭제 (W7)

### 2.4 W3의 설계 원칙

| 원칙 | 의미 |
| --- | --- |
| 노드는 한 가지 일만 한다 | I/O 노드와 계산 노드를 섞지 않는다 |
| 결정적 규칙은 Domain 함수에 남긴다 | 점수·날짜·중복·권한·근거 검증은 노드가 **호출**할 뿐 재구현하지 않는다 |
| 실패는 예외가 아니라 Edge다 | 부분 실패는 `warnings` 누적 후 다음 노드로 진행 |
| Subgraph는 자기 입력만 안다 | 다른 Skill을 직접 import하지 않는다(합성은 W4·W6의 책임) |

## 3. 선행 조건

| ID | 조건 | 확인 방법 |
| --- | --- | --- |
| W3-E1 | W1 스냅샷 전건 PASS | `tests.contracts.test_contract_snapshots` |
| W3-E2 | W2 검증 V1~V9 PASS | W2 증빙 |
| W3-E3 | W2-V6(LLM 구조화 출력 동등성) PASS | W2 증빙 — 미충족 시 LLM Skill 착수 금지 |

## 4. 요구사항

| ID | 구분 | 요구사항 | 출처 |
| --- | --- | --- | --- |
| W3-R1 | 기능 | 공개 Skill 11개 각각을 `StateGraph` Subgraph로 구현한다 | 96번 §2 |
| W3-R2 | 기능 | 각 Subgraph의 출력이 W1 스냅샷의 `expected`와 일치한다 | 계획서 §9-7 |
| W3-R3 | 제약 | 모든 조회에 요청된 `user_id` 범위를 적용하고 Soft Delete를 제외한다 | 96번 §11-3, `AGENTS.md` |
| W3-R4 | 제약 | 우선순위 점수·순위·근거 ID를 LLM이 생성·변경하지 않는다 | `AGENTS.md`, 96번 §11-4 |
| W3-R5 | 기능 | Provider 부분 실패 시 사용 가능한 결과와 `warnings`를 보존한다 | 96번 §11-6 |
| W3-R6 | 기능 | Daily Briefing의 소스 수집을 병렬 노드로 팬아웃/팬인한다 | 계획서 §2.1 |
| W3-R7 | 제약 | Subgraph가 다른 Skill 모듈을 직접 import하지 않는다 | §2.4 |
| W3-R8 | 제약 | 운영 경로에 Mock·고정 샘플 응답을 두지 않는다 | `AGENTS.md` 완료 규칙 |
| W3-R9 | 제약 | 공개 함수·노드에 한글 Docstring을 작성한다 | `AGENTS.md` 주석 규칙 |

## 5. 설계

### 5.1 이식 대상과 순서

의존성이 적고 결정적인 것부터, 복잡하고 의존이 많은 것을 뒤로 둔다.

| 순서 | Skill | 현재 위치 | 난이도 근거 |
| --- | --- | --- | --- |
| 1 | `rank_priorities` | [priority.py](../workmate-agent/app/workflows/priority.py) | LLM 없음, 결정적 계산 |
| 2 | `get_meeting_analysis` | [assistant_skills.py:174](../workmate-agent/app/workflows/assistant_skills.py#L174) | 단순 조회 |
| 3 | `review_action_items` | [assistant_skills.py:199](../workmate-agent/app/workflows/assistant_skills.py#L199) | 상태 변경, 확인 대상 |
| 4 | `review_proposal` | [assistant_skills.py:226](../workmate-agent/app/workflows/assistant_skills.py#L226) | 상태 변경, 확인 대상 |
| 5 | `manage_tasks` | [assistant_skills.py:293](../workmate-agent/app/workflows/assistant_skills.py#L293) | CRUD, 삭제는 확인 대상 |
| 6 | `read_email` | [assistant_skills.py:63](../workmate-agent/app/workflows/assistant_skills.py#L63) | Gmail 실시간 호출 |
| 7 | `daily_briefing` | [daily_briefing.py](../workmate-agent/app/workflows/daily_briefing.py) | 병렬 + 부분 실패 |
| 8 | `weekly_report` | [weekly_report.py](../workmate-agent/app/workflows/weekly_report.py) | LLM + 근거 검증 + 부분 결과 |
| 9 | `search_meetings` | [meetings.py:377](../workmate-agent/app/workflows/meetings.py#L377) | 하이브리드 검색 + 근거 판정 |
| 10 | `analyze_meeting` | [meetings.py:216](../workmate-agent/app/workflows/meetings.py#L216) | STT + LLM + 색인, 실패 격리 |
| 11 | `assistant_ask` | [assistant_router.py:771](../workmate-agent/app/workflows/assistant_router.py#L771) | 937줄, 나머지 10개 호출 |

### 5.2 노드 분해 설계

96번 §5·§6의 목표 구조를 그대로 따른다. 대표 세 가지만 옮겨 적는다.

**rank_priorities** (96번 §5.2)

```
START → load_incomplete_tasks → filter_user_and_soft_delete → calculate_deterministic_score
      → stable_sort_and_top3 → load_previous_snapshot → explain_rank_changes
      → save_priority_snapshot → build_priority_result → END
```

Gmail 노드를 갖지 않는다. 점수·순위·근거 ID는 [app/domain/priority.py](../workmate-agent/app/domain/priority.py)가
계속 소유한다(W3-R4).

**daily_briefing** (96번 §5.1) — 병렬 팬아웃의 표준 사례

```
START → calculate_date_range ─┬→ load_tasks ─────────┐
                              ├→ fetch_calendar ─────┤
                              ├→ fetch_gmail ────────┼→ normalize_and_deduplicate
                              └→ load_meeting_signals┘
      → calculate_priorities → compose_deterministic_summary → build_result → END
```

- Task 저장소 실패는 **전체 실패**, Gmail·Calendar 실패는 `warnings` 누적 후 계속(W3-R5).
- `compose_deterministic_summary`는 LLM 노드가 아니다 — 고정 템플릿 조합이다.
- 병렬 갱신이 충돌하지 않는 이유는 W2에서 정의한 `warnings`·`source_data` Reducer다.

**assistant_ask** (96번 §6) — W3에서는 확인 흐름을 기존 방식으로 유지

```
START → load_conversation_context → resolve_context_references → route_with_llm
      → {build_direct_reply | build_clarifying_question | validate_skill_and_arguments}
      → requires_confirmation? ─(예)→ build_pending_action_reply → END   ← W6에서 interrupt로 교체
                              └(아니오)→ call_selected_skill → phrase_answer → END
```

W3 시점에는 `pending_action`을 응답에 실어 보내는 **현재 동작을 그대로 재현**한다. W1 스냅샷과
대조해야 하기 때문이다. `interrupt`로 바꾸는 것은 W6의 일이며, 그때 스냅샷도 의도적으로 갱신한다.

> **코드 조사에서 나온 두 가지(2026-09-28):**
>
> 1. **`daily_briefing`에 숨은 부작용이 있다.** 내부에서 `rank_priorities` Workflow를 호출하며
>    ([daily_briefing.py:139, 238](../workmate-agent/app/workflows/daily_briefing.py#L139)), 그 과정에서
>    우선순위 Snapshot이 저장된다([priority.py:123](../workmate-agent/app/workflows/priority.py#L123)).
>    응답에 드러나지 않아 **스냅샷 대조로 검출되지 않는다.** 처리 방침은
>    [30-3-5](30-3-5-design.md) §3(결정 W3-D1: 부작용 유지), 검증은 W3-V11.
> 2. **보조 Skill 5종은 UI REST 함수를 호출하는 얇은 래퍼다.** 업무 로직이 `action_item_api`·
>    `proposal_api`·`task_api`(전부 W3 범위 밖)에 있으므로 3노드로 최소 분해한다(결정 W3-D4).

### 5.3 Subgraph 간 호출 규칙 (W3-R7)

현재 코드는 Workflow가 Workflow를 지연 import로 직접 호출한다
([assistant_router.py:881-891](../workmate-agent/app/workflows/assistant_router.py#L881-L891),
[daily_briefing.py:238](../workmate-agent/app/workflows/daily_briefing.py#L238)).

W3에서는 이 호출을 Subgraph가 직접 하지 않는다. 대신

- `daily_briefing`이 필요로 하는 우선순위 계산은 **Domain 함수 호출**로 바꾼다(원래 계산은 Domain에 있다).
- `assistant_ask`가 다른 Skill을 실행하는 것은 **W4에서 Root Graph가 주입한 Subgraph 핸들**을 통해서 한다.
  W3 단계에서는 주입 인터페이스만 정의하고, 실제 연결은 W4에서 완성한다.

### 5.4 State 스키마 불일치 처리

Skill마다 입력 모양이 다르다. 공통 State를 유지하되 Skill 입력은 `input` 하위 dict에 둔다.
Subgraph 전용 State를 따로 두는 방식은 채택하지 않는다 — 상위/하위 변환 코드가 Skill 수만큼 늘고
`warnings` 누적 경로가 끊긴다.

## 6. 작업 분해 (WBS)

| ID | 작업 | 선행 | 산출물 |
| --- | --- | --- | --- |
| W3-T0 | 노드 분해 설계 확정(11개 Skill의 노드 목록·Edge) | — | 설계 메모 |
| W3-T1 | `rank_priorities` Subgraph + 테스트 | W3-T0 | `skills/rank_priorities.py` |
| W3-T2 | 보조 Skill 5종(`get_meeting_analysis`·`review_action_items`·`review_proposal`·`manage_tasks`·`read_email`) | W3-T1 | `skills/assistant_skills/*` |
| W3-T3 | `daily_briefing` (병렬·부분 실패) | W3-T1 | `skills/daily_briefing.py` |
| W3-T4 | `weekly_report` (LLM·근거 검증) | W3-T3 | `skills/weekly_report.py` |
| W3-T5 | `search_meetings` | W3-T4 | `skills/search_meetings.py` |
| W3-T6 | `analyze_meeting` (STT·색인 실패 격리) | W3-T5 | `skills/analyze_meeting.py` |
| W3-T7 | `assistant_ask` (확인 흐름은 기존 방식 유지) | W3-T2~T6 | `skills/assistant_router.py` |
| W3-T8 | Skill별 스냅샷 대조 실행 | 각 Skill 완료 시마다 | 대조 로그 |
| W3-T9 | 증빙·커밋 | W3-T8 | `result.md` |

각 Skill 작업은 **완료 즉시 해당 스냅샷을 대조**한다(W3-T8을 마지막에 몰지 않는다). 11개를 다 만든 뒤
한꺼번에 대조하면 실패 원인 분리가 어렵다.

## 7. 검증 설계

| ID | 검증 항목 | 방법 | 판정 기준 |
| --- | --- | --- | --- |
| W3-V1 | 스냅샷 대조 | `tests.contracts.test_contract_snapshots` | 전건 PASS |
| W3-V2 | Skill별 단위 테스트 | Skill별 신규 테스트 | PASS |
| W3-V3 | `user_id` 범위 | 타 사용자 데이터 혼입 시나리오 | 결과에 미포함 |
| W3-V4 | 결정성 | 동일 입력 2회 실행 | 동일 출력 |
| W3-V5 | 부분 실패 | Gmail·Calendar 장애 주입 | 부분 결과 + `warnings` 보존 |
| W3-V6 | 병렬 정합성 | `daily_briefing` 병렬 노드 동시 경고 | 경고 누적, 유실 없음 |
| W3-V7 | LLM 책임 경계 | 점수·순위·근거 ID 생성 경로 검사 | LLM 경로 미개입 |
| W3-V8 | Mock 부재 | `mock=True` 반환 경로 검사 | 운영 Skill에 없음 |
| W3-V9 | Subgraph 독립성 | `skills/` 내부 import 검사 | Skill 간 직접 import 없음 |
| W3-V10 | 기존 테스트 | 전체 스위트 | 실패 0 |

## 8. 추적성 매트릭스

| 요구사항 | 작업 | 검증 |
| --- | --- | --- |
| W3-R1 | W3-T1~T7 | W3-V2 |
| W3-R2 | W3-T8 | W3-V1 |
| W3-R3 | W3-T1~T7 | W3-V3 |
| W3-R4 | W3-T1 | W3-V7 |
| W3-R5 | W3-T3, T4, T6 | W3-V5 |
| W3-R6 | W3-T3 | W3-V6 |
| W3-R7 | W3-T0, T7 | W3-V9 |
| W3-R8 | W3-T1~T7 | W3-V8 |
| W3-R9 | W3-T1~T7 | 코드 검토 |

## 9. 완료 정의 (Exit criteria)

1. 공개 Skill 11개 전부가 `app/graph/skills/` 아래 Subgraph로 존재한다.
2. W3-V1(스냅샷 대조)이 전건 PASS — `assistant_ask`의 확인 흐름 포함.
3. W3-V3·V5·V7이 PASS — 사용자 범위·부분 실패·LLM 책임 경계 불변식이 유지된다.
4. 기존 `app/workflows/`는 **아직 삭제하지 않았고**, 기존 테스트가 여전히 통과한다.

## 10. 위험과 완화

| 위험 | 영향 | 완화 |
| --- | --- | --- |
| `assistant_router.py` 937줄을 한 번에 옮기지 못한다 | W3이 무기한 지연 | 노드 단위로 쪼개 착수 — 먼저 `route_with_llm`, 다음 확인 분기, 마지막 결과 문장화. 순서는 96번 §6 |
| 노드 분해 중 중간 상태가 State에 안 실려 값이 유실된다 | 스냅샷 대조 실패 | Skill 완료 즉시 대조(W3-T8)로 조기 발견 |
| 병렬 노드가 같은 채널을 덮어써 경고가 사라진다 | 부분 실패 정보 손실 | W2 Reducer + W3-V6 |
| Domain 규칙을 노드에 재구현해 점수가 달라진다 | 결정성 위반, `AGENTS.md` 위배 | Domain 함수 호출만 허용. W3-V7로 확인 |
| Skill 간 직접 호출이 남아 순환 의존이 생긴다 | Subgraph 합성(W4) 불가 | W3-V9 import 검사 |

## 11. 롤백·중단 기준

- W3은 신규 파일 추가만 하므로(기존 `app/workflows/`는 건재) 롤백 비용이 낮다.
- **중단 기준:** 동일 Skill의 스냅샷 대조가 서로 다른 원인으로 3회 이상 실패하면 그 Skill의 노드 분해
  설계를 W3-T0으로 되돌려 재설계한다. 스냅샷 기대값을 고쳐서 통과시키지 않는다.

## 12. 참조

- [96-workmate-langgraph-target-architecture.md](96-workmate-langgraph-target-architecture.md) §5, §6, §11
- [30-1-w1-contract-snapshot.md](30-1-w1-contract-snapshot.md) — 수용 기준의 출처
- [`app/domain/`](../workmate-agent/app/domain/) — 결정적 규칙의 소유자
