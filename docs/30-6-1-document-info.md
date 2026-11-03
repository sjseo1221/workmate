# W6-1 — 문서 정보와 문서 체계

> [30-6-w6-interrupt-resume.md](30-6-w6-interrupt-resume.md) §1의 상세 문서.

## 1. 단계 식별

| 항목 | 값 |
| --- | --- |
| 단계 코드 | W6 |
| 단계명 | 사용자 확인을 interrupt로, 공개 계약 개편 |
| 상위 계획 | [30-langgraph-migration-plan.md](30-langgraph-migration-plan.md) §4.1, §5 |
| 선행 단계 | [W5 진입점 교체](30-5-w5-entrypoint-swap.md) |
| 후행 단계 | [W7 레거시 삭제](30-7-w7-legacy-removal.md) |
| 상태 | 대기 |
| 관련 확정 결정 | **D1=B**(공개 계약까지 개편), D5=A(폴링 유지) |
| 승인 필요 | §5.1 계약 설계안 C1~C5는 구현 착수 전 승인 대상 |

## 2. 단계 성격 — 유일하게 계약을 바꾸는 단계

전환 10단계 중 **공개 계약을 의도적으로 바꾸는 단계는 W6뿐**이다.

| 단계 | 공개 계약 |
| --- | --- |
| W0~W3 | 불변 |
| W4 | 불변(동작 3건 변경, Schema는 불변) |
| W5 | 불변(멱등성이 외부에 노출) |
| **W6** | **변경** ← D1=B |
| W7~W9 | 불변 |

### 2.1 무엇이 바뀌는가

```
[현재]
1. 사용자: "그 Task 지워줘"
2. 서버: pending_action{skill_id, arguments}를 응답에 싣고 종료
   ※ 서버에 아무 상태도 남지 않는다
3. UI: 확인 버튼 표시
4. 사용자 확인 → UI가 confirmed_skill_id·confirmed_arguments로 새 요청
5. 서버: LLM 라우팅을 건너뛰고 즉시 실행

[W6 이후]
1. 사용자: "그 Task 지워줘"
2. Graph: interrupt() → Checkpoint에 State 동결, Task는 INPUT_REQUIRED
3. UI: 폴링 중 INPUT_REQUIRED를 보고 확인 UI 표시
4. 사용자 확인 → 같은 thread_id로 resume
5. Graph: Checkpoint의 검증된 skill_id·arguments로 멈춘 자리에서 이어 실행
```

### 2.2 이것이 LangGraph 전환의 하이라이트인 이유

앞선 단계들은 "손으로 만든 것을 프레임워크 기능으로 갈아 끼우는" 성격이었다. W6은 다르다.

| | 현재 방식 | interrupt 방식 |
| --- | --- | --- |
| 대기 중 서버 상태 | **없음** | Checkpoint에 State 동결 |
| 재개 방식 | 프론트가 새 요청 | 같은 `thread_id`로 이어하기 |
| 중간 State | 유실 | 보존 |
| Task 추적 | 대기 상태가 보이지 않음 | `INPUT_REQUIRED`로 추적 |
| 취소 | 정의 없음 | `CANCELED` 전이 |

**서버가 대기 상태를 들고 있게 되는 것**이 본질적 차이다. 이것은 재요청 방식으로는 흉내 낼 수 없다.

### 2.3 W6의 범위가 넓은 이유

계약이 바뀌므로 그 계약을 쓰는 모든 곳이 영향받는다.

| 영향 | 파일 | 소유 |
| --- | --- | --- |
| Agent 구현 | `app/graph/skills/assistant_router.py` 등 | 우리 |
| 공개 문서 | [02-a2a-interface.md](02-a2a-interface.md) | 우리 |
| UI | [AssistantDrawer.tsx](../workmate-ui/app/views/AssistantDrawer.tsx) | 우리 |
| 오케스트레이터 어댑터 | [tools/m51_legacy_adapter.py](../workmate-agent/tools/m51_legacy_adapter.py) | 우리 |
| **오케스트레이터 본체** | `AI-agent_game_platform` | **타 팀 — 승인 필요** |

## 3. 문서 체계

