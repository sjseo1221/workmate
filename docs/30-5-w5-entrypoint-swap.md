# W5 — 진입점 교체

> **이 문서는 요약과 색인이다.** 각 절의 상세는 아래 12개 문서에 있고, 충돌 시 상세 문서를 기준으로
> 한다.
>
> | 절 | 상세 문서 | 내용 |
> | --- | --- | --- |
> | §1 | [30-5-1](30-5-1-document-info.md) | 문서 정보·용어·교체 대상 |
> | §2 | [30-5-2](30-5-2-scope.md) | 목적, 교체 지점 3곳, 범위 |
> | §3 | [30-5-3](30-5-3-entry-criteria.md) | 선행 조건, **기준선 테스트 보강** |
> | §4 | [30-5-4](30-5-4-requirements.md) | 요구사항 W5-R1~R10 |
> | §5 | [30-5-5](30-5-5-design.md) | 설계 — 교체 전후, 오류 경계, **`message_id` 비대칭** |
> | §6 | [30-5-6](30-5-6-wbs.md) | 작업 분해 W5-T0~T10 |
> | §7 | [30-5-7](30-5-7-verification.md) | 검증 설계 W5-V1~V10 + **로컬 HTTP 확인** |
> | §8 | [30-5-8](30-5-8-traceability.md) | 추적성, **과거 회귀 → 검증 매핑** |
> | §9 | [30-5-9](30-5-9-exit-criteria.md) | 완료 정의, 승인 경계 |
> | §10 | [30-5-10](30-5-10-risks.md) | 위험 등록부 W5-K1~K9 |
> | §11 | [30-5-11](30-5-11-rollback.md) | 롤백·중단·재개, **롤백 착지점** |
> | §12 | [30-5-12](30-5-12-references.md) | 참조 자료와 읽을 지점 |
>
> **W5의 본질:** 코드 변경은 작지만(호출 3곳) **지켜야 할 과거 회귀가 다섯 건**이다 —
> 2026-08-14 Artifact text Part 누락, 2026-08-15 CORS 헤더 없는 500, 2026-08-16 비동기 Task가
> `WORKING`에 갇힘·`warnings` 유실·`data` 누락. 변경량으로 위험을 판단하지 않는다
> ([30-5-8](30-5-8-traceability.md) §6). 또한 **단위 테스트만으로는 부족하다** — 2026-08-15 사고는
> 단위 테스트를 통과하는 상태에서 발생했다. 로컬 실제 HTTP 확인이 완료 조건이다.

## 1. 문서 정보

| 항목 | 값 |
| --- | --- |
| 단계 | W5 |
| 상위 계획 | [30-langgraph-migration-plan.md](30-langgraph-migration-plan.md) §5 |
| 선행 단계 | [W4 Root Graph](30-4-w4-root-graph.md) |
| 후행 단계 | [W6 interrupt·공개 계약](30-6-w6-interrupt-resume.md) |
| 상태 | 대기 |
| 성격 | **전환의 실질적 스위치 지점** — 이 단계부터 운영 경로가 Graph가 된다 |

## 2. 목적과 범위

### 2.1 목적

요청이 실제로 지나가는 경로를 `WorkflowRegistry`에서 `build_workmate_graph()`로 바꾼다. W4까지 만든
Graph는 어디에도 연결돼 있지 않았고, W5에서 처음으로 운영 경로가 된다.

### 2.2 교체 지점 (전체 3곳)

