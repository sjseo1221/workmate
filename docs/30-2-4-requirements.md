# W2-4 — 요구사항 명세

> [30-2-w2-graph-foundation.md](30-2-w2-graph-foundation.md) §4의 상세 문서.

각 요구사항을 **설명 / 근거 / 수용 기준 / 검증 / 우선순위** 형식으로 기술한다.
우선순위는 `필수`(미충족 시 W2 미완료), `중요`(미충족 시 후행 단계에 조건부 전달), `권장`으로 구분한다.

## 요약

| ID | 구분 | 한 줄 | 우선순위 | 검증 |
| --- | --- | --- | --- | --- |
| W2-R1 | 기능 | `WorkmateState`를 TypedDict로 정의 | 필수 | W2-V1 |
| W2-R2 | 기능 | `warnings` 누적 Reducer | 필수 | W2-V1 |
| W2-R3 | 제약 | 식별자 5종 불변 | 필수 | W2-V2 |
| W2-R4 | 제약 | Secret을 State에 담지 않음 | 필수 | W2-V9 |
| W2-R5 | 기능 | 경계 어댑터 왕복 변환 | 필수 | W2-V3 |
| W2-R6 | 기능 | Checkpointer 백엔드 자동 선택 | 필수 | W2-V5 |
| W2-R7 | 기능 | `thread_id` 기반 저장·복원·이력 | 필수 | W2-V4 |
| W2-R8 | 기능 | `langchain-openai` 모델 객체 사용 | 필수 | W2-V6 |
| W2-R9 | 제약 | 네트워크 오류만 재시도 | **필수(최우선)** | W2-V7 |
| W2-R10 | 제약 | `temperature=0` + strict 구조화 출력 유지 | 필수 | W2-V6 |
| W2-R11 | 제약 | Checkpointer와 Task Store 책임 분리 | 필수 | W2-V4, 설계 검토 |

---

## W2-R1 — State 정의

**설명** [96번 §3](96-workmate-langgraph-target-architecture.md)의 `WorkmateState`를 `TypedDict`로
정의한다. 필드 집합은 96번 문서를 그대로 따르며, 이번에 임의로 추가·삭제하지 않는다.

**근거** Skill 11개가 공유하는 자료구조이므로 W3 이전에 확정돼야 한다. 96번 문서는 승인된 목표
설계이고, W2는 그것을 구현으로 옮기는 단계다.

**수용 기준**
- `request_id`·`message_id`·`task_id`·`thread_id`·`user_id`·`skill_id` 식별자 6종 존재
- `input`·`now`·`timezone` 실행 문맥 존재
- `source_data`·`normalized_items`·`warnings`·`pending_action` 중간 상태 존재
- `task_state`·`result`·`markdown`·`error` 결과 필드 존재
- `task_state`는 96번 §3의 7개 값만 허용

**검증** W2-V1 / **우선순위** 필수

---

## W2-R2 — `warnings` 누적 Reducer

**설명** `warnings` 채널은 노드별 값을 덮어쓰지 않고 누적한다(`Annotated[list, add]`).

