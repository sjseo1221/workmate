# W5-12 — 참조 자료

> [30-5-w5-entrypoint-swap.md](30-5-w5-entrypoint-swap.md) §12의 상세 문서.

"무엇을 참조하는가"가 아니라 **"어디를 왜 읽는가"** 를 기록한다.

## 1. 설계 근거 문서

### 96-workmate-langgraph-target-architecture.md

| 절 | 읽는 이유 | 대응 |
| --- | --- | --- |
| §9 영속 실행 시퀀스 | **진입점 → Task Store → Graph → Checkpointer의 순서** | W5 전체 설계 |
| §10 구현 경계 | "A2A/FastAPI — 인증, 전송 Schema, 상태·오류 매핑" | W5-R5, W5-D4 |
| §7 Task 상태 | 상태 전이 규칙 | W5-R9 |
| §8 오류·재시도 | "HTTP 계층 재시도는 Orchestrator가 같은 `message_id`로 담당" | W5-K8 판단 근거 |

§9의 시퀀스가 W5가 만들려는 구조다. 특히 **Task 저장이 Graph 실행보다 앞**이라는 점을 확인한다.

### 30-langgraph-migration-plan.md

| 절 | 읽는 이유 |
| --- | --- |
| §0.1 전제 | "운영 배포 중이 아니다" — W5의 위험 감수 근거 |
| §4 D5 | 폴링 유지 결정 |
| §5 W5 | 단계 정의 |
| §7.1 | 스위치오버와 롤백 |

## 2. 코드 참조 — 교체 대상

### 2.1 A2A 진입점

