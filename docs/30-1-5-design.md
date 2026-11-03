# W1-5 — 설계

> [30-1-w1-contract-snapshot.md](30-1-w1-contract-snapshot.md) §5의 상세 문서.

## 1. 산출물 구조

```
workmate-agent/tests/contracts/
  __init__.py
  _harness.py                              기록·대조 공용 코드
  _normalize.py                            비결정 값 정규화
  _fixtures.py                             케이스별 Fixture 세팅 (Skill별 setup)
  cases/
    rank_priorities.basic.json
    rank_priorities.second_run_unchanged.json
    rank_priorities.empty_tasks.json
    daily_briefing.all_sources_ok.json
    daily_briefing.gmail_unavailable.json
    daily_briefing.calendar_unavailable.json
    daily_briefing.both_providers_down.json
    weekly_report.llm_ok.json
    weekly_report.provider_failure.json
    analyze_meeting.transcript_present.json
    analyze_meeting.missing_source.json
    analyze_meeting.index_failure.json
    search_meetings.grounded.json
    search_meetings.insufficient_evidence.json
    search_meetings.empty_query.json
    get_meeting_analysis.found.json
    review_action_items.approve_and_reject.json
    review_proposal.approve.json
    review_proposal.ignore.json
    manage_tasks.list.json
    manage_tasks.create.json
    manage_tasks.delete.json
    read_email.found.json
    assistant_ask.direct_reply.json
    assistant_ask.routes_to_skill.json
    assistant_ask.requires_confirmation.json
    assistant_ask.confirmed_execution.json
  test_contract_snapshots.py               대조 모드를 unittest로 노출
```

목표 27건. 최종 수는 W1-T1의 시나리오 조사 결과에 따라 조정한다.

## 2. 스냅샷 스키마

```json
{
  "case_id": "rank_priorities.basic",
  "skill_id": "rank_priorities",
  "description": "다른 사용자 Task를 제외하고 Top 3를 계산한다",
  "origin": "tests/test_priority_workflow.py::test_workflow_ranks_only_owned_tasks",
  "fixture": {
    "tasks": [
      {"task_id": "...", "assignee_user_id": "...", "title": "긴급", "priority_hint": 10},
      {"task_id": "...", "assignee_user_id": "<other>", "title": "다른 사용자", "priority_hint": 10}
    ]
  },
  "request": {
    "task_id": "task-1", "thread_id": "task-1", "message_id": "message-1",
    "user_id": "...",
    "payload": {"user_id": "...", "timezone": "Asia/Seoul", "as_of": "2026-08-13T09:00:00+09:00"}
  },
  "normalized_fields": [
    {"path": "data.data.calculated_at", "rule": "timestamp", "reason": "datetime.now() 기반"},
    {"path": "text", "rule": "timestamp_in_json", "reason": "위와 같은 값이 JSON 문자열에도 포함"}
  ],
  "expected": {
    "artifact_name": "priority_ranking",
    "artifact_description": "Deterministic Top 3 ranking computed from user-owned Tasks.",
    "state": "completed",
    "mock": false,
    "warnings": [],
    "text": "...",
    "data": { "type": "priority_ranking", "data": { "..." } },
    "markdown": null
  }
}
```

### 2.1 필드 설명

| 필드 | 역할 |
| --- | --- |
| `case_id` | 파일명과 일치. 대조 로그에서 파일을 바로 찾는다 |
| `origin` | **이 케이스가 어느 기존 테스트에서 왔는지.** W3에서 같은 시나리오를 재현할 때 참조 |
| `fixture` | DB·저장소 초기 상태 |
| `request` | Workflow 입력 |
| `normalized_fields` | 비교 제외 경로 + **규칙 + 이유** |
| `expected` | `WorkflowResult` 8개 필드 전체 |

### 2.2 설계 결정 W1-D1 — `origin`을 기록한다

기존 테스트에서 시나리오를 가져왔다면 출처를 남긴다. W3에서 Skill을 재작성할 때 "이 케이스가 왜
있는지"를 알아야 하고, 기존 테스트의 주석에 실사용 배경이 담겨 있기 때문이다.

예: `daily_briefing.gmail_unavailable`의 `origin`을 따라가면
[test_daily_briefing.py](../workmate-agent/tests/test_daily_briefing.py)의 해당 테스트가 나오고,
거기서 2026-08-16 갭 문서 #7의 배경을 볼 수 있다.

### 2.3 설계 결정 W1-D2 — `normalized_fields`에 이유를 쓴다

단순 경로 목록이 아니라 `{path, rule, reason}` 객체로 둔다.

