# W3-1 — 문서 정보와 문서 체계

> [30-3-w3-skill-subgraphs.md](30-3-w3-skill-subgraphs.md) §1의 상세 문서.

## 1. 단계 식별

| 항목 | 값 |
| --- | --- |
| 단계 코드 | W3 |
| 단계명 | Skill Subgraph 11개 재작성 |
| 상위 계획 | [30-langgraph-migration-plan.md](30-langgraph-migration-plan.md) §5 |
| 선행 단계 | [W2 Graph 골격](30-2-w2-graph-foundation.md) |
| 후행 단계 | [W4 Root Graph](30-4-w4-root-graph.md) |
| 상태 | 대기 |
| 관련 확정 결정 | D2=A(스냅샷이 수용 기준), D3=B(LLM 경계) |

## 2. 단계 성격

W3은 **전환에서 가장 큰 단계**다. 영향 규모는 다음과 같다.

| 대상 | 규모 |
| --- | --- |
| 재작성할 구현 | `app/workflows/` 약 2,600줄 |
| 영향받는 테스트 | 18개 파일 약 4,675줄 |
| Skill 수 | 공개 11개 |
| 최대 단일 파일 | [assistant_router.py](../workmate-agent/app/workflows/assistant_router.py) 937줄 + 테스트 1,019줄 |

### 2.1 W3이 하는 일의 본질

코드를 옮기는 것이 아니라 **함수 안에 숨어 있던 중간 상태를 State로 드러내는 것**이다.

현재 Skill은 하나의 `async def execute()` 안에서 지역 변수로 모든 중간 결과를 들고 있다. 예를 들어
[daily_briefing.py](../workmate-agent/app/workflows/daily_briefing.py)의 `execute()`는 `warnings`,
`calendar_events`, `messages`, `message_summaries`, `provider_freshness`, `registered_task_ids`를
지역 변수로 유지한다. 이 값들은 함수가 끝나면 사라지고, 외부에서 관찰할 수 없다.

Subgraph로 바꾸면 같은 값이 State 채널이 된다. 그 결과 Checkpoint에 남고, 이력 조회가 가능해지고,
병렬 노드가 안전하게 공유할 수 있게 된다. 대신 **무엇을 State에 올리고 무엇을 노드 지역에 둘지**를
결정해야 하며, 이것이 W3 설계의 핵심이다.

### 2.2 W3에서 하지 않는 일

W3 시점에도 **운영 경로는 여전히 `WorkflowRegistry`**다. 만든 Subgraph는 테스트에서만 실행된다.
`app/workflows/`는 그대로 살아 있고, 기존 테스트도 계속 통과해야 한다.

특히 `assistant_ask`의 확인 흐름은 **현재 방식(`pending_action` 반환) 그대로** 재현한다. `interrupt`로
바꾸는 것은 W6이며, W3에서 미리 바꾸면 W1 스냅샷과 대조할 수 없다.

## 3. 문서 체계

W3 상세 계획은 상위 문서 [30-3](30-3-w3-skill-subgraphs.md)의 절 번호에 대응하는 12개 문서로 분해한다.

| 문서 | 대응 절 | 내용 |
| --- | --- | --- |
| [30-3-1](30-3-1-document-info.md) | §1 | 문서 정보·체계·용어·ID 규칙 (이 문서) |
| [30-3-2](30-3-2-scope.md) | §2 | 목적과 범위, 설계 원칙 4종 |
| [30-3-3](30-3-3-entry-criteria.md) | §3 | 선행 조건, 부분 착수 규칙 |
| [30-3-4](30-3-4-requirements.md) | §4 | 요구사항 W3-R1~R9 |
| [30-3-5](30-3-5-design.md) | §5 | 설계 — Skill 11개 노드 분해, 숨은 부작용 |
| [30-3-6](30-3-6-wbs.md) | §6 | 작업 분해 W3-T0~T9 |
| [30-3-7](30-3-7-verification.md) | §7 | 검증 설계 W3-V1~V10 |
| [30-3-8](30-3-8-traceability.md) | §8 | 추적성 매트릭스 |
| [30-3-9](30-3-9-exit-criteria.md) | §9 | 완료 정의와 Skill별 판정 |
| [30-3-10](30-3-10-risks.md) | §10 | 위험 등록부 |
| [30-3-11](30-3-11-rollback.md) | §11 | 롤백·중단·재개 기준 |
| [30-3-12](30-3-12-references.md) | §12 | 참조 자료와 읽을 지점 |

상위 문서 [30-3](30-3-w3-skill-subgraphs.md)은 **요약과 색인**이다. 충돌 시 상세 문서를 기준으로 한다.

## 4. 식별자 규칙

