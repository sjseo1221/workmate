# W5-4 — 요구사항 명세

> [30-5-w5-entrypoint-swap.md](30-5-w5-entrypoint-swap.md) §4의 상세 문서.

## 요약

| ID | 구분 | 한 줄 | 우선순위 | 검증 |
| --- | --- | --- | --- | --- |
| W5-R1 | 기능 | A2A `message:send`가 Root Graph로 처리 | 필수 | W5-V1 |
| W5-R2 | 기능 | UI REST 동기 경로가 Root Graph로 처리 | 필수 | W5-V3 |
| W5-R3 | 기능 | `_ASYNC_SKILLS` 백그라운드 경로가 Root Graph로 처리 | 필수 | W5-V4 |
| W5-R4 | 제약 | **A2A 이벤트 순서 유지** | **필수(계약)** | W5-V2 |
| W5-R5 | 제약 | 인증·Route allowlist·Agent Card 무변경 | 필수 | W5-V6 |
| W5-R6 | 제약 | **오류→HTTP 매핑 유지** | **필수(계약)** | W5-V5 |
| W5-R7 | 제약 | 공개 응답 필드 집합 유지 | 필수 | W5-V7 |
| W5-R8 | 기능 | `thread_id = task_id` 규칙 유지 | 필수 | W5-V8 |
| W5-R9 | 기능 | 백그라운드 실패가 `FAILED` Task로 드러남 | **필수** | W5-V4 |
| W5-R10 | 기능 | Checkpointer 수명이 앱과 함께 관리됨 | 필수 | W5-V9 |

---

## W5-R1 — A2A 경로

**설명** A2A `message:send` 요청이 Root Graph로 처리된다.

