# W6-13 — 참조 자료

> [30-6-w6-interrupt-resume.md](30-6-w6-interrupt-resume.md) §13의 상세 문서.

"무엇을 참조하는가"가 아니라 **"어디를 왜 읽는가"** 를 기록한다.

## 1. 설계 근거 문서

### 96-workmate-langgraph-target-architecture.md

**W6은 96번 문서 의존도가 가장 높다.** 요구사항 11개 중 7개가 여기서 나온다.

| 절 | 읽는 이유 | 대응 |
| --- | --- | --- |
| **§6 Assistant Router Subgraph** | **W6의 설계도.** 노드 구성과 확인 시퀀스 다이어그램 | W6-R1, §2 설계 |
| §6 마지막 문단 | "Resume 시 LLM Router를 다시 호출하지 않고 Checkpoint에 저장된 `skill_id`와 검증된 `arguments`를 사용한다" | W6-R5 |
| §6 시퀀스 다이어그램 | 사용자 → Graph → Checkpointer → Skill의 왕복 | W6-R3 |
| **§7 Task 상태와 Checkpoint** | 상태 전이도 — `WORKING → INPUT_REQUIRED → WORKING` | W6-R2, C1 |
| §7 | `CANCELED` 전이 경로 | W6-R7, C4 |
| §7 하단 flowchart | `task_id ↔ thread_id` 매핑, 멱등성 Store 위치 | C5 |
| **§11-7** | "사용자 확인이 필요한 동작은 `interrupt` 전에는 외부 상태를 변경하지 않는다" | **W6-R4** |
| §11-8 | "Resume은 새 Task를 만들지 않고 같은 `thread_id`와 멱등성 Key를 사용한다" | W6-R6, C5 |
| §8 오류·재시도 Graph | `AUTH_REQUIRED + interrupt` 경로 — W6 범위 밖이지만 상태 전이 참고 | — |

§6의 두 다이어그램(flowchart와 sequenceDiagram)을 **둘 다** 읽는다. 전자는 노드 구성, 후자는 시간
순서를 보여준다.

### 30-langgraph-migration-plan.md

| 절 | 읽는 이유 |
| --- | --- |
| §0.1 전제 | "호환보다 설계 정합성 우선" — D1=B의 근거 |
| **§4 D1** | 확정 결정(B안) |
| **§4.1** | W6에서 확정할 계약 항목 5개의 초안 |
| §5 W6 | 단계 정의 |
| §7.2 | 동결 구역에 `AssistantDrawer.tsx`·`m51_legacy_adapter.py` 포함 |

### 02-a2a-interface.md

**개정 대상이자 현재 계약의 원본이다.**

| 읽는 이유 |
| --- |
| 현재 확인·재요청 계약의 정의 |
| Task 상태 값 목록 — `INPUT_REQUIRED`가 이미 정의돼 있는지 |
| 멱등성 계약 |
| Artifact 구조 |

## 2. 코드 참조

### 2.1 현재 확인 흐름 — 바꾸는 대상