| 이유 | 설명 |
| --- | --- |
| 과도한 정규화 억제 | 이유를 쓰게 하면 "일단 빼두자"가 어려워진다 |
| 리뷰 가능성 | 정규화 목록만 훑어도 "무엇이 검증되지 않는지" 파악된다 |
| W9 보고 | 스냅샷의 한계를 정량적으로 기술할 수 있다 |

## 3. 하네스 설계

### 3.1 인터페이스

```python
# tests/contracts/_harness.py

@dataclass(frozen=True, slots=True)
class SnapshotCase:
    """스냅샷 1건의 입력과 기대 출력."""
    case_id: str
    skill_id: str
    description: str
    origin: str | None
    fixture: dict
    request: dict
    normalized_fields: tuple[NormalizedField, ...]
    expected: dict | None      # 기록 모드에서는 None


async def run_case(case: SnapshotCase) -> dict:
    """Fixture를 세팅하고 Workflow를 실행해 정규화된 결과를 반환한다.

    실행은 항상 격리된 임시 저장소에서 한다 — 케이스 간 상태가 섞이면
    결정성(W1-R6)이 깨진다.
    """


def record(case_path: Path) -> None:
    """기록 모드 — expected를 채워 파일에 다시 쓴다.

    WORKMATE_SNAPSHOT_RECORD=1일 때만 동작한다(W1-R9). 기대값이 실수로
    덮어써지면 회귀를 정답으로 고정하게 된다.
    """


def verify(case_path: Path) -> list[Difference]:
    """대조 모드 — expected와 실제 결과의 차이를 경로 단위로 반환한다."""


@dataclass(frozen=True, slots=True)
class Difference:
    path: str          # "data.data.priorities[0].score"
    expected: object
    actual: object
```

### 3.2 실행 격리

케이스마다 독립된 임시 저장소를 쓴다.

```
run_case()
  ├─ 임시 디렉터리 생성 (SQLite 파일)
  ├─ WORKMATE_TASK_DB_PATH 등 환경변수 설정
  ├─ fixture를 저장소에 적재
  ├─ Fake Provider 주입
  ├─ Workflow 실행
  ├─ 결과 정규화
  └─ 임시 디렉터리 정리
```

**격리가 없으면 생기는 문제:** `rank_priorities`는 실행 시 우선순위 Snapshot을 저장하고, 다음 실행의
`changes` 값이 달라진다. 케이스가 서로 영향을 주면 실행 순서에 따라 결과가 바뀐다(결정성 위반).

`rank_priorities.second_run_unchanged` 케이스는 **의도적으로** 2회 실행하는 시나리오다. 이런 경우는
`fixture`에 "사전 실행" 정보를 담아 명시적으로 표현한다.

### 3.3 Fixture 적재

Skill마다 필요한 저장소가 다르다. `_fixtures.py`에 Skill별 setup 함수를 둔다.

```python
FIXTURE_LOADERS: dict[str, Callable[[dict, Path], None]] = {
    "rank_priorities": load_task_fixture,
    "daily_briefing": load_task_and_sync_fixture,
    "analyze_meeting": load_meeting_fixture,
    ...
}
```

기존 [`tests/fixtures/work_domain.py`](../workmate-agent/tests/fixtures/work_domain.py)의
`task_fixture()`·`sync_state_fixture()`를 재사용한다. `OWNER_USER_ID`·`OTHER_USER_ID` 상수도
그대로 쓴다 — 사용자 격리 시나리오가 이미 이 값으로 작성돼 있다.

## 4. 정규화 설계

### 4.1 원칙 — 주입 우선, 치환은 차선

| 우선순위 | 방법 | 예 |
| --- | --- | --- |
| 1 | **주입** — 입력으로 고정값을 넣어 출력이 결정적이 되게 한다 | `payload.as_of`, `payload.timezone` |
| 2 | **치환** — 출력의 해당 경로를 마스킹하고 형식만 검증 | `calculated_at` → `"<timestamp>"` |
| 3 | (금지) 필드 제외 | — |

3번을 금지하는 이유: 필드를 아예 빼면 그 필드가 사라지는 회귀도 통과한다. 치환은 **존재 여부와
형식**은 검증한다.

### 4.2 규칙표

| 규칙 | 대상 | 검증 내용 | 예 |
| --- | --- | --- | --- |
| `timestamp` | 출력 타임스탬프 | ISO-8601 형식 | `calculated_at`, `generated_at` |
| `uuid` | `uuid4()` 기반 ID | UUID 형식 | `priority_snapshot_id`, Artifact ID |
| `timestamp_in_json` | `text` 안의 JSON 문자열에 포함된 타임스탬프 | 파싱 후 해당 경로만 치환 | `text` |
| `tmpdir` | 임시 경로 | 존재 여부 | 파일 경로 |
| `sorted_keys` | dict 순회 순서 | — | JSON 저장 시 `sort_keys=True` |

