# W3-4 — 요구사항 명세

> [30-3-w3-skill-subgraphs.md](30-3-w3-skill-subgraphs.md) §4의 상세 문서.

각 요구사항을 **설명 / 근거 / 수용 기준 / 검증 / 우선순위** 형식으로 기술한다.

## 요약

| ID | 구분 | 한 줄 | 우선순위 | 검증 |
| --- | --- | --- | --- | --- |
| W3-R1 | 기능 | Skill 11개를 Subgraph로 구현 | 필수 | W3-V2 |
| W3-R2 | 기능 | 출력이 W1 스냅샷과 일치 | **필수(최우선)** | W3-V1 |
| W3-R3 | 제약 | 모든 조회에 `user_id` 범위·Soft Delete 제외 | **필수(보안)** | W3-V3 |
| W3-R4 | 제약 | 점수·순위·근거 ID를 LLM이 만들지 않음 | 필수 | W3-V7 |
| W3-R5 | 기능 | Provider 부분 실패 시 부분 결과 + `warnings` | 필수 | W3-V5 |
| W3-R6 | 기능 | Daily Briefing 소스 수집 병렬화 | 중요 | W3-V6 |
| W3-R7 | 제약 | Subgraph가 다른 Skill을 직접 import하지 않음 | 필수 | W3-V9 |
| W3-R8 | 제약 | 운영 경로에 Mock·고정 샘플 없음 | 필수 | W3-V8 |
| W3-R9 | 제약 | 공개 함수·노드에 한글 Docstring | 권장 | 코드 검토 |
| W3-R10 | 제약 | 숨은 부작용을 의도적으로만 변경 | **필수** | W3-V11 |
| W3-R11 | 제약 | 확인 흐름을 W3에서 바꾸지 않음 | 필수 | W3-V1 |

---

## W3-R1 — Skill 11개 Subgraph 구현