| 위치 | 읽는 이유 |
| --- | --- |
| [assistant_router.py:221-243](../workmate-agent/app/workflows/assistant_router.py#L221) | **`_requires_confirmation()`** — 판정 규칙 4종. Docstring에 2026-08-17 배경. **W6에서 변경 금지** |
| [assistant_router.py:771-793](../workmate-agent/app/workflows/assistant_router.py#L771) | `assistant_ask_workflow()` 진입, Docstring에 재요청 방식 설명 |
| [assistant_router.py:794-816](../workmate-agent/app/workflows/assistant_router.py#L794) | **`confirmed_skill_id` 재요청 경로** — `route()`를 건너뛰는 것이 W6-R5의 선례 |
| [assistant_router.py:866-876](../workmate-agent/app/workflows/assistant_router.py#L866) | **`pending_action` 반환** — 교체 대상 |
| [assistant_router.py:877-916](../workmate-agent/app/workflows/assistant_router.py#L877) | 확인 불필요 시 즉시 실행 경로 |

### 2.2 Task 상태 처리

| 위치 | 읽는 이유 |
| --- | --- |
| [internal_chat.py:276-301](../workmate-agent/app/internal_chat.py#L276) | **`_save_task_status()`** — `status.message`에 메시지를 담는 **선례**(C2), `record_message()`를 안 부르는 이유(C5) |
| [internal_chat.py:303-334](../workmate-agent/app/internal_chat.py#L303) | 백그라운드 실행의 상태 전이 |
| [runtime.py:245-262](../workmate-agent/app/a2a/runtime.py#L245) | `TaskUpdater`로 상태 전이 |
| [runtime.py:276-287](../workmate-agent/app/a2a/runtime.py#L276) | **`cancel()`** — 기존 취소 경로. W6-V6-5에서 관계 정리 |

### 2.3 멱등성 — C5 설계에 필요

| 위치 | 읽는 이유 |
| --- | --- |
| [persistence.py:234-245](../workmate-agent/app/a2a/persistence.py#L234) | **해시 불일치 시 `ValueError`** — W6-K8의 원인 |
| [persistence.py:210-232](../workmate-agent/app/a2a/persistence.py#L210) | `record_message()` 시그니처 |
| [30-4-5](30-4-5-design.md) §3 | W4의 멱등성 설계 |

### 2.4 UI

| 위치 | 읽는 이유 |
| --- | --- |
| [AssistantDrawer.tsx:40-42](../workmate-ui/app/views/AssistantDrawer.tsx#L40) | `POLL_INTERVAL_MS`(1.5초), `POLL_TIMEOUT_MS`(5분), **`TERMINAL_FAILURE_STATES`에 `CANCELED` 포함** |
| [AssistantDrawer.tsx:143-163](../workmate-ui/app/views/AssistantDrawer.tsx#L143) | **폴링 루프** — `INPUT_REQUIRED`가 어디에도 안 걸린다 |
| [AssistantDrawer.tsx:118-125](../workmate-ui/app/views/AssistantDrawer.tsx#L118) | 확인 시 `confirmedSkillId` 재요청 |
| [AssistantDrawer.tsx:166](../workmate-ui/app/views/AssistantDrawer.tsx#L166) | `pendingAction`을 메시지에 붙이는 지점 |
| [AssistantDrawer.tsx:14-16](../workmate-ui/app/views/AssistantDrawer.tsx#L14) | 주석: Drawer가 확인 버튼을 눌러야 재요청한다는 설명 |

### 2.5 어댑터

| 위치 | 읽는 이유 |
| --- | --- |
| [tools/m51_legacy_adapter.py](../workmate-agent/tools/m51_legacy_adapter.py) | 응답 변환 로직 — 흡수 가능성 판정 |
| [test_m51_legacy_adapter.py:1-10](../workmate-agent/tests/test_m51_legacy_adapter.py#L1) | Docstring에 어댑터의 역할과 2026-08-17 결정 배경 |
| [test_m51_legacy_adapter.py](../workmate-agent/tests/test_m51_legacy_adapter.py) | "확인 필요 안내" 변환을 검증하는 케이스 |

**어댑터 테스트의 Docstring이 중요하다.**

> 이 파일은 더 이상 `_infer_skill`류 키워드 매핑을 검증하지 않고, "항상 assistant_ask로 간다"는 것과
> **응답 변환(실행된 Skill 노출, 확인 필요 안내)** 만 검증한다.

"확인 필요 안내" 변환이 이미 있다는 뜻이다 — 흡수 가능성이 높다는 신호다.

## 3. 개발 규칙

### AGENTS.md

| 규칙 | W6에서의 적용 |
| --- | --- |
| **오케스트레이터 저장소는 명시적 허용 시에만 수정** | [30-6-10](30-6-10-approval.md) §3 |
| 동 — "로컬 실행 확인·디버깅처럼 되돌리기 쉬운 상황에도 예외 없이" | 조사(읽기)는 가능, 수정은 불가 |
| 사용자 승인 없이 데이터 모델·공개 A2A Schema 변경 금지 | 계약안 승인(W6-E3) |
| 공식 SDK Route를 전부 공개하지 않음 | C3가 b안이 될 때 승인 |
| UI 육안 검수는 자동 승인 대상이 아님 | W6-V7, E-2 |
| 변경이 필요하면 문서·Schema·Contract Test를 함께 수정 | W6-R9 |
| 실패한 테스트 삭제·우회 금지 | [30-6-12](30-6-12-rollback.md) §3.2 |
| 기대값 완화 금지 | 스냅샷 3건 이상 갱신 금지 |

### 13-manual-verification-guide.md

육안 검수 항목의 형식. W6 항목을 여기에 추가한다.

## 4. 선후 단계 문서

| 문서 | W6과의 관계 |
| --- | --- |
| [30-2-4](30-2-4-requirements.md) W2-R7 | Checkpointer — `interrupt`의 전제 |
| [30-3-5](30-3-5-design.md) §6 | **W3-D5: 확인 판정과 실행 사이 노드 분리** — W6의 교체 지점을 미리 만들어 둠 |
| [30-3-4](30-3-4-requirements.md) W3-R11 | 확인 흐름 동결 — W6까지 유지 |
| [30-3-7](30-3-7-verification.md) W3-V11-4 | 확인 대기 중 외부 상태 불변 — W6-V2의 선행 확인 |
| [30-4-4](30-4-4-requirements.md) W4-R8 | Checkpointer Graph 결합 |
| [30-5-4](30-5-4-requirements.md) W5-R6 | 오류 매핑 — `INPUT_REQUIRED`도 같은 경로 |
| [30-5-4](30-5-4-requirements.md) W5-R3 | 비동기 폴링 — UI 분기 추가 지점 |
| [30-1-12](30-1-12-handoff.md) §5 | **스냅샷 갱신 절차** — W6이 기록 모드를 쓰는 유일한 단계 |
| [30-7](30-7-w7-legacy-removal.md) | W6 롤백의 착지점이 사라지는 시점 |
| [30-9](30-9-w9-docs-evidence.md) | 계약 변경 내역의 소비처 |

## 5. 외부 문서

| 자료 | 확인할 내용 |
| --- | --- |
| **LangGraph — `interrupt`** | 호출 방식, 반환값, Checkpoint에 무엇이 저장되는가 |
| **LangGraph — `Command(resume=...)`** | 재개 방식, `config`의 `thread_id` 전달 |
| LangGraph — interrupt 이후 상태 조회 | `graph.get_state(config)`로 중단 정보를 꺼내는 방법 |
| LangGraph — Human-in-the-loop 패턴 | 공식 예제와 우리 구조의 차이 |
| **a2a-sdk 1.1.2 — `message:send`** | **임의 payload 통과 여부, 기존 Task 이어받기 지원**(C3 판정) |
| a2a-sdk — Task 상태 | `TASK_STATE_INPUT_REQUIRED`가 정의돼 있는지 |

### 5.1 C3 판정에 필요한 SDK 확인

W6-T1에서 가장 먼저 할 일이다.

```
1. a2a-sdk의 TaskState enum에 INPUT_REQUIRED가 있는가
2. message:send 핸들러가 임의 payload를 Workflow까지 전달하는가
3. 기존 task_id를 이어받는 방식이 있는가
4. 없다면 새 Route가 불가피한가
```

**문서가 아니라 실제 SDK 코드와 실행으로 확인한다.**

## 6. 이 문서 묶음

| 문서 | 대응 절 |
| --- | --- |
| [30-6-1](30-6-1-document-info.md) | §1 문서 정보·용어·확인 대상 4종 |
| [30-6-2](30-6-2-scope.md) | §2 목적, 현재/목표 동작, 범위 |
| [30-6-3](30-6-3-entry-criteria.md) | §3 선행 조건 (**승인이 선행 조건**) |
| [30-6-4](30-6-4-requirements.md) | §4 요구사항 W6-R1~R11 |
| [30-6-5](30-6-5-design.md) | §5 설계 — **계약안 C1~C5**, Subgraph, 불변식, UI |
| [30-6-6](30-6-6-wbs.md) | §6 작업 분해 W6-T1~T10 |
| [30-6-7](30-6-7-verification.md) | §7 검증 설계 W6-V1~V11 |
| [30-6-8](30-6-8-traceability.md) | §8 추적성, **계약 항목 추적**, 의도적 변경 누적 |
| [30-6-9](30-6-9-exit-criteria.md) | §9 완료 정의 (**자동 승인 불가**) |
| [30-6-10](30-6-10-approval.md) | §10 **승인 경계** |
| [30-6-11](30-6-11-risks.md) | §11 위험 등록부 W6-K1~K10 |
| [30-6-12](30-6-12-rollback.md) | §12 롤백·중단·재개 |
| [30-6-13](30-6-13-references.md) | §13 참조 (이 문서) |
