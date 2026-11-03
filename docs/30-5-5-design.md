# W5-5 — 설계

> [30-5-w5-entrypoint-swap.md](30-5-w5-entrypoint-swap.md) §5의 상세 문서.

## 1. A2A 경로 교체

### 1.1 교체 전후

```
[현재]
RuntimeBootstrapExecutor.execute()
  ├─ Task 저장 (submitted)
  ├─ record_message()                  ← 반환값 무시(W4-D1에서 개선)
  ├─ save_checkpoint("submitted")      ← 제거 대상
  ├─ event_queue.enqueue(submitted)
  ├─ registry.execute(WorkflowRequest) ← 교체 대상
  ├─ TaskUpdater.start_work()
  ├─ Artifact 저장·발행
  └─ TaskUpdater.complete()

[W5 이후]
RuntimeBootstrapExecutor.execute()
  ├─ Task 저장 (submitted)             ← 유지 (FK 참조 때문)
  ├─ event_queue.enqueue(submitted)
  ├─ graph.ainvoke(state, config)      ← Graph가 멱등성·라우팅·검증·Artifact·영속을 담당
  ├─ TaskUpdater.start_work()
  ├─ Artifact 발행
  └─ TaskUpdater.complete()
```

### 1.2 무엇이 Graph로 들어가고 무엇이 남는가

| 항목 | W5 이후 위치 | 근거 |
| --- | --- | --- |
| Task `submitted` 저장 | **Executor에 남음** | Message·Artifact가 FK로 Task를 참조. Graph 실행 전에 있어야 한다 |
| `record_message()` | **Graph `idempotency_check`로 이동** | W4-R2 |
| `save_checkpoint("submitted")` | **제거** | Checkpointer가 대체. 읽는 코드 없음 |
| Workflow 실행 | Graph | W5-R1 |
| Artifact 저장 | Graph `persist_result` | W4-R5 |
| **이벤트 발행** | **Executor에 남음** | SDK EventQueue는 전송 계층의 일(96번 §10) |

### 1.3 이벤트 발행이 Executor에 남는 이유

[96번 §10](96-workmate-langgraph-target-architecture.md): "A2A/FastAPI — 인증, 전송 Schema, 상태·오류
매핑". EventQueue는 A2A SDK의 전송 메커니즘이다. Graph가 SDK 타입을 알면 계층이 섞인다.

Graph는 State에 결과를 담고, Executor가 그것을 SDK 이벤트로 번역한다.

### 1.4 이벤트 순서 보장

```python
await event_queue.enqueue_event(submitted)        # 1
final_state = await graph.ainvoke(state, config)  # (Graph 실행)
await updater.start_work()                        # 2
... Artifact 발행 ...                              # 3
await updater.complete()                          # 4
```

**주의:** `start_work()`가 Graph 실행 **뒤**에 오는 현재 구조를 유지한다. 순서를 "더 자연스럽게"
바꾸고 싶어질 수 있지만(실행 전에 `working`), 그것은 계약 변경이다. W5의 목적이 아니다.

---

## 2. UI REST 동기 경로 교체

### 2.1 교체 전후

```
[현재]
result = await workflow_registry().execute(WorkflowRequest(...))
 ↓ try/except로 ValueError→422, RuntimeError→503
await _persist_task(task_id, request, result, user_id)
return SkillChatMessageResponse(...)

[W5 이후]
final_state = await graph.ainvoke(state, config)
 ↓ 같은 try/except 유지
result = result_from_state(final_state)     ← W2 어댑터
return SkillChatMessageResponse(...)
```

### 2.2 `_persist_task()` 처리

