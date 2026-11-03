# W1 — 계약 스냅샷 추출

> **이 문서는 요약과 색인이다.** 각 절의 상세는 아래 13개 문서에 있고, 충돌 시 상세 문서를 기준으로
> 한다.
>
> | 절 | 상세 문서 | 내용 |
> | --- | --- | --- |
> | §1 | [30-1-1](30-1-1-document-info.md) | 문서 정보·용어·**시한 제약** |
> | §2 | [30-1-2](30-1-2-scope.md) | 목적, 부분 단언의 빈틈, **보장하지 않는 것 6종** |
> | §3 | [30-1-3](30-1-3-entry-criteria.md) | 선행 조건, Skill별 준비물 |
> | §4 | [30-1-4](30-1-4-requirements.md) | 요구사항 W1-R1~R10 |
> | §5 | [30-1-5](30-1-5-design.md) | 설계 — 스키마, 하네스, 정규화 금지 목록, 결정 W1-D1~D5 |
> | §6 | [30-1-6](30-1-6-wbs.md) | 작업 분해 W1-T1~T11 |
> | §7 | [30-1-7](30-1-7-verification.md) | 검증 설계 W1-V1~V9 |
> | §8 | [30-1-8](30-1-8-traceability.md) | 추적성, 케이스×Skill 매트릭스 |
> | §9 | [30-1-9](30-1-9-exit-criteria.md) | 완료 정의, **조건부 완료** |
> | §10 | [30-1-10](30-1-10-risks.md) | 위험 등록부 W1-K1~K9 |
> | §11 | [30-1-11](30-1-11-rollback.md) | 롤백·중단·재개, **재작성 기한** |
> | §12 | [30-1-12](30-1-12-handoff.md) | 후행 단계에 넘기는 것 |
> | §13 | [30-1-13](30-1-13-references.md) | 참조 자료와 읽을 지점 |
>
> **상세화에서 추가된 것:** 요구사항 R9(기록 모드 보호)·R10(현재 동작 그대로 기록), 검증 V8(정규화
> 목록 완전성)·V9(기록 모드 보호), 설계 결정 W1-D1~D5, 정규화 **금지 목록**.

## 1. 문서 정보

| 항목 | 값 |
| --- | --- |
| 단계 | W1 |
| 상위 계획 | [30-langgraph-migration-plan.md](30-langgraph-migration-plan.md) §5 |
| 선행 단계 | [W0 기준선](30-0-w0-baseline.md) — 완료 |
| 후행 단계 | [W2 Graph 골격](30-2-w2-graph-foundation.md) |
| 상태 | 대기 |
| 시한 제약 | **옛 구현이 살아 있는 동안에만 수행 가능.** W3 착수 전 반드시 완료 |

## 2. 목적과 범위

### 2.1 목적

전환 후 결과가 전환 전과 같은지 판정할 **기계 판독 가능한 기준(oracle)** 을 만든다.

D1=B로 공개 계약이 바뀌므로 `test_contract.py`를 "기대값 무변경 감시선"으로 쓸 수 없고, 구현과 테스트를
동시에 재작성하므로 기존 테스트도 안전망이 되지 못한다. 스냅샷이 유일한 회귀 감지 수단이다.

### 2.2 문제 정의