**수용 기준**
- [runtime.py:236-244](../workmate-agent/app/a2a/runtime.py#L236)의 `registry.execute()`가
  `graph.ainvoke()`로 교체됨
- `config={"configurable": {"thread_id": task_id}}` 전달
- 결과가 어댑터를 거쳐 Artifact로 변환됨
- `app/` 안에 `workflow_registry()` 호출이 남지 않음

**검증** W5-V1 / **우선순위** 필수

---

## W5-R2 — UI REST 동기 경로

**설명** `POST /api/v1/internal/skill-chat/messages`의 동기 Skill 실행이 Root Graph로 처리된다.

**수용 기준**
- [internal_chat.py:318-327](../workmate-agent/app/internal_chat.py#L318) 교체
- 응답 구조 동일(`skill_id`·`input_type`·`input`·`task_id`·`state`·`artifact`·`warnings`)
- `artifact` dict의 8개 키 유지(`name`·`description`·`text`·`data`·`markdown`·`mock`·
  `business_result`)

**검증** W5-V3 / **우선순위** 필수

---

## W5-R3 — 비동기 경로

**설명** `_ASYNC_SKILLS`(`analyze_meeting`·`assistant_ask`)의 백그라운드 실행이 Root Graph로 처리된다.

**근거** D5=A — 폴링 구조를 유지하고 Graph 호출만 교체한다.

**수용 기준**
- [`_run_skill_in_background()`](../workmate-agent/app/internal_chat.py#L303)의 Workflow 호출 교체
- 즉시 `state="submitted"` 응답
- `WORKING` 전이 유지
- 완료 시 `_persist_task()`로 최종 상태 기록

**검증** W5-V4 / **우선순위** 필수

---

## W5-R4 — 이벤트 순서 (계약)

**설명** A2A 이벤트가 `submitted → working → artifact(last_chunk) → completed` 순으로 발행된다.

**근거** [runtime.py:197-205](../workmate-agent/app/a2a/runtime.py#L197)의 Docstring이 이를 계약으로
명시한다.

> Contract: The first event is a submitted ``Task``. Status, artifact, and completed events follow
> in that order.

**과거 사고** 2026-08-14 — `_artifact_parts`가 구조화 `data`만 있는 결과에서 `text` Part를 생략해
Orchestrator가 `COMPLETED`인데도 빈 결과를 읽었다. 이벤트 자체는 순서대로 왔지만 **내용이 비어
있었다.** W5에서는 순서와 내용 둘 다 확인한다.

**수용 기준**
- 이벤트 4종이 순서대로 발행
- `artifact` 이벤트에 `last_chunk=True`
- Artifact Part에 `text/plain`이 포함됨(구조화 결과에도)

**검증** W5-V2 / **우선순위** **필수(공개 계약)**

---

## W5-R5 — 전송 계층 무변경

**설명** 인증·Route allowlist·Agent Card를 변경하지 않는다.

**근거** [96번 §10](96-workmate-langgraph-target-architecture.md): "A2A/FastAPI — 인증, 전송 Schema,
상태·오류 매핑 / 업무 규칙, Provider 직접 호출은 하지 않는다."

`AGENTS.md`: "공식 SDK가 제공하는 Route를 전부 공개하지 않는다. 승인된 MVP Route allowlist만 등록하고
제외 Route의 `404` 또는 `405` Contract Test를 유지한다."

**수용 기준**
- Route allowlist 5개 유지(`message:send`·`message:stream`·`tasks/{id}`·`tasks/{id}:cancel`·
  `tasks/{id}:subscribe`)
- 제외 Route가 404/405를 유지
- Agent Card의 Skill 11개 불변
- JWT·JWKS·Service Token 코드 무수정

**검증** W5-V6 / **우선순위** 필수

---

## W5-R6 — 오류 매핑 (계약)

**설명** Workflow 계층 예외가 정의된 HTTP 상태로 변환된다.

| 예외 | HTTP | 의미 |
| --- | --- | --- |
| `ValueError` | 422 | 잘못된 입력·상태 (예: "final transcript is required") |
| `RuntimeError` | 503 | 인프라·설정 미비 (`DATABASE_URL` 미설정 등) |

**근거** [internal_chat.py:402-425](../workmate-agent/app/internal_chat.py#L402)의 주석이 배경을
설명한다.

> 잡지 않으면 이 미들웨어 체인(`verify_a2a_headers`가 CORSMiddleware 바깥에 있음)에서는 예외가
> Starlette의 최상위 ServerErrorMiddleware까지 그대로 올라가 CORS 헤더 없는 500을 반환한다 —
> 브라우저는 이를 읽지 못해 실제 오류 메시지 대신 `TypeError: Failed to fetch`만 보게 된다
> (2026-08-15 실사용 중 발견).

**Graph 도입으로 깨지는 방식:** Graph가 노드 예외를 자체 예외로 감싸면 `ValueError`/`RuntimeError`
매핑이 안 걸린다.

**수용 기준**
- 노드에서 발생한 `ValueError`가 그대로 올라와 422가 된다
- `RuntimeError`가 503이 된다
- 응답에 CORS 헤더가 있다
- Graph가 예외를 삼키지 않는다

**검증** W5-V5 / **우선순위** **필수(공개 계약)**

---

## W5-R7 — 응답 필드 유지

**설명** 공개 응답의 필드 집합이 그대로다.

**수용 기준**
- 운영 경로를 경유한 스냅샷 대조 전건 PASS
- A2A Artifact 구조 동일
- UI REST 응답 구조 동일

**검증** W5-V7 / **우선순위** 필수

---

## W5-R8 — `thread_id` 규칙

**설명** `thread_id = task_id`를 유지한다.

**근거** 현재 [runtime.py:240-241](../workmate-agent/app/a2a/runtime.py#L240)과
[internal_chat.py:321-322](../workmate-agent/app/internal_chat.py#L321)이 모두 이 규칙을 쓴다.
W6의 resume이 `thread_id`로 재개하므로 규칙이 흔들리면 안 된다.

**수용 기준**
- 세 진입점 모두 `thread_id = task_id`
- Checkpoint 조회 시 `task_id`로 찾을 수 있다

**검증** W5-V8 / **우선순위** 필수

---

## W5-R9 — 백그라운드 실패 노출

**설명** 백그라운드 실행이 실패하면 `FAILED` Task의 `status.message`로 드러난다.

**근거** [`_run_skill_in_background()`](../workmate-agent/app/internal_chat.py#L303)의 Docstring.

> 동기 경로는 `ValueError`/`RuntimeError`를 422/503으로 바로 돌려주지만, 여긴 이미 요청이 끝난
> 뒤라 그럴 수 없다 — 실패 원인을 `FAILED` Task의 `status.message`에 담아 Polling으로 드러낸다.

현재 구현은 `ValueError`·`RuntimeError`와 **그 외 모든 예외**를 잡아 `FAILED`로 기록한다. 마지막
`except Exception`에는 주석이 있다: "Task를 WORKING에 영원히 묶어두지 않기 위한 방어".

**수용 기준**
- Graph 실행 중 예외가 나도 Task가 `WORKING`에 남지 않는다
- 실패 원인이 `status.message`에 담긴다
- 방어적 `except Exception`이 유지된다

**검증** W5-V4 / **우선순위** **필수**

---

## W5-R10 — Checkpointer 수명

**설명** Checkpointer 연결이 앱 수명과 함께 열리고 닫힌다.

**근거** `AsyncSqliteSaver`·`AsyncPostgresSaver`는 연결을 보유한다. 요청마다 새로 만들면 연결이
누적된다([30-2-5](30-2-5-design.md) §4.5).

**수용 기준**
- 프로세스 단위 싱글턴
- 앱 lifespan에서 정리
- Windows Selector Event Loop와 충돌하지 않는다

**검증** W5-V9 / **우선순위** 필수

---

## 요구사항 간 의존

```
W5-R1, R2, R3 (교체 3곳)
   ├→ W5-R4 (이벤트 순서)      ← R1에만 해당
   ├→ W5-R6 (오류 매핑)        ← R2, R3에 해당
   ├→ W5-R7 (응답 필드)        ← 전부
   └→ W5-R8 (thread_id)        ← 전부

W5-R9 (백그라운드 실패) ← R3의 부속
W5-R10 (Checkpointer 수명) ← 전부의 전제
W5-R5 (전송 계층 무변경) ← 경계 조건
```

## 참조

- [96번 §9·§10](96-workmate-langgraph-target-architecture.md)
- [30-5-5](30-5-5-design.md) — 구현 설계
- [30-5-7](30-5-7-verification.md) — 검증 케이스