**근거** W3의 `daily_briefing`은 Gmail·Calendar·Task를 **병렬 노드**로 수집한다. 두 노드가 동시에
경고를 남길 때 덮어쓰기 기본값이면 하나가 사라진다. 96번 §11-6("Provider 일부 실패는 사용 가능한
결과와 `warnings`를 보존한다")이 깨진다.

**수용 기준**
- 두 노드가 각각 경고를 추가했을 때 결과 State에 둘 다 존재
- 순서는 superstep 순서를 따르되, 같은 superstep 내 순서는 보장하지 않는다(테스트에서 순서 비의존
  단언 사용)

**검증** W2-V1 / **우선순위** 필수

---

## W2-R3 — 식별자 불변식

**설명** `user_id`·`request_id`·`message_id`·`task_id`·`thread_id`는 실행 중 변경되지 않는다.

**근거** [96번 §11-2](96-workmate-langgraph-target-architecture.md). 이 값들이 중간에 바뀌면 권한
범위(`user_id`)·멱등성(`message_id`)·재개 지점(`thread_id`)이 모두 무너진다. 특히 `user_id`가
바뀌면 타 사용자 데이터 접근이 되므로 보안 문제다.

**수용 기준**
- 노드가 식별자를 변경하려 시도하면 테스트가 이를 검출한다
- 종료 State의 식별자 5종이 초기 State와 동일

**구현 방식** 런타임 강제(Reducer에서 변경 거부)와 테스트 검출 중 **후자를 기본**으로 한다. 런타임
강제는 정상 흐름에 비용을 더하고, 이 불변식은 코드 리뷰와 테스트로 충분히 지킬 수 있다. 단, 테스트는
"우연히 안 바뀜"이 아니라 "바꾸려 하면 실패"를 확인해야 한다.

**검증** W2-V2 / **우선순위** 필수

---

## W2-R4 — Secret 비저장

**설명** Secret·Token·API Key·Presigned URL·원본 개인정보를 State에 담지 않는다.

**근거** 96번 §3, `AGENTS.md` 금지 사항. State는 Checkpointer를 통해 **DB에 영속화**된다. 지금까지
메모리에만 있던 값이 W2 이후 디스크에 남는다는 점이 중요하다. 기존 코드 기준으로 "State에 담기지
않던 값"이 자동으로 안전한 것이 아니다.

**수용 기준**
- State 직렬화 결과에 토큰·키 패턴이 검출되지 않는다
- Gmail 메시지 원문·회의 녹취 원문처럼 큰 개인정보는 State에 싣지 않고 식별자로 참조한다

**검증** W2-V9 / **우선순위** 필수

---

## W2-R5 — 경계 어댑터

**설명** 전송 payload → State, 종료 State → 공개 응답 구조의 왕복 변환을 제공한다.

**근거** 공개 응답 모양을 한 지점에 가둬 두면, W3에서 Skill을 재작성해도 계약이 흔들리지 않는다.
W7에서 `WorkflowResult`가 삭제된 뒤에도 같은 필드 집합을 유지해야 W1 스냅샷과 대조할 수 있다.

**수용 기준**
- `state_from_request()`가 식별자·payload·실행 문맥을 손실 없이 State로 옮긴다
- `result_from_state()`가 `artifact_name`·`artifact_description`·`text`·`data`·`markdown`·`state`·
  `warnings`·`mock` 8개 필드를 산출한다
- 왕복(payload → State → 결과) 후 입력 식별자가 보존된다

**검증** W2-V3 / **우선순위** 필수

---

## W2-R6 — Checkpointer 백엔드 선택

**설명** `DATABASE_URL`이 있으면 PostgreSQL Saver, 없으면 SQLite Saver를 쓴다.

**근거** [`build_task_store()`](../workmate-agent/app/a2a/runtime.py#L402)가 이미 같은 규칙을 쓴다.
두 저장소가 서로 다른 규칙으로 백엔드를 고르면 "Task는 Postgres인데 Checkpoint는 SQLite" 같은
상태가 생긴다.

**수용 기준**
- `DATABASE_URL` 설정 시 Postgres Saver 반환
- 미설정 시 SQLite Saver 반환, 경로는 Task Store와 같은 규칙(`.runtime/` 하위)
- 두 경우 모두 실제 저장·복원이 동작

**검증** W2-V5 / **우선순위** 필수

---

## W2-R7 — thread 기반 저장·복원·이력

**설명** `thread_id`로 State를 저장하고 복원하며, 이력을 조회할 수 있다.

**근거** [96번 §7](96-workmate-langgraph-target-architecture.md). W6의 `interrupt`/`resume`이
성립하려면 "멈춘 지점의 State"를 정확히 복원할 수 있어야 한다.

**수용 기준**
- 같은 `thread_id`로 2회 실행 시 이력이 누적된다
- `get_state_history()`로 노드별 Snapshot을 조회할 수 있다
- `thread_id = task_id` 규칙이 유지된다

**검증** W2-V4 / **우선순위** 필수

---

## W2-R8 — `langchain-openai` 모델 객체

**설명** LLM 호출을 `urllib` 직접 호출에서 `langchain-openai` 모델 객체로 바꾼다.

**근거** D3=B(사용자 결정, 2026-09-23). LangGraph 생태계의 표준 방식을 익히는 것이 학습 목적에 부합한다.

**수용 기준**
- W3 Skill이 사용하는 LLM 경로가 모델 객체를 통한다
- 범위 밖 호출자와 공유되는 모듈의 처리는 [30-2-5](30-2-5-design.md) §5.3을 따른다

**검증** W2-V6 / **우선순위** 필수

---

## W2-R9 — 재시도 정책 보존 (최우선)

**설명** **네트워크 계층 오류만 재시도하고, HTTP 4xx/5xx는 즉시 실패한다.**

**근거** [assistant_router.py:295-305](../workmate-agent/app/workflows/assistant_router.py#L295-L305).
2026-08-19 실사용 중 Windows 환경의 간헐적 DNS 실패(`getaddrinfo failed`)로 `assistant_ask` 전체가
500으로 죽는 문제가 재현됐다. 대응으로 재시도를 추가하되, HTTP 오류는 재시도해도 같은 결과이므로
**재시도 대상에서 명시적으로 제외**했다.

`langchain-openai`의 기본 재시도는 429·5xx를 재시도한다. 그대로 두면 이 구분이 사라지고, 장애 시
지연이 증폭된다.

**수용 기준**
- 모델 객체의 라이브러리 재시도가 꺼져 있다(`max_retries=0`)
- 네트워크 오류: 최대 3회 시도
- HTTP 4xx/5xx: 1회 시도 후 즉시 실패
- 현재 상수(`_CHAT_COMPLETION_MAX_ATTEMPTS = 3`, timeout 30초)와 동등

**검증** W2-V7 / **우선순위** **필수(최우선)** — 계획서 §9-6 완료 조건

---

## W2-R10 — 구조화 출력 동작 유지

**설명** `temperature=0`과 JSON Schema strict 구조화 출력 동작을 유지한다.

**근거** 현재 [assistant_router.py:276-283](../workmate-agent/app/workflows/assistant_router.py#L276-L283)은
`response_format: {"type": "json_schema", "json_schema": {..., "strict": True}}`를 쓴다. Router가
`skill_id`·`arguments`를 결정하는 경로이므로 응답 형태가 흔들리면 라우팅이 실패한다.

`with_structured_output`은 Provider와 모델에 따라 function calling·json_mode·json_schema 중 하나로
동작하며, 어느 것이 선택되는지에 따라 결과가 달라질 수 있다.

**수용 기준**
- 같은 Schema·프롬프트에 대해 기존 경로와 동일한 구조의 결과를 얻는다
- 결정성 확보를 위해 `temperature=0`이 전달된다
- strict 모드가 유지되거나, 유지되지 않는 경우 그 사실과 대체 검증 수단이 기록된다

**검증** W2-V6 / **우선순위** 필수

---

## W2-R11 — 저장소 책임 분리

**설명** LangGraph Checkpointer와 A2A Task Store의 책임을 합치지 않는다.

**근거** [96번 §10](96-workmate-langgraph-target-architecture.md) 경계표.

| 저장소 | 소유 | 소유하지 않음 |
| --- | --- | --- |
| A2A Task Store | 외부 Task 상태, Artifact, `message_id` 멱등성 | Graph 내부 노드 State |
| Checkpointer | 내부 State, 재개 지점, interrupt payload | 외부 Task 상태 원장 |

둘을 합치면 "외부에 이미 응답한 요청"과 "내부 실행 재개"가 한 저장소에 섞여, 장애 복구 시 어느 쪽이
진실인지 판정할 수 없다.

**수용 기준**
- Checkpointer가 Task 상태·Artifact를 쓰지 않는다
- Task Store가 노드 State를 쓰지 않는다
- 두 저장소의 연결은 `task_id ↔ thread_id`뿐이다

**검증** W2-V4 + 설계 검토 / **우선순위** 필수

---

## 요구사항 간 의존

```
W2-R1 (State) ─┬→ W2-R2 (Reducer)
               ├→ W2-R3 (불변식)
               ├→ W2-R4 (Secret)
               └→ W2-R5 (어댑터)

W2-R6 (백엔드) ─→ W2-R7 (thread) ─→ W2-R11 (책임 분리)

W2-R8 (모델 객체) ─┬→ W2-R9 (재시도)
                   └→ W2-R10 (구조화 출력)
```

State 계열(R1~R5), Checkpointer 계열(R6·R7·R11), LLM 계열(R8~R10)은 서로 독립이므로 병렬 작업이
가능하다([30-2-6](30-2-6-wbs.md) §3).

## 참조

- [30-2-5](30-2-5-design.md) — 각 요구사항의 구현 설계
- [30-2-7](30-2-7-verification.md) — 검증 케이스 상세
- [30-2-8](30-2-8-traceability.md) — 요구사항↔작업↔검증 대응