**설명** [runtime.py:66-82](../workmate-agent/app/a2a/runtime.py#L66)의 공개 Skill 11개 각각을
`StateGraph` Subgraph로 구현한다.

**근거** [96번 §2](96-workmate-langgraph-target-architecture.md): "Skill은 별도 Agent가 아니라 Root
Graph가 호출하는 Subgraph다."

**수용 기준**
- `app/graph/skills/` 아래 11개 Subgraph 존재
- 각 Subgraph가 `WorkmateState`를 입출력으로 사용
- 컴파일 가능하고 단독 실행 가능(W4 합성 전에도 테스트 가능)

**검증** W3-V2 / **우선순위** 필수

---

## W3-R2 — 스냅샷 일치 (최우선)

**설명** 각 Subgraph의 출력이 W1 계약 스냅샷의 `expected`와 일치한다.

**근거** D2=A. 구현과 테스트를 동시에 재작성하므로 스냅샷이 유일한 회귀 감지 수단이다
([계획서 §1-4](30-langgraph-migration-plan.md)).

**수용 기준**
- `WorkflowResult` 8개 필드가 모두 일치 — `artifact_name`·`artifact_description`·`text`·`data`·
  `markdown`·`state`·`warnings`·`mock`
- 정규화된 필드(`normalized_fields`)는 형식만 비교
- 차이가 있으면 **의도적 변경으로 설명되거나 수정**되어야 한다. "사소한 차이"로 넘기지 않는다

**검증** W3-V1 / **우선순위** **필수(최우선)**

---

## W3-R3 — 사용자 범위 (보안)

**설명** 모든 조회에 요청된 `user_id` 조건을 적용하고 Soft Delete 데이터를 제외한다.

**근거** `AGENTS.md` 구현 규칙, [96번 §11-3](96-workmate-langgraph-target-architecture.md).
이것이 깨지면 타 사용자 데이터가 노출된다. W3에서 조회 코드를 노드로 옮기는 과정에서 조건이 누락될
위험이 실재한다.

**수용 기준**
- 각 Skill에 대해 타 사용자 데이터를 섞은 Fixture로 실행했을 때 결과에 포함되지 않는다
- Soft Delete된 Task·Meeting이 결과에 없다
- 조회 노드가 `state["user_id"]`를 사용한다(Fixture 하드코딩 금지)

**검증** W3-V3 / **우선순위** **필수(보안)**

---

## W3-R4 — LLM 책임 경계

**설명** 우선순위 점수·순위·근거 ID를 LLM이 생성하거나 변경하지 않는다.

**근거** `AGENTS.md`: "우선순위 점수는 결정적으로 계산한다", [96번 §11-4·11-5](96-workmate-langgraph-target-architecture.md).

**수용 기준**
- `rank_priorities` Subgraph에 LLM 노드가 없다
- 점수 계산은 [`rank_tasks()`](../workmate-agent/app/domain/priority.py) Domain 함수 호출로만 이뤄진다
- `weekly_report`에서 LLM은 요약 문장만 만들고, 분류(`completed`/`in_progress`/`delayed`)와
  `source_refs`는 Domain이 소유한다
- `search_meetings`에서 근거 ID는 검색 결과에서 오고 LLM이 만들지 않는다

**검증** W3-V7 / **우선순위** 필수

---

## W3-R5 — 부분 실패 보존

**설명** Provider 일부 실패 시 사용 가능한 결과와 `warnings`를 반환한다.

**근거** `AGENTS.md`: "외부 Provider 장애 시 정의된 부분 결과와 `warnings`를 반환한다",
[96번 §11-6](96-workmate-langgraph-target-architecture.md).

**수용 기준** — Skill별 실패 파급이 현재 동작과 같아야 한다([30-3-5](30-3-5-design.md) §7).

| Skill | 핵심(전체 실패) | 보조(`warnings` 후 진행) |
| --- | --- | --- |
| `daily_briefing` | Task 저장소 | Gmail, Calendar, 메일 본문 보강, LLM 관련성 판정 |
| `weekly_report` | Task·근거 조회 | LLM 요약 |
| `analyze_meeting` | 회의 조회, STT, 분석, 근거 검증 | 색인(embedding·pgvector) |
| `search_meetings` | 검색, 회의 날짜 누락 | LLM 답변 생성 |

**검증** W3-V5 / **우선순위** 필수

---

## W3-R6 — Daily Briefing 병렬화

**설명** 소스 수집을 병렬 노드로 팬아웃하고 합류 노드에서 팬인한다.

**근거** [계획서 §2.1](30-langgraph-migration-plan.md), [96번 §5.1](96-workmate-langgraph-target-architecture.md).
현재 구현은 Gmail → Calendar → Task 순차다.

**수용 기준**
- Gmail·Calendar·Task 수집이 서로 기다리지 않는다
- 두 소스가 동시에 실패해도 `warnings` 2건이 모두 보존된다(W2 Reducer가 여기서 처음 실제로 쓰인다)
- 결과 값은 순차 실행과 동일하다

**주의** 현재 코드에는 이미 부분적 병렬이 있다 — 메일 본문 보강은
`asyncio.gather(..., return_exceptions=True)`로 병렬 실행되며 개별 실패를 조용히 무시한다
([daily_briefing.py:195-208](../workmate-agent/app/workflows/daily_briefing.py#L195)). 이 동작도
보존해야 한다.

**검증** W3-V6 / **우선순위** 중요

---

## W3-R7 — Subgraph 독립성

**설명** Subgraph가 다른 Skill 모듈을 직접 import하지 않는다.

**근거** 현재 지연 import로 서로를 부르는 구조는 Subgraph 합성(W4) 시 순환 의존이 된다.

**수용 기준**
- `app/graph/skills/` 내부에서 다른 Skill 모듈을 import하지 않는다
- Skill 실행이 필요하면 **주입된 핸들**을 통한다([30-3-5](30-3-5-design.md) §4)
- 공통 로직이 필요하면 Domain 함수로 내린다

**검증** W3-V9 / **우선순위** 필수

---

## W3-R8 — Mock 부재

**설명** 운영 경로의 Skill이 Mock·고정 샘플 응답을 반환하지 않는다.

**근거** `AGENTS.md` 완료 규칙: "마일스톤이 담당하는 실제 Workflow가 운영 실행 경로에서 Mock·고정
샘플 응답을 반환하면 완료 처리하지 않는다. Fake·Mock은 단위·계약 테스트의 명시적인 Fixture에서만
허용한다."

**수용 기준**
- 공개 Skill 11개의 결과에 `mock=True`가 없다
- 테스트 Fixture에서만 Fake를 주입한다

**검증** W3-V8 / **우선순위** 필수

---

## W3-R9 — Docstring

**설명** 모듈·공개 함수·노드에 한글 Docstring을 작성한다.

**근거** `AGENTS.md` 주석 규칙: 모듈·공개 API·Domain·Adapter 경계에 역할과 계약을 기록하고, 이벤트
순서·멱등성·재시도·취소처럼 코드만 읽어도 놓치기 쉬운 불변식을 명시한다.

**수용 기준**
- 각 노드 함수에 "무엇을 읽고 무엇을 State에 쓰는지" 기록
- 부분 실패 정책(핵심/보조)을 노드 Docstring에 명시
- 함수명·Schema 필드명·환경변수명은 원문 유지

**검증** 코드 검토 / **우선순위** 권장

---

## W3-R10 — 숨은 부작용 보존

**설명** 결과 값에 드러나지 않는 DB 쓰기 부작용을 의도치 않게 제거하거나 추가하지 않는다.

**근거** 조사 결과 `daily_briefing`은 내부에서 `rank_priorities` Workflow를 호출하며, 그 과정에서
우선순위 Snapshot이 저장된다([priority.py:123](../workmate-agent/app/workflows/priority.py#L123)).
이 부작용은 `daily_briefing`의 응답에 나타나지 않으므로 **W1 스냅샷으로 검출되지 않는다.**

**수용 기준**
- [30-3-5](30-3-5-design.md) §3의 W3-D1 결정에 따른다
- 부작용 유지/제거 중 무엇을 택했든 **증빙에 명시**한다
- 부작용 발생 여부를 DB 상태로 직접 검증한다

**검증** W3-V11 / **우선순위** **필수**

---

## W3-R11 — 확인 흐름 동결

**설명** `assistant_ask`의 확인 흐름을 W3에서 `interrupt`로 바꾸지 않는다.

**근거** W1 스냅샷의 `assistant_ask.requires_confirmation` 케이스와 대조해야 한다. 미리 바꾸면 "이식
오류인지 계약 변경인지" 구분할 수 없다.

**수용 기준**
- `pending_action`을 응답에 싣고 종료하는 동작이 그대로다
- `confirmed_skill_id` 재요청 경로가 그대로 동작한다
- [`_requires_confirmation()`](../workmate-agent/app/workflows/assistant_router.py#L221)의 판정 규칙
  4종이 그대로다 — `analyze_meeting` 항상, `review_action_items`의 `reject` 포함,
  `review_proposal`의 `ignore`, `manage_tasks`의 `delete`
- 단, **노드 경계는 W6을 고려해 미리 나눈다**

**검증** W3-V1(스냅샷) / **우선순위** 필수

---

## 요구사항 간 의존

```
W3-R1 (Subgraph) ─┬→ W3-R2 (스냅샷 일치)   ← 최우선 수용 기준
                  ├→ W3-R3 (user_id)       ← 보안
                  ├→ W3-R5 (부분 실패)
                  ├→ W3-R6 (병렬화)
                  └→ W3-R11 (확인 흐름 동결)

W3-R7 (독립성) ─→ W4 합성 가능성
W3-R10 (숨은 부작용) ─→ W3-D1 결정에 종속
```

## 참조

- [30-3-5](30-3-5-design.md) — 각 요구사항의 구현 설계
- [30-3-7](30-3-7-verification.md) — 검증 케이스
- [30-3-8](30-3-8-traceability.md) — 추적성
