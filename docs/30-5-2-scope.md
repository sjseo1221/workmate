# W5-2 — 목적과 범위

> [30-5-w5-entrypoint-swap.md](30-5-w5-entrypoint-swap.md) §2의 상세 문서.

## 1. 목적

요청이 실제로 지나가는 경로를 `WorkflowRegistry`에서 `build_workmate_graph()`로 바꾼다.

W4까지 만든 Graph는 어디에도 연결돼 있지 않았고, W5에서 처음으로 운영 경로가 된다.

### 1.1 이 단계의 성공 기준

**"아무 일도 일어나지 않는 것"** 이다. 사용자·오케스트레이터·UI 입장에서 W5 전후로 달라지는 것이
없어야 한다(W4-D1 멱등성 변경 제외).

| 관점 | W5 전 | W5 후 |
| --- | --- | --- |
| A2A 응답 | 동일 | 동일 |
| UI REST 응답 | 동일 | 동일 |
| 이벤트 순서 | `submitted → working → artifact → completed` | 동일 |
| 오류 코드 | 422 / 503 | 동일 |
| 내부 | Registry dict 조회 | Root Graph |

## 2. 교체 지점 (전체 3곳)

| # | 위치 | 현재 | 이후 |
| --- | --- | --- | --- |
| 1 | [runtime.py:236-244](../workmate-agent/app/a2a/runtime.py#L236) | `registry.execute(WorkflowRequest(...))` | `graph.ainvoke(state, config)` |
| 2 | [internal_chat.py:318-327](../workmate-agent/app/internal_chat.py#L318) | 동기 Skill 실행 | 동일 |
| 3 | [internal_chat.py:391-400](../workmate-agent/app/internal_chat.py#L391) | `_ASYNC_SKILLS` 백그라운드 실행 | 동일 (폴링 구조 유지, D5=A) |

### 2.1 세 지점이 다른 점

| # | 실행 방식 | 응답 시점 | 오류 처리 |
| --- | --- | --- | --- |
| 1 | A2A SDK Executor 안 | 이벤트 큐로 발행 | SDK 경유 |
| 2 | 요청 처리 중 동기 | 즉시 응답 | `ValueError`→422, `RuntimeError`→503 |
| 3 | `background_tasks` | 즉시 `submitted` 응답 후 백그라운드 | **예외가 삼켜지면 Task가 영원히 `submitted`** |

3번의 오류 처리가 가장 취약하다. 현재 [`_run_skill_in_background()`](../workmate-agent/app/internal_chat.py#L303)이
어떻게 실패를 다루는지 확인하고 보존한다.

## 3. 범위 내 (In scope)

| ID | 항목 | 산출물 |
| --- | --- | --- |
| S1 | 교체 지점 3곳 | `runtime.py`, `internal_chat.py` |
| S2 | `save_checkpoint("submitted")` 호출 제거 | `runtime.py` |
| S3 | Checkpointer 수명 관리(앱 lifespan 결합) | `main.py` |
| S4 | 예외 전파 경로 확인·보정 | 테스트 |
| S5 | 이벤트 순서 테스트 | `test_runtime_boot.py` 계승 |
| S6 | 운영 경로 경유 스냅샷 대조 | 대조 로그 |
| S7 | UI REST `message_id` 방침 결정 | [30-5-5](30-5-5-design.md) §6 |

### 3.1 S2 — `save_checkpoint` 제거

현재 [runtime.py:228-233](../workmate-agent/app/a2a/runtime.py#L228)이 `{task_id}:submitted` 마커를
쓴다. W0 조사 결과 **읽는 코드가 없다.** Checkpointer가 같은 일을 하므로 제거한다.

다만 **Task 저장 자체는 유지한다.** 주석이 이유를 설명한다.

> Message·Checkpoint·Artifact가 FK로 Task Snapshot을 참조하므로 SDK EventQueue보다 먼저 최소 Task를
> 영속화한다.

즉 `task_store.save(submitted, ...)`와 `record_message(...)`는 남고, `save_checkpoint(...)` 한 덩어리만
제거한다.

### 3.2 S7 — W4에서 넘어온 문제

W4에서 멱등성을 제대로 구현하면([W4-D1](30-4-5-design.md) §3), UI REST 경로의 `message_id` 생성
방식이 문제가 된다.

```python
# internal_chat.py:267 — task_id가 매 요청 새 uuid4()
message_id=f"internal-{task_id}",
```

매번 다르므로 멱등성이 영원히 발동하지 않는다. W5에서 방침을 정한다([30-5-5](30-5-5-design.md) §6).

## 4. 범위 외 (Out of scope)

| 항목 | 담당 | 이유 |
| --- | --- | --- |
| 인증(JWT·JWKS·Service Token) | — | [runtime.py:85-163](../workmate-agent/app/a2a/runtime.py#L85), [internal_chat.py:53-157](../workmate-agent/app/internal_chat.py#L53). Graph 진입 전 |
| Agent Card | — | 공개 Skill 목록은 변하지 않는다 |
| Route allowlist | — | [runtime.py:313-338](../workmate-agent/app/a2a/runtime.py#L313). 5개 유지 |
| 입력 Schema 검증 | — | [internal_chat.py:369-372](../workmate-agent/app/internal_chat.py#L369). 전송 계층의 일 |
| **`interrupt`·`INPUT_REQUIRED`** | [W6](30-6-w6-interrupt-resume.md) | 확인 흐름 개편 |
| 스트리밍 전환 | 별건 | D5=A로 폴링 유지 |
| `app/workflows/` 삭제 | [W7](30-7-w7-legacy-removal.md) | W5 시점에는 파일이 남아 있다 |
| UI(`AssistantDrawer.tsx`) 수정 | W6 | W5에서는 UI가 볼 변화가 없다 |

### 4.1 특히 주의 — Route allowlist

`AGENTS.md`: "공식 SDK가 제공하는 Route를 전부 공개하지 않는다. 승인된 MVP Route allowlist만 등록하고
제외 Route의 `404` 또는 `405` Contract Test를 유지한다."

W5는 allowlist를 바꾸지 않지만, Executor를 손대면서 Route 등록이 영향받을 수 있다. W5-V6에서 확인한다.

### 4.2 W5에서 UI를 안 고치는 이유

D5=A(폴링 유지)이므로 UI가 보는 응답 형태가 그대로다. UI 수정은 W6에서 `INPUT_REQUIRED`가 생길 때
필요해진다.

## 5. 범위 변경 절차

| 상황 | 처리 |
| --- | --- |
| 오류 매핑을 보정해야 함 | 범위 내(S4). 기존 매핑을 **유지하는 방향**으로만 |
| 이벤트 순서 조정 필요 | 범위 내. 단 공개 계약이므로 기존 순서 유지 |
| Route allowlist 변경 필요 | **범위 이탈.** 보고 |
| 인증 코드 수정 필요 | 범위 이탈. 보고 |
| UI 수정 필요 | W5에서 필요해졌다면 무언가 잘못됐다. 원인 조사 |
| `message_id` 방침 변경 | 범위 내(S7). 단 공개 계약에 영향 있으면 보고 |

## 6. 참조

- [96번 §9](96-workmate-langgraph-target-architecture.md) — 영속 실행 시퀀스
- [96번 §10](96-workmate-langgraph-target-architecture.md) — A2A/FastAPI 계층의 책임
- [30-5-5](30-5-5-design.md) — 교체 설계