현재 [internal_chat.py:238-274](../workmate-agent/app/internal_chat.py#L238)가 Task·Artifact 저장과
`record_message()`를 한다. W4의 `persist_result` 노드가 같은 일을 하므로 **중복된다.**

| 선택지 | 내용 | 평가 |
| --- | --- | --- |
| A | `_persist_task()` 제거, Graph가 전담 | 저장 형태가 A2A 경로와 통일된다 |
| B | 유지하고 Graph의 `persist_result`를 UI 경로에서 건너뜀 | 분기가 생긴다 |
| **C** | **Graph가 전담하되 `_persist_task()`의 특수 처리를 `persist_result`에 반영** | **채택** |

**설계 결정 W5-D1: C.** `_persist_task()`에는 UI 경로 고유의 처리가 있다.

```python
metadata={"mock": result.mock, "business_result": not result.mock, "warnings": result.warnings},
```

주석이 이유를 설명한다.

> `warnings`도 여기 함께 싣는다 — Task Store Snapshot(Polling으로 조회하는 값)엔 원래 Artifact만
> 남고 동기 응답의 `warnings` 필드는 저장되지 않았다. (…) `_ASYNC_SKILLS`는 결과를 Polling으로만
> 받으므로 여기 없으면 부분 실패 경고가 조용히 사라진다.

**이 처리를 잃으면 비동기 Skill의 경고가 사라진다.** `persist_result` 노드가 Artifact metadata에
`warnings`를 싣도록 한다.

---

## 3. 비동기 경로 교체

### 3.1 현재 구조

```python
async def _run_skill_in_background(task_id, request, payload, user_id) -> None:
    await _save_task_status(task_id, WORKING, user_id)
    try:
        result = await workflow_registry().execute(WorkflowRequest(...))
    except (ValueError, RuntimeError) as exc:
        await _save_task_status(task_id, FAILED, user_id, message_text=str(exc))
        return
    except Exception as exc:   # Task를 WORKING에 영원히 묶어두지 않기 위한 방어
        await _save_task_status(task_id, FAILED, user_id, message_text=f"unexpected error: {exc}")
        return
    await _persist_task(task_id, request, result, user_id)
```

### 3.2 교체 시 보존할 것

| 항목 | 이유 |
| --- | --- |
| `WORKING` 전이 | 폴링 클라이언트가 진행 중임을 안다 |
| `ValueError`/`RuntimeError` → `FAILED` + 메시지 | 폴링으로 원인을 볼 수 있다 |
| **방어적 `except Exception`** | Task가 `WORKING`에 영원히 남지 않는다 |
| `_save_task_status()`가 `record_message()`를 부르지 않는 것 | 같은 `message_id` 두 번 쓰면 `ValueError`(멱등성 Key) |

마지막 항목이 미묘하다. 주석이 설명한다.

> `_persist_task`와 달리 `record_message`를 호출하지 않는다 — 그건 같은 `message_id`를 두 번 쓰면
> `ValueError`를 내는 멱등성 Key라 최종 결과 저장 시점에 딱 한 번만 기록해야 한다.

**W4에서 멱등성을 Graph로 옮겼으므로**, Graph의 `idempotency_check`와 `persist_result`가 이 규칙을
지켜야 한다. `_save_task_status()`는 상태 전이만 하고 멱등성 Key를 건드리지 않는 구조를 유지한다.

### 3.3 Graph 실행 중 예외

Graph가 예외를 감싸면 `except (ValueError, RuntimeError)`가 안 걸린다. [W5-R6](30-5-4-requirements.md)과
같은 문제다. §4에서 다룬다.

---

## 4. 오류 경계 설계 (W5-R6)

### 4.1 문제

Workflow 계층은 관례적으로 두 예외를 쓴다.

| 예외 | 의미 | 발생 위치 예 |
| --- | --- | --- |
| `ValueError` | 잘못된 입력·상태 | "final transcript is required", "meeting not found for requested user" |
| `RuntimeError` | 인프라·설정 미비 | `DATABASE_URL` 미설정, psycopg 미설치, R2 설정 누락 |

`app/workflows/*.py` 15곳에서 `ValueError`를 쓴다.

### 4.2 Graph가 깨뜨리는 방식

LangGraph는 노드 예외를 그대로 전파하는 것이 기본이지만, 다음 경우 감싸질 수 있다.

| 상황 | 결과 |
| --- | --- |
| 노드에 `RetryPolicy`가 붙어 재시도 소진 | 원 예외가 유지되는지 확인 필요 |
| Subgraph 경계 | 동상 |
| `ainvoke` 자체의 예외 처리 | 동상 |

### 4.3 설계 결정 W5-D2 — 노드는 예외를 그대로 올린다

```
노드에서 ValueError 발생
  → Subgraph가 감싸지 않음
  → Root Graph가 감싸지 않음
  → ainvoke가 그대로 raise
  → internal_chat의 except (ValueError, RuntimeError)가 잡음
  → 422 / 503
```

**구현 규칙**
- Root 노드에서 `try/except Exception`으로 광범위하게 잡지 않는다
- 부분 실패는 `warnings`로 처리하되, 전체 실패는 예외로 올린다
- Graph 자체 오류 타입으로 변환하지 않는다

### 4.4 W8과의 관계

W8에서 `RetryPolicy`를 붙이면 재시도 소진 시 어떤 예외가 나오는지 확인해야 한다. W5에서 매핑을
고정해 두면 W8에서 깨졌을 때 바로 알 수 있다.

---

## 5. Checkpointer 수명 (W5-R10)

### 5.1 현재 앱 구조

[main.py:94](../workmate-agent/app/main.py#L94)에서 FastAPI 앱을 만들고 Router들을 등록한다. Windows
환경 설정(Selector Event Loop·IPv4 강제)도 여기 있다.

### 5.2 설계

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Checkpointer 연결을 앱 수명과 함께 연다.

    요청마다 새로 만들면 연결이 누적된다. 프로세스 단위 싱글턴으로 두고
    종료 시 정리한다.
    """
    checkpointer = await open_checkpointer()
    app.state.graph = build_workmate_graph(checkpointer=checkpointer)
    yield
    await close_checkpointer(checkpointer)
```

### 5.3 주의 — Windows

`main.py`의 Selector Event Loop 정책은 실사용 대응이다. 비동기 Checkpointer가 이 정책과 충돌하면
**Checkpointer 쪽을 조정**한다. Event Loop 설정은 더 오래된 대응이므로 건드리지 않는다
([30-2-11](30-2-11-rollback.md) §7).

---

## 6. UI REST `message_id` 문제 (W4에서 이월)

### 6.1 현재

```python
task_id = str(uuid4())                      # internal_chat.py:373
message_id = f"internal-{task_id}"          # internal_chat.py:267
```

요청마다 `task_id`가 새로 생기므로 `message_id`도 매번 다르다. **멱등성이 영원히 발동하지 않는다.**

### 6.2 이것이 문제인가

| 관점 | 판단 |
| --- | --- |
| 기능적으로 | 문제 아님 — UI는 재시도 시 새 요청으로 취급해도 된다 |
| 계약 관점 | A2A 경로와 동작이 다르다 |
| W4-D1 이후 | A2A는 멱등하고 UI REST는 아니다 — 비대칭 |

### 6.3 선택지

| | 방식 | 영향 |
| --- | --- | --- |
| **A** | **현행 유지** — UI REST는 멱등성 없음 | 없음. 비대칭이 남는다 |
| B | 클라이언트가 `message_id`를 보내게 함 | UI 수정 필요. 공개 계약 변경 |
| C | 요청 내용 해시로 `message_id` 생성 | 의도치 않은 중복 차단 가능성(같은 내용 재요청이 막힘) |

**설계 결정 W5-D3: A(현행 유지).**

근거:
- UI REST는 내부 검증 경로이고 브라우저가 재시도를 자동으로 하지 않는다
- B는 공개 계약 변경이라 W6의 범위와 겹친다 — 거기서 함께 다루는 편이 낫다
- C는 "같은 할 일을 두 번 만들기"처럼 정당한 중복 요청을 막는다

**기록:** 비대칭이 남는다는 사실을 증빙과 W9에 남긴다. W6에서 공개 계약을 개편할 때 함께 검토할
후보로 표시한다.

---

## 7. 설계 결정 요약

| ID | 결정 | 근거 |
| --- | --- | --- |
| W5-D1 | `_persist_task()`의 `warnings` metadata 처리를 `persist_result`에 반영 | §2.2 |
| W5-D2 | 노드 예외를 감싸지 않고 그대로 전파 | §4.3 |
| W5-D3 | UI REST `message_id`는 현행 유지(비대칭 기록) | §6.3 |
| W5-D4 | 이벤트 발행은 Executor에 남긴다 | §1.3 |
| W5-D5 | `start_work()` 호출 위치(Graph 실행 뒤) 유지 | §1.4 |

## 8. 참조

- [96번 §9](96-workmate-langgraph-target-architecture.md) — 영속 실행 시퀀스
- [96번 §10](96-workmate-langgraph-target-architecture.md) — 계층 책임
- [30-4-5](30-4-5-design.md) §3 — 멱등성 설계
- [`app/internal_chat.py`](../workmate-agent/app/internal_chat.py) 주석 — 각 처리의 배경