| 문서 | 대응 절 | 내용 |
| --- | --- | --- |
| [30-6-1](30-6-1-document-info.md) | §1 | 문서 정보·체계·용어 (이 문서) |
| [30-6-2](30-6-2-scope.md) | §2 | 목적, 현재/목표 동작, 범위 |
| [30-6-3](30-6-3-entry-criteria.md) | §3 | 선행 조건 |
| [30-6-4](30-6-4-requirements.md) | §4 | 요구사항 W6-R1~R11 |
| [30-6-5](30-6-5-design.md) | §5 | 설계 — **계약안 C1~C5**, Subgraph, 불변식, UI |
| [30-6-6](30-6-6-wbs.md) | §6 | 작업 분해 W6-T1~T10 |
| [30-6-7](30-6-7-verification.md) | §7 | 검증 설계 W6-V1~V10 |
| [30-6-8](30-6-8-traceability.md) | §8 | 추적성 매트릭스 |
| [30-6-9](30-6-9-exit-criteria.md) | §9 | 완료 정의 |
| [30-6-10](30-6-10-approval.md) | §10 | **승인 경계** |
| [30-6-11](30-6-11-risks.md) | §11 | 위험 등록부 |
| [30-6-12](30-6-12-rollback.md) | §12 | 롤백·중단 기준 |
| [30-6-13](30-6-13-references.md) | §13 | 참조 자료 |

## 4. 식별자 규칙

| 접두 | 의미 | 예 |
| --- | --- | --- |
| `W6-E` | 선행 조건 | `W6-E2` |
| `W6-R` | 요구사항 | `W6-R4` |
| `W6-T` | 작업 | `W6-T6` |
| `W6-V` | 검증 | `W6-V7` |
| `W6-K` | 위험 | `W6-K1` |
| `W6-D` | 설계 결정 | `W6-D1` |
| **`C`** | **공개 계약 항목** | `C1`~`C5` |

`C` 접두는 W6 고유다. 승인 대상 계약 항목을 다른 식별자와 구분한다.

## 5. 용어

| 용어 | 정의 | 주의 |
| --- | --- | --- |
| **`interrupt()`** | Graph 실행을 그 지점에서 멈추고 Checkpoint에 동결 | Checkpointer 없이는 동작하지 않는다 |
| **`Command(resume=...)`** | 멈춘 지점부터 이어 실행 | 새 실행이 아니라 **재개**다 |
| **`INPUT_REQUIRED`** | 사용자 입력을 기다리는 Task 상태 | **현재 agent·UI 어디에도 없는 문자열** |
| **`pending_action`** | 현재 방식의 확인 요청 payload | `{skill_id, arguments}` |
| **`confirmed_skill_id`** | 현재 방식의 확인 응답 | 프론트가 재요청 시 전달 |
| **확인 대상 동작** | 실행 전 사용자 확인이 필요한 조합 | [`_requires_confirmation()`](../workmate-agent/app/workflows/assistant_router.py#L221) 4종 |
| **Human-in-the-loop** | 사람의 판단을 실행 흐름에 넣는 패턴 | W6이 구현하는 것 |

## 6. 확인 대상 동작 4종

[`_requires_confirmation()`](../workmate-agent/app/workflows/assistant_router.py#L221)이 정의한다.
**W6에서 이 판정 규칙 자체는 바꾸지 않는다.**

| Skill | 조건 | 성격 |
| --- | --- | --- |
| `analyze_meeting` | 항상 | 비용이 큼(STT+LLM) |
| `review_action_items` | `decisions`에 `reject` 포함 | 파괴적 |
| `review_proposal` | `decision == "ignore"` | 파괴적 |
| `manage_tasks` | `action == "delete"` | 파괴적 |

Docstring이 배경을 설명한다.

> 파괴적 동작(거절·무시·삭제)뿐 아니라, `analyze_meeting`처럼 **되돌릴 수는 없어도 파괴적이진 않은**
> costly한 동작도 포함한다(2026-08-17, 사용자 요청) — STT+LLM 비용이 들고, 여러 회의 중 엉뚱한 걸
> 골라 실행하면 그 비용이 헛되이 든다.

## 7. 산출물 위치

```
workmate-agent/
  app/graph/skills/assistant_router.py   interrupt 도입
  app/a2a/runtime.py                     INPUT_REQUIRED 표면화, resume 경로
  app/internal_chat.py                   동상
  tools/m51_legacy_adapter.py            어댑터 대응
workmate-ui/
  app/views/AssistantDrawer.tsx          폴링 분기, 확인 UI, resume 호출
docs/
  02-a2a-interface.md                    계약 개정
  evidence/langgraph/W6/runs/{run_id}/result.md
```

## 8. 변경 이력

| 일자 | 변경 | 사유 |
| --- | --- | --- |
| 2026-09-23 | 초판 (상위 문서 §1) | 단계별 상세 계획 |
| 2026-09-29 | 13개 문서로 분해 | 절별 상세화 요청 |