| 접두 | 의미 | 예 | 정의 위치 |
| --- | --- | --- | --- |
| `W3-E` | 선행 조건 | `W3-E3` | [30-3-3](30-3-3-entry-criteria.md) |
| `W3-R` | 요구사항 | `W3-R4` | [30-3-4](30-3-4-requirements.md) |
| `W3-T` | 작업 | `W3-T7` | [30-3-6](30-3-6-wbs.md) |
| `W3-V` | 검증 | `W3-V1` | [30-3-7](30-3-7-verification.md) |
| `W3-K` | 위험 | `W3-K2` | [30-3-10](30-3-10-risks.md) |
| `W3-D` | 설계 결정 | `W3-D1` | [30-3-5](30-3-5-design.md) |

W3은 Skill별로 작업이 반복되므로, 작업 ID에 Skill을 덧붙여 구분한다(예: `W3-T3.daily_briefing`).

## 5. 용어

| 용어 | 정의 | 주의 |
| --- | --- | --- |
| **Skill** | 공개 `skill_id`로 호출되는 업무 단위. 현재 11개 | Agent Card의 Skill과 내부 Skill이 같다(2026-08-17 이후) |
| **Subgraph** | Skill 하나를 구현하는 `StateGraph` | Root Graph의 노드로 꽂힌다(W4) |
| **노드** | Subgraph의 실행 단위 함수 | State 부분 갱신(dict)을 반환한다 |
| **팬아웃/팬인** | 한 노드에서 여러 노드로 분기했다가 다시 합류 | `daily_briefing`의 소스 수집 |
| **부분 실패** | 일부 Provider가 실패해도 사용 가능한 결과를 내는 것 | 예외로 죽이지 않고 `warnings` 누적 |
| **핵심 소스 / 보조 소스** | 실패 시 전체 실패 / 부분 결과 | Skill마다 다르다([30-3-5](30-3-5-design.md) §7) |
| **확인 대상 동작** | 실행 전 사용자 확인이 필요한 조합 | [`_requires_confirmation()`](../workmate-agent/app/workflows/assistant_router.py#L221)이 정의 |
| **숨은 부작용** | 결과에 드러나지 않지만 DB를 바꾸는 동작 | [30-3-5](30-3-5-design.md) §3의 W3-D1 |

## 6. 대상 Skill 목록

[runtime.py:66-82](../workmate-agent/app/a2a/runtime.py#L66)의 `_SKILLS` 11개가 대상이다.

| # | skill_id | 현재 구현 | 분류 |
| --- | --- | --- | --- |
| 1 | `rank_priorities` | [priority.py](../workmate-agent/app/workflows/priority.py) | 결정적 |
| 2 | `daily_briefing` | [daily_briefing.py](../workmate-agent/app/workflows/daily_briefing.py) | 부분 실패 + 병렬 |
| 3 | `weekly_report` | [weekly_report.py](../workmate-agent/app/workflows/weekly_report.py) | LLM + 근거 검증 |
| 4 | `analyze_meeting` | [meetings.py:216](../workmate-agent/app/workflows/meetings.py#L216) | STT + LLM + 색인 |
| 5 | `search_meetings` | [meetings.py:377](../workmate-agent/app/workflows/meetings.py#L377) | 검색 + 근거 판정 |
| 6 | `get_meeting_analysis` | [assistant_skills.py:174](../workmate-agent/app/workflows/assistant_skills.py#L174) | 단순 조회 |
| 7 | `review_action_items` | [assistant_skills.py:199](../workmate-agent/app/workflows/assistant_skills.py#L199) | 상태 변경 |
| 8 | `review_proposal` | [assistant_skills.py:226](../workmate-agent/app/workflows/assistant_skills.py#L226) | 상태 변경 |
| 9 | `manage_tasks` | [assistant_skills.py:293](../workmate-agent/app/workflows/assistant_skills.py#L293) | CRUD |
| 10 | `read_email` | [assistant_skills.py:63](../workmate-agent/app/workflows/assistant_skills.py#L63) | 외부 실시간 조회 |
| 11 | `assistant_ask` | [assistant_router.py:771](../workmate-agent/app/workflows/assistant_router.py#L771) | Meta(나머지 10개 호출) |

`runtime_bootstrap`은 전송 골격 확인용 Mock Workflow로 공개 Skill이 아니다. W4에서 Root Graph의
처리 방식을 정한다.

## 7. 산출물 위치

```
workmate-agent/
  app/graph/skills/
    rank_priorities.py
    daily_briefing.py
    weekly_report.py
    analyze_meeting.py
    search_meetings.py
    assistant_router.py
    assistant_skills/
      get_meeting_analysis.py  review_action_items.py  review_proposal.py
      manage_tasks.py          read_email.py
  tests/
    test_graph_skill_*.py            Skill별 신규 테스트
docs/evidence/langgraph/W3/runs/{run_id}/result.md
```

## 8. 변경 이력

| 일자 | 변경 | 사유 |
| --- | --- | --- |
| 2026-09-23 | 초판 (상위 문서 §1) | 단계별 상세 계획 수립 |
| 2026-09-28 | 12개 문서로 분해, Skill 구현 구조 조사 결과 반영 | 절별 상세화 요청 |