| 위치 | 읽는 이유 |
| --- | --- |
| [runtime.py:197-205](../workmate-agent/app/a2a/runtime.py#L197) | **`execute()` Docstring의 이벤트 순서 계약** — W5-R4의 출처 |
| [runtime.py:206-221](../workmate-agent/app/a2a/runtime.py#L206) | payload 추출, Task `submitted` 저장. **주석: FK 참조 때문에 EventQueue보다 먼저** |
| [runtime.py:222-233](../workmate-agent/app/a2a/runtime.py#L222) | `record_message()`(W4로 이동), `save_checkpoint()`(제거 대상) |
| [runtime.py:234-244](../workmate-agent/app/a2a/runtime.py#L234) | **교체 지점 1** — `registry.execute(WorkflowRequest(...))` |
| [runtime.py:245-262](../workmate-agent/app/a2a/runtime.py#L245) | `TaskUpdater` 사용, Artifact 발행 순서 |
| [runtime.py:265-275](../workmate-agent/app/a2a/runtime.py#L265) | `_payload()` — 입력 추출 방식 |
| [runtime.py:276-287](../workmate-agent/app/a2a/runtime.py#L276) | `cancel()` — W5 범위 밖이지만 W6에서 관련 |
| [runtime.py:289-312](../workmate-agent/app/a2a/runtime.py#L289) | **`_artifact_parts()`** — text Part 처리. W4로 이관됐는지 확인 |
| [runtime.py:313-338](../workmate-agent/app/a2a/runtime.py#L313) | Route allowlist — **변경 금지**(W5-R5) |

### 2.2 UI REST 진입점

| 위치 | 읽는 이유 |
| --- | --- |
| [internal_chat.py:349-373](../workmate-agent/app/internal_chat.py#L349) | 요청 검증, `task_id` 생성, `_ASYNC_SKILLS` 분기 |
| [internal_chat.py:374-388](../workmate-agent/app/internal_chat.py#L374) | 비동기 즉시 응답 구조 |
| [internal_chat.py:390-400](../workmate-agent/app/internal_chat.py#L390) | **교체 지점 2** — 동기 실행 |
| [internal_chat.py:401-425](../workmate-agent/app/internal_chat.py#L401) | **오류 매핑 주석** — W5-R6의 출처. 2026-08-15 배경 |
| [internal_chat.py:426-443](../workmate-agent/app/internal_chat.py#L426) | 응답 구조 — `artifact` dict 7개 키 |
| [internal_chat.py:238-274](../workmate-agent/app/internal_chat.py#L238) | `_persist_task()` — **`warnings` metadata 주석**(W5-D1) |
| [internal_chat.py:276-301](../workmate-agent/app/internal_chat.py#L276) | `_save_task_status()` — **`record_message()`를 안 부르는 이유** |
| [internal_chat.py:303-334](../workmate-agent/app/internal_chat.py#L303) | **교체 지점 3** + 예외 처리 3단 |
| [internal_chat.py:444-462](../workmate-agent/app/internal_chat.py#L444) | 폴링 Route — 변경하지 않지만 W6에서 관련 |

### 2.3 앱 구성

| 위치 | 읽는 이유 |
| --- | --- |
| [main.py](../workmate-agent/app/main.py) | Selector Event Loop·IPv4 설정(유지), Router 등록, CORS 미들웨어 순서 |
| [main.py:94-113](../workmate-agent/app/main.py#L94) | FastAPI 앱 생성과 미들웨어 — **lifespan 추가 지점** |

**CORS 미들웨어 순서가 중요하다.** `verify_a2a_headers`가 `CORSMiddleware` 바깥에 있다는 사실이
2026-08-15 사고의 배경이다.

## 3. 과거 회귀 기록 — 반드시 읽는다

W5에서 재발하면 안 되는 다섯 건이다. **HANDOFF.md의 해당 항목과 코드 주석을 함께 읽는다.**

| # | 회귀 | 시점 | 코드 주석 위치 |
| --- | --- | --- | --- |
| 1 | 구조화 결과에서 `text` Part 생략 → Orchestrator가 빈 결과 | 2026-08-14 | HANDOFF `### 2026-08-14 Orchestrator 채팅 Skill 라우팅 연동` |
| 2 | CORS 헤더 없는 500 → `Failed to fetch` | 2026-08-15 | [internal_chat.py:402-425](../workmate-agent/app/internal_chat.py#L402) |
| 3 | 비동기 Task가 `WORKING`에 갇힘 | 2026-08-16 | [internal_chat.py:331-333](../workmate-agent/app/internal_chat.py#L331) |
| 4 | 비동기 결과의 `warnings` 유실 | 2026-08-16 | [internal_chat.py:252-258](../workmate-agent/app/internal_chat.py#L252) |
| 5 | `data`가 비면 프론트가 `null`만 읽음 | 2026-08-16 | [daily_briefing.py:299-306](../workmate-agent/app/workflows/daily_briefing.py#L299) |

**주석을 읽는 것이 문서를 읽는 것보다 정확하다.** 코드 주석에는 재현 조건과 증상이 구체적으로
적혀 있다.

## 4. 테스트 참조 — 기준선

W5-T0에서 확인·보강할 대상이다.

| 테스트 | 확인할 것 |
| --- | --- |
| [test_runtime_boot.py](../workmate-agent/tests/test_runtime_boot.py) | 이벤트 순서, Artifact 구성 |
| [test_internal_chat.py](../workmate-agent/tests/test_internal_chat.py) | 오류 매핑 422/503, 비동기 경로, 폴링 |
| [test_contract.py](../workmate-agent/tests/test_contract.py) | Route allowlist, 제외 Route 404/405 |
| [test_m51_legacy_adapter.py](../workmate-agent/tests/test_m51_legacy_adapter.py) | 어댑터가 기대하는 응답 형태 — W5 변경의 영향 확인 |

### 4.1 `test_m51_legacy_adapter.py`를 읽는 이유

W5는 어댑터를 고치지 않지만, 어댑터가 기대하는 응답 형태가 바뀌면 깨진다. 특히

- 이벤트 순서 변화 → 어댑터가 결과를 놓침
- 멱등성 변경 → 재시도 시 응답이 달라짐

## 5. 개발 규칙

### AGENTS.md

| 규칙 | W5에서의 적용 |
| --- | --- |
| 공식 SDK Route를 전부 공개하지 않음. allowlist만 등록하고 제외 Route의 404/405 Contract Test 유지 | W5-R5, W5-V6 |
| FastAPI Route에 업무 규칙을 직접 작성하지 않음 | 교체 후에도 유지 |
| 장기 Task의 원장은 영속 Task Store | W5-R9 |
| 프로세스 메모리 상태만으로 완료·복구를 판정하지 않음 | 비동기 경로 |
| 외부 Provider 장애 시 부분 결과와 `warnings` | W5-D1(metadata 보존) |
| 실패한 테스트 삭제·우회 금지 | [30-5-11](30-5-11-rollback.md) §3.2 |

## 6. 선후 단계 문서

| 문서 | W5와의 관계 |
| --- | --- |
| [30-4](30-4-w4-root-graph.md) | `build_workmate_graph()` 제공 |
| [30-4-5](30-4-5-design.md) §3 | **멱등성 설계** — W5에서 외부에 노출된다 |
| [30-4-9](30-4-9-exit-criteria.md) §6.1 | **`message_id` 문제를 W5로 이월** |
| [30-2-5](30-2-5-design.md) §4.5 | Checkpointer 수명 관리 |
| [30-1-12](30-1-12-handoff.md) | 스냅샷의 운영 경로 대조 |
| [30-6](30-6-w6-interrupt-resume.md) | 같은 진입점에 `INPUT_REQUIRED`를 추가 |
| [30-7](30-7-w7-legacy-removal.md) | W5가 만드는 "아무도 안 쓰는 상태"가 삭제의 전제 |
| [30-8](30-8-w8-retry-observability.md) | 예외 전파 재확인 |

## 7. 외부 문서

| 자료 | 확인할 내용 |
| --- | --- |
| LangGraph — `ainvoke` | `config={"configurable": {"thread_id": ...}}` 전달, **예외 전파 동작** |
| LangGraph — 예외 처리 | 노드 예외가 감싸지는지, Subgraph 경계에서의 동작 |
| FastAPI — lifespan | `@asynccontextmanager` 방식, `app.state` 사용 |
| Starlette — 미들웨어 순서 | `ServerErrorMiddleware`와 `CORSMiddleware`의 관계 |
| a2a-sdk 1.1.2 | `TaskUpdater`, `EventQueue`, Route 생성 |

**LangGraph의 예외 전파 동작을 문서가 아니라 실행으로 확인한다**(W5-V5-6). W5-K1의 핵심이다.

## 8. 이 문서 묶음

| 문서 | 대응 절 |
| --- | --- |
| [30-5-1](30-5-1-document-info.md) | §1 문서 정보·용어·교체 대상 |
| [30-5-2](30-5-2-scope.md) | §2 목적, 교체 지점 3곳, 범위 |
| [30-5-3](30-5-3-entry-criteria.md) | §3 선행 조건, **기준선 테스트** |
| [30-5-4](30-5-4-requirements.md) | §4 요구사항 W5-R1~R10 |
| [30-5-5](30-5-5-design.md) | §5 설계 — 교체 전후, 오류 경계, `message_id`, 결정 W5-D1~D5 |
| [30-5-6](30-5-6-wbs.md) | §6 작업 분해 W5-T0~T10 |
| [30-5-7](30-5-7-verification.md) | §7 검증 설계 W5-V1~V10 + 로컬 HTTP |
| [30-5-8](30-5-8-traceability.md) | §8 추적성, **과거 회귀 → 검증 매핑** |
| [30-5-9](30-5-9-exit-criteria.md) | §9 완료 정의, 승인 경계 |
| [30-5-10](30-5-10-risks.md) | §10 위험 등록부 W5-K1~K9 |
| [30-5-11](30-5-11-rollback.md) | §11 롤백·중단·재개, **롤백 착지점** |
| [30-5-12](30-5-12-references.md) | §12 참조 (이 문서) |