현재 테스트는 **부분 단언(partial assertion)** 만 한다. 예: [test_priority_workflow.py:41-44](../workmate-agent/tests/test_priority_workflow.py#L41-L44)는
`priorities`의 `task_id` 목록, `source_refs`, `changes[0].change_type`만 확인한다. 점수 값, 근거 문자열,
`calculated_at` 포맷, `artifact_name`, `markdown` 본문은 검증되지 않는다. 새 구현이 이들을 바꿔도
기존·신규 테스트 모두 통과할 수 있다.

### 2.3 범위 내

- 스냅샷 하네스(기록 모드 / 대조 모드) 구현
- Skill 11개의 대표 시나리오 스냅샷 생성
- 비결정 값 정규화 규칙 정의와 구현

### 2.4 범위 외

- `app/` 아래 운영 코드 수정 (W1은 읽기 전용 측정이다)
- 기존 테스트 수정·삭제
- 실제 외부 Provider(Gmail·Calendar·OpenAI·STT) 호출

## 3. 선행 조건

| ID | 조건 | 확인 방법 |
| --- | --- | --- |
| W1-E1 | W0 완료, 기준 Commit 고정 | `git log -1` = `8043c1e`, 트리 clean |
| W1-E2 | 전체 테스트 440 passed / 0 skipped | W0 증빙 |
| W1-E3 | 테스트 DB 기동 | `docker ps`에 `workmate-test-pg` |

## 4. 요구사항

| ID | 구분 | 요구사항 | 출처 |
| --- | --- | --- | --- |
| W1-R1 | 기능 | Skill별 `(fixture, request) → WorkflowResult` 전체를 JSON으로 저장한다 | 계획서 §1-4 |
| W1-R2 | 기능 | 저장된 `request`로 재실행해 `expected`와 대조하는 검증 모드를 제공한다 | 계획서 §5 W3 |
| W1-R3 | 기능 | 비결정 값을 정규화하고, 정규화한 필드를 스냅샷에 명시한다 | W1-R6의 전제 |
| W1-R4 | 기능 | 정상·부분 실패·입력 오류 세 부류를 각 Skill에 대해 포함한다 | 96번 §11-6 |
| W1-R5 | 제약 | 운영 코드를 수정하지 않는다 | §2.4 |
| W1-R6 | 비기능 | 동일 환경에서 2회 연속 실행 시 결과가 동일하다(결정성) | 스냅샷 성립 조건 |
| W1-R7 | 제약 | 외부 Provider는 기존 테스트의 Fake·patch를 재사용한다 | §2.4, 비용·결정성 |
| W1-R8 | 제약 | Secret·Token·개인정보를 스냅샷에 기록하지 않는다 | `AGENTS.md` 금지 사항 |

## 5. 설계

### 5.1 산출물 구조

```
workmate-agent/tests/contracts/
  __init__.py
  _harness.py                              기록·대조 공용 코드
  _normalize.py                            비결정 값 정규화
  cases/
    rank_priorities.basic.json
    rank_priorities.second_run_unchanged.json
    rank_priorities.empty_tasks.json
    daily_briefing.all_sources_ok.json
    daily_briefing.gmail_unavailable.json
    daily_briefing.calendar_unavailable.json
    weekly_report.llm_ok.json
    weekly_report.provider_failure.json
    analyze_meeting.transcript_present.json
    analyze_meeting.missing_source.json
    search_meetings.grounded.json
    search_meetings.insufficient_evidence.json
    get_meeting_analysis.found.json
    review_action_items.approve_and_reject.json
    review_proposal.approve.json
    manage_tasks.create_update_delete.json
    read_email.found.json
    assistant_ask.direct_reply.json
    assistant_ask.routes_to_skill.json
    assistant_ask.requires_confirmation.json
    ... (Skill 11개 × 2~4 케이스, 목표 25~30건)
  test_contract_snapshots.py               대조 모드를 unittest로 노출
```

### 5.2 스냅샷 스키마

```json
{
  "case_id": "rank_priorities.basic",
  "skill_id": "rank_priorities",
  "description": "다른 사용자 Task를 제외하고 Top 3를 계산한다",
  "fixture": {
    "tasks": [{"task_id": "a", "assignee_user_id": "alice", "title": "긴급", "priority_hint": 10}]
  },
  "request": {
    "task_id": "task-1", "thread_id": "task-1", "message_id": "message-1",
    "user_id": "alice",
    "payload": {"user_id": "alice", "timezone": "Asia/Seoul", "as_of": "2026-08-13T09:00:00+09:00"}
  },
  "normalized_fields": ["data.data.calculated_at"],
  "expected": {
    "artifact_name": "...",
    "artifact_description": "...",
    "state": "completed",
    "mock": false,
    "warnings": [],
    "text": "...",
    "data": { "...전체..." },
    "markdown": null
  }
}
```

- `expected`는 [`WorkflowResult`](../workmate-agent/app/workflows/registry.py#L41)의 **모든 필드**를 담는다.
  부분 단언으로 생긴 빈틈(§2.2)을 없애는 것이 목적이므로 선택적 축소를 하지 않는다.
- `normalized_fields`는 §5.4 규칙이 적용된 경로 목록이다. 대조 시 이 경로는 값이 아니라 **형식**만 본다.

### 5.3 하네스 인터페이스

```python
# tests/contracts/_harness.py

@dataclass(frozen=True, slots=True)
class SnapshotCase:
    """스냅샷 1건의 입력과 기대 출력."""
    case_id: str
    skill_id: str
    fixture: dict
    request: dict
    normalized_fields: tuple[str, ...]
    expected: dict | None      # 기록 모드에서는 None


async def run_case(case: SnapshotCase) -> dict:
    """Fixture를 세팅하고 Workflow를 실행해 정규화된 결과를 반환한다."""


def record(case_path: Path) -> None:
    """기록 모드 — expected를 채워 파일에 다시 쓴다. W1에서만 사용한다."""


def verify(case_path: Path) -> list[str]:
    """대조 모드 — expected와 실제 결과의 차이를 경로 단위로 반환한다."""
```

- 기록 모드는 `WORKMATE_SNAPSHOT_RECORD=1`일 때만 동작하게 해 **실수로 기대값이 덮어써지는 것을 막는다**
  (`AGENTS.md`: 기대값 완화를 해결 방법으로 인정하지 않는다).
- 대조 모드는 `tests/contracts/test_contract_snapshots.py`에서 일반 unittest로 실행된다.

### 5.4 비결정 값 정규화 규칙

W1의 실질적 난이도는 여기에 있다. 규칙은 **주입 우선, 치환은 차선**이다.

| 값 | 처리 | 방법 |
| --- | --- | --- |
| "현재 시각" 기반 계산 | 주입 | `payload.as_of`·`timezone`을 고정값으로 전달 |
| `calculated_at`·`generated_at` 등 출력 타임스탬프 | 치환 | `"<timestamp>"`로 바꾸고 ISO-8601 형식만 검증 |
| `uuid4()` 기반 ID(Artifact ID 등) | 치환 | `"<uuid>"` |
| 임시 디렉터리 경로 | 치환 | `"<tmpdir>"` |
| dict 순회 순서 | 정렬 | JSON 저장 시 `sort_keys=True` |
| 부동소수점 점수 | 반올림 금지 | 값 그대로 비교 — 점수 변화는 회귀로 잡아야 한다 |

치환한 값은 `normalized_fields`에 반드시 기록한다. 기록 없는 치환은 금지한다(무엇을 검증하지 않는지
명시되지 않으면 스냅샷의 신뢰도를 알 수 없다).

### 5.5 외부 의존 처리

| Provider | 처리 | 근거 |
| --- | --- | --- |
| Gmail·Calendar | 기존 테스트의 Fake Adapter 재사용 | [tests/fixtures/](../workmate-agent/tests/fixtures/) |
| LLM(OpenAI 호환) | `patch`로 고정 응답 주입 | 결정성 확보 |
| STT | `tests/fixtures/fake_realtime_stt.py` | 기존 자산 |
| R2 | `tests/fixtures/fake_r2.py` | 기존 자산 |
| DB | 임시 SQLite + 테스트 Postgres | W0 환경 |

**한계(명시적 기록 대상):** LLM을 Fake로 고정하므로 이 스냅샷은 "같은 LLM 응답이 주어졌을 때 주변
코드가 같은 결과를 만드는가"만 보장한다. 프롬프트 변경과 실제 모델 응답 품질은 검증 범위 밖이다.
D3=B(`langchain-openai` 도입)로 호출 계층 자체가 바뀌므로, 그 경계는 [W2](30-2-w2-graph-foundation.md)의
구조화 출력 동등성 테스트가 담당한다.

## 6. 작업 분해 (WBS)

| ID | 작업 | 선행 | 산출물 |
| --- | --- | --- | --- |
| W1-T1 | 기존 테스트에서 시나리오·Fixture 목록 추출 | — | 케이스 후보표 |
| W1-T2 | 정규화 규칙 구현 | — | `_normalize.py` |
| W1-T3 | 하네스 구현(기록·대조) | W1-T2 | `_harness.py` |
| W1-T4 | 결정적 Skill 케이스 작성 (`rank_priorities`, `manage_tasks`, `get_meeting_analysis`, `review_*`) | W1-T3 | cases/*.json |
| W1-T5 | 부분 실패 Skill 케이스 작성 (`daily_briefing`, `weekly_report`) | W1-T3 | cases/*.json |
| W1-T6 | LLM 의존 Skill 케이스 작성 (`analyze_meeting`, `search_meetings`, `read_email`) | W1-T3 | cases/*.json |
| W1-T7 | `assistant_ask` 케이스 작성 (직접 응답·Skill 위임·확인 필요) | W1-T6 | cases/*.json |
| W1-T8 | 대조 모드를 unittest로 노출 | W1-T4~T7 | `test_contract_snapshots.py` |
| W1-T9 | 결정성 검증(2회 연속 실행) | W1-T8 | 실행 로그 |
| W1-T10 | 증빙·`HANDOFF.md` 기록, 커밋 | W1-T9 | `result.md` |

`assistant_ask`(W1-T7)를 마지막에 두는 이유는 이 Skill이 나머지 10개를 내부에서 호출하기 때문이다
([assistant_router.py:881-891](../workmate-agent/app/workflows/assistant_router.py#L881-L891)). 하위 Skill
케이스가 먼저 안정돼야 한다.

## 7. 검증 설계

| ID | 검증 항목 | 방법 | 판정 기준 |
| --- | --- | --- | --- |
| W1-V1 | 스냅샷 대조 통과 | `uv run python -m unittest tests.contracts.test_contract_snapshots -v` | 전건 PASS |
| W1-V2 | 결정성 | 위 명령 2회 연속 실행 | 두 결과 동일 |
| W1-V3 | 커버리지 | 케이스 파일의 `skill_id` 집합 | 공개 Skill 11개 전부 포함 |
| W1-V4 | 시나리오 부류 | 케이스 메타데이터 집계 | 각 Skill에 정상 1건 이상, 전체에 부분 실패·오류 각 1건 이상 |
| W1-V5 | 기존 테스트 무영향 | 전체 스위트 실행 | 440 + 신규, 실패 0 |
| W1-V6 | 운영 코드 무변경 | `git diff --stat app/` | 출력 없음 |
| W1-V7 | Secret 비포함 | 케이스 파일 전수 검사 | 토큰·키 패턴 미검출 |

## 8. 추적성 매트릭스

| 요구사항 | 작업 | 검증 |
| --- | --- | --- |
| W1-R1 | W1-T3, T4~T7 | W1-V1, W1-V3 |
| W1-R2 | W1-T3, T8 | W1-V1 |
| W1-R3 | W1-T2 | W1-V2 |
| W1-R4 | W1-T4~T7 | W1-V4 |
| W1-R5 | 전 작업 | W1-V6 |
| W1-R6 | W1-T2, T9 | W1-V2 |
| W1-R7 | W1-T6, T7 | W1-V1 |
| W1-R8 | W1-T10 | W1-V7 |

## 9. 완료 정의 (Exit criteria)

1. W1-V1~V7이 전부 PASS.
2. 공개 Skill 11개 전부에 대해 최소 1건의 스냅샷이 존재하고, 부분 실패·입력 오류 케이스가 포함됨.
3. 정규화된 필드 목록이 각 케이스에 명시됨.
4. 증빙에 "이 스냅샷이 보장하지 않는 것"(§5.5 한계)이 기록됨.

## 10. 위험과 완화

| 위험 | 영향 | 완화 |
| --- | --- | --- |
| 정규화가 불완전해 스냅샷이 간헐 실패한다 | 대조 결과를 신뢰할 수 없어 안전망이 무력화 | W1-V2로 2회 연속 실행 확인. 실패 시 원인 필드를 `normalized_fields`에 추가하되 **이유를 함께 기록** |
| 과도한 정규화로 실제 회귀를 놓친다 | 전환 후 값이 바뀌어도 감지 못함 | 치환은 §5.4 표에 있는 부류만 허용. 점수·순위·근거 ID는 치환 금지 |
| 케이스가 대표성을 갖지 못한다 | 커버되지 않은 경로에서 회귀 발생 | W1-T1에서 기존 테스트 시나리오를 전수 조사해 후보를 뽑는다 |
| `assistant_ask` 케이스가 하위 Skill에 연쇄 의존한다 | 하나가 바뀌면 여러 스냅샷이 동시에 깨짐 | W1-T7을 마지막에 배치. 확인 필요 경로는 W6에서 의도적으로 바뀌므로 별도 표시 |
| 스냅샷 기록 모드가 실수로 실행돼 기대값이 덮어써진다 | 회귀를 정답으로 고정 | 환경변수 가드(§5.3) + 기대값 변경은 반드시 커밋 diff로 검토 |

## 11. 롤백·중단 기준

- W1 산출물은 `tests/` 아래 신규 파일뿐이므로 롤백은 파일 삭제로 충분하다.
- **중단 기준:** W1-V2(결정성)를 세 번의 정규화 보완으로도 만족시키지 못하는 Skill이 있으면, 그 Skill은
  스냅샷 대신 "검증 불가 사유"를 기록하고 W3에서 사람이 직접 비교한다. 무리한 정규화로 검증력을
  희생하지 않는다.

## 12. 후행 단계에 넘기는 것

- [W3](30-3-w3-skill-subgraphs.md): Skill별 스냅샷은 Subgraph 재작성의 수용 기준이 된다.
- [W6](30-6-w6-interrupt-resume.md): `assistant_ask.requires_confirmation` 스냅샷은 D1=B로
  **의도적으로 바뀌는** 유일한 부류다. 변경 전후를 나란히 기록해 계약 변경 내역의 근거로 쓴다.
- [W9](30-9-w9-docs-evidence.md): 스냅샷 diff 요약이 전환 결과 보고의 핵심 증빙이 된다.

## 13. 참조

- [30-langgraph-migration-plan.md](30-langgraph-migration-plan.md) §1-4, §5 W1, §8
- [`WorkflowResult`](../workmate-agent/app/workflows/registry.py#L41)
- [`tests/fixtures/`](../workmate-agent/tests/fixtures/)