**금지 대상** — 아래는 정규화하지 않는다. 회귀로 잡아야 하는 값이다.

| 값 | 이유 |
| --- | --- |
| 점수(`score`, `score_breakdown`) | 계산이 바뀌면 알아야 한다 |
| 순위(`rank`), 근거 ID(`source_refs`) | `AGENTS.md` 결정적 규칙 |
| `warnings`의 `code`·`retryable` | 실패 정책의 계약 |
| `artifact_name`·`artifact_description` | 공개 계약 |
| 근거 문장(`reasons`) | 값이 바뀌면 사용자가 보는 내용이 바뀐다 |

### 4.3 `text` 필드의 특수성

`text`는 대부분 `json.dumps(result_payload, sort_keys=True)` 결과다. 즉 `data`와 같은 내용이 문자열로
들어 있다. 타임스탬프가 포함되면 문자열 전체가 달라진다.

**처리:** `timestamp_in_json` 규칙으로 `text`를 파싱해 해당 경로만 치환한 뒤 다시 직렬화해 비교한다.
문자열 전체를 정규화 대상으로 빼면 `text`의 회귀를 전혀 못 잡는다.

### 4.4 병렬 결과 순서

`daily_briefing`의 `warnings`는 현재 순차 실행이므로 순서가 고정적이다. 그러나 W3에서 병렬화하면
(W3-R6) 순서가 바뀔 수 있다.

**설계 결정 W1-D3 — `warnings`는 순서 비의존 비교를 기본으로 한다.**

| | 방식 | 평가 |
| --- | --- | --- |
| A | 순서까지 비교 | W3 병렬화 후 전부 실패. 실패가 회귀 때문인지 순서 때문인지 불분명 |
| **B** | **순서 비의존(정렬 후 비교)** | **채택** — 경고의 집합이 같은지를 본다 |

경고 순서는 사용자에게 의미 있는 계약이 아니다. 내용과 개수가 계약이다.

## 5. 외부 의존 처리

| Provider | 처리 | 근거 자산 |
| --- | --- | --- |
| Gmail·Calendar | Fake Adapter 주입 | `build_daily_briefing_workflow(provider_factory=...)` |
| LLM(라우팅·요약·분석) | 고정 응답 주입 | `patch` 또는 주입 파라미터 |
| Embedding | Fake Provider | `build_search_meetings_workflow(embedding_provider=...)` |
| STT | [`fake_realtime_stt.py`](../workmate-agent/tests/fixtures/fake_realtime_stt.py) | 기존 |
| R2 | [`fake_r2.py`](../workmate-agent/tests/fixtures/fake_r2.py) | 기존 |
| DB | 임시 SQLite / 테스트 Postgres | W0 환경 |

### 5.1 주입 지점이 이미 있다

대부분의 Workflow 빌더가 테스트 주입 파라미터를 갖는다.

| Skill | 주입 파라미터 |
| --- | --- |
| `daily_briefing` | `provider_factory`, `repositories` |
| `analyze_meeting` | `analyzer`, storage, stt |
| `search_meetings` | `repository`, `embedding_provider`, `answer_service` |
| `weekly_report` | `client`(LLM), `meeting_repository` |

덕분에 W1-R5(운영 코드 무수정)를 지키면서 Fake를 넣을 수 있다. 주입 지점이 없는 Skill은 `patch`로
처리한다.

### 5.2 한계

**이 스냅샷이 보장하는 것:** "같은 LLM 응답이 주어졌을 때 그 주변 코드가 같은 결과를 만든다."

**보장하지 않는 것:** 프롬프트 변경, 실제 모델 응답 품질, 모델 교체의 영향.

D3=B(`langchain-openai` 도입)로 호출 계층 자체가 바뀌므로, 그 경계는
[W2-V6](30-2-7-verification.md)의 구조화 출력 동등성 테스트가 담당한다. W1과 W2-V6이 함께 있어야 LLM
경로 전환이 안전하다.

## 6. 설계 결정 요약

| ID | 결정 | 근거 |
| --- | --- | --- |
| W1-D1 | 케이스에 `origin`(출처 테스트)을 기록 | §2.2 |
| W1-D2 | `normalized_fields`에 규칙과 이유를 함께 기록 | §2.3 |
| W1-D3 | `warnings`는 순서 비의존 비교 | §4.4 |
| W1-D4 | 케이스마다 저장소 격리 | §3.2 |
| W1-D5 | 필드 제외 금지, 치환만 허용 | §4.1 |

## 7. 참조

- [30-1-4](30-1-4-requirements.md) — 이 설계가 만족하는 요구사항
- [30-1-7](30-1-7-verification.md) — 설계 결정의 검증
- [`tests/fixtures/`](../workmate-agent/tests/fixtures/) — 재사용할 기존 자산