| # | 위치 | 현재 | 이후 |
| --- | --- | --- | --- |
| 1 | [runtime.py:236-244](../workmate-agent/app/a2a/runtime.py#L236-L244) | `registry.execute(WorkflowRequest(...))` | Graph `ainvoke` |
| 2 | [internal_chat.py:318-327](../workmate-agent/app/internal_chat.py#L318-L327) | 동기 Skill 실행 | Graph `ainvoke` |
| 3 | [internal_chat.py:391-400](../workmate-agent/app/internal_chat.py#L391-L400) | `_ASYNC_SKILLS` 백그라운드 실행 | Graph `ainvoke` (폴링 구조 유지, D5=A) |

### 2.3 범위 내

- 위 3개 호출부 교체
- A2A 이벤트 순서 계약 유지
- 오류 매핑(`ValueError`→422, `RuntimeError`→503) 유지

### 2.4 범위 외

- 인증·Route allowlist·Agent Card ([runtime.py:85-163](../workmate-agent/app/a2a/runtime.py#L85-L163), [:313-338](../workmate-agent/app/a2a/runtime.py#L313-L338))
- `interrupt`·`INPUT_REQUIRED` (W6)
- `app/workflows/` 삭제 (W7) — W5 시점에는 아직 파일이 남아 있다

## 3. 선행 조건

| ID | 조건 | 확인 방법 |
| --- | --- | --- |
| W5-E1 | W4 완료, Root 경유 스냅샷 PASS | W4-V6 |
| W5-E2 | 멱등성 검증 PASS | W4-V3 |
| W5-E3 | Checkpointer 동작 확인 | W4-V7 |

## 4. 요구사항

| ID | 구분 | 요구사항 | 출처 |
| --- | --- | --- | --- |
| W5-R1 | 기능 | A2A `message:send` 요청이 Root Graph로 처리된다 | 계획서 §5 W5 |
| W5-R2 | 기능 | UI REST(`/messages`) 동기 경로가 Root Graph로 처리된다 | 동상 |
| W5-R3 | 기능 | `_ASYNC_SKILLS` 백그라운드 경로가 Root Graph로 처리된다 | D5=A |
| W5-R4 | 제약 | A2A 이벤트 순서 `submitted → working → artifact(last_chunk) → completed`를 유지한다 | [runtime.py:197-262](../workmate-agent/app/a2a/runtime.py#L197-L262) |
| W5-R5 | 제약 | 인증·Route allowlist·Agent Card를 변경하지 않는다 | §2.4 |
| W5-R6 | 제약 | 오류→HTTP 상태 매핑을 유지한다(`ValueError`→422, `RuntimeError`→503) | [internal_chat.py:402-425](../workmate-agent/app/internal_chat.py#L402-L425) |
| W5-R7 | 제약 | 공개 응답 필드 집합을 유지한다 | W1 스냅샷 |
| W5-R8 | 기능 | `thread_id = task_id` 규칙을 유지한다 | 현행 [runtime.py:240-241](../workmate-agent/app/a2a/runtime.py#L240-L241) |

## 5. 설계

### 5.1 교체 전후 (A2A 경로)

```
[현재]
RuntimeBootstrapExecutor.execute()
  → Task 저장 → record_message → save_checkpoint("submitted")
  → registry.execute(WorkflowRequest) → WorkflowResult
  → TaskUpdater.start_work() → Artifact 저장·발행 → complete()

[W5 이후]
RuntimeBootstrapExecutor.execute()
  → Task 저장 → record_message
  → graph.ainvoke(state, config={"configurable": {"thread_id": task_id}})
  → 종료 State → adapter.result_from_state()
  → TaskUpdater.start_work() → Artifact 저장·발행 → complete()
```

- `save_checkpoint("submitted")` 호출은 제거한다. Checkpointer가 같은 일을 대신하며, 기존 호출은 읽는
  코드가 없는 마커였다(W0 §10.2).
- Task 저장과 이벤트 발행은 그대로 둔다 — Task Store가 외부 원장이라는 경계는 변하지 않는다.

### 5.2 오류 처리 경계

현재 UI REST는 Workflow 계층의 관례적 예외를 HTTP 상태로 번역한다.

| 예외 | HTTP | 의미 |
| --- | --- | --- |
| `ValueError` | 422 | 잘못된 입력·상태 (예: "final transcript is required") |
| `RuntimeError` | 503 | 인프라·설정 미비 (`DATABASE_URL` 미설정 등) |

이 번역은 CORS 헤더 없는 500을 막기 위한 것으로, 실사용 중 발견된 문제의 대응이다
([internal_chat.py:402-425](../workmate-agent/app/internal_chat.py#L402-L425) 주석). Graph 노드에서 발생한
예외도 같은 매핑을 받아야 한다. Graph가 예외를 감싸 다른 타입으로 바꾸면 이 경로가 깨진다.

**설계 결정:** 노드는 기존 예외 타입을 그대로 올린다. Root Graph는 예외를 삼키지 않는다.

### 5.3 비동기 Skill 경로 (D5=A)

`_ASYNC_SKILLS = {"analyze_meeting", "assistant_ask"}`의 백그라운드 + 폴링 구조는 유지한다.
Graph 호출만 교체하며, `INPUT_REQUIRED` 처리는 W6에서 추가한다.

```
POST /messages (async skill)
  → Task SUBMITTED 저장 → background_tasks.add_task(...)
  → 즉시 응답(state="submitted")
  → [백그라운드] graph.ainvoke(...) → _persist_task(최종 상태)
  → 클라이언트는 GET /tasks/{id} 폴링
```

## 6. 작업 분해 (WBS)

| ID | 작업 | 선행 | 산출물 |
| --- | --- | --- | --- |
| W5-T1 | A2A Executor 교체 | — | `runtime.py` |
| W5-T2 | `save_checkpoint("submitted")` 제거 | W5-T1 | `runtime.py` |
| W5-T3 | UI REST 동기 경로 교체 | — | `internal_chat.py` |
| W5-T4 | 비동기 경로 교체 | W5-T3 | `internal_chat.py` |
| W5-T5 | 예외 전파 경로 확인·보정 | W5-T1, T3 | 오류 매핑 테스트 |
| W5-T6 | 이벤트 순서 테스트 | W5-T1 | `tests/test_runtime_boot.py` 계승분 |
| W5-T7 | 전체 스냅샷 대조(운영 경로 경유) | W5-T1~T4 | 대조 로그 |
| W5-T8 | 증빙·커밋 | W5-T7 | `result.md` |

## 7. 검증 설계

| ID | 검증 항목 | 방법 | 판정 기준 |
| --- | --- | --- | --- |
| W5-V1 | A2A 경로 | `message:send` 요청 | Graph 실행, Artifact 반환 |
| W5-V2 | 이벤트 순서 | 이벤트 큐 관찰 | submitted → working → artifact → completed |
| W5-V3 | UI 동기 경로 | `POST /messages` | 동일 응답 구조 |
| W5-V4 | UI 비동기 경로 | async Skill 요청 후 폴링 | `submitted` → `completed` |
| W5-V5 | 오류 매핑 | `ValueError`/`RuntimeError` 유발 | 422 / 503, CORS 헤더 존재 |
| W5-V6 | Route allowlist | 제외 Route 호출 | 404 또는 405 유지 |
| W5-V7 | 운영 경로 스냅샷 | W5-T7 | 전건 PASS |
| W5-V8 | `thread_id` 규칙 | Checkpoint 조회 | `thread_id == task_id` |
| W5-V9 | 전체 테스트 | 스위트 실행 | 실패 0 |

## 8. 추적성 매트릭스

| 요구사항 | 작업 | 검증 |
| --- | --- | --- |
| W5-R1 | W5-T1 | W5-V1 |
| W5-R2 | W5-T3 | W5-V3 |
| W5-R3 | W5-T4 | W5-V4 |
| W5-R4 | W5-T1, T6 | W5-V2 |
| W5-R5 | — (변경 금지) | W5-V6 |
| W5-R6 | W5-T5 | W5-V5 |
| W5-R7 | W5-T7 | W5-V7 |
| W5-R8 | W5-T1 | W5-V8 |

## 9. 완료 정의 (Exit criteria)

1. 운영 경로 3곳이 전부 Graph를 호출한다. `WorkflowRegistry` 호출이 `app/` 안에 남아 있지 않다
   (모듈 자체는 W7까지 존재).
2. W5-V2(이벤트 순서)·V5(오류 매핑)·V6(Route allowlist) PASS.
3. W5-V7(운영 경로 스냅샷) 전건 PASS.

## 10. 위험과 완화

| 위험 | 영향 | 완화 |
| --- | --- | --- |
| Graph가 예외를 감싸 오류 매핑이 깨진다 | 브라우저에 `Failed to fetch`만 표시(2026-08-15 회귀) | §5.2 설계 결정 + W5-V5 |
| 이벤트 순서가 바뀌어 SDK 클라이언트가 결과를 놓친다 | Orchestrator가 빈 결과를 읽음(2026-08-14 유형) | W5-V2 |
| `save_checkpoint` 제거로 FK 참조가 깨진다 | Task 저장 실패 | Task 저장 자체는 유지. 제거 대상은 checkpoint 쓰기 한 줄 |
| 비동기 경로에서 Graph 예외가 삼켜져 Task가 영원히 `submitted` | UI 5분 타임아웃 | 백그라운드 실행의 예외를 잡아 `FAILED`로 기록 |

## 11. 롤백·중단 기준

- W5부터는 운영 경로가 바뀌므로 롤백 비용이 올라간다. 단, `main` 브랜치는 그대로이므로 실질 롤백은
  전환 브랜치 revert다.
- **중단 기준:** W5-V5(오류 매핑) 또는 W5-V2(이벤트 순서)가 PASS하지 않으면 W6으로 진행하지 않는다.
  두 항목 모두 실사용 중 발견돼 고친 회귀의 재발 방지선이다.

## 12. 참조

- [30-langgraph-migration-plan.md](30-langgraph-migration-plan.md) §4 D5, §5 W5
- [`app/a2a/runtime.py`](../workmate-agent/app/a2a/runtime.py), [`app/internal_chat.py`](../workmate-agent/app/internal_chat.py)
- [02-a2a-interface.md](02-a2a-interface.md)
