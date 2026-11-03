# W6-3 — 선행 조건

> [30-6-w6-interrupt-resume.md](30-6-w6-interrupt-resume.md) §3의 상세 문서.

## 1. 선행 조건 목록

| ID | 조건 | 출처 | 확인 방법 | 미충족 시 |
| --- | --- | --- | --- | --- |
| W6-E1 | W5 완료 — 운영 경로가 Graph | [30-5-9](30-5-9-exit-criteria.md) | `grep -rn "workflow_registry" app/` 빈 결과 | 착수 금지 |
| W6-E2 | **Checkpointer 동작** — `interrupt`의 성립 조건 | [W4-V7](30-4-7-verification.md) | 이력 조회 | **착수 불가** |
| W6-E3 | §5.1 계약 설계안 C1~C5 **사용자 승인** | [30-6-10](30-6-10-approval.md) | 승인 기록 | 구현 착수 금지 |
| W6-E4 | W5-V2(이벤트 순서)·V5(오류 매핑) PASS | [30-5-7](30-5-7-verification.md) | W5 증빙 | 착수 금지 |
| W6-E5 | W5-V7(운영 경로 스냅샷) 전건 PASS | 동상 | 대조 | 변경 전 기준선 없음 |
| W6-E6 | 어댑터 흡수 가능성 판정 | W6-T1 | 판정 기록 | 오케스트레이터 승인 필요 여부 결정 |

## 2. 각 조건의 근거

### 2.1 W6-E2 — Checkpointer는 절대 조건

`interrupt()`는 Checkpointer 없이 **아예 동작하지 않는다.** 멈춘 지점과 State를 어딘가 저장해야
재개할 수 있기 때문이다.

```
interrupt() 호출
  → 현재 State를 Checkpoint에 저장
  → 실행 중단
  ...
Command(resume=...) 호출
  → thread_id로 Checkpoint 조회
  → State 복원
  → 멈춘 노드부터 계속
```

W2에서 만들고(W2-R7) W4에서 Graph에 결합했다(W4-R8). 둘 중 하나라도 검증되지 않았으면 W6은 시작조차
할 수 없다.

### 2.2 W6-E3 — 계약 승인이 코드보다 먼저

D1=B는 "공개 계약까지 개편한다"는 방향 결정이다. **구체안은 아직 정해지지 않았다.**

| 결정된 것 | 미정인 것 |
| --- | --- |
| interrupt 기반으로 간다 | Task 상태를 어떻게 노출할지(C1) |
| | payload를 어디에 실을지(C2) |
| | resume을 어떤 Route로 표현할지(C3) |
| | 취소 시 상태(C4) |
| | 멱등성 Key 처리(C5) |

특히 **C3이 Route allowlist에 영향을 줄 수 있다.** allowlist 변경은 `AGENTS.md`상 승인 대상이므로,
구현 후에 묻는 것은 순서가 틀렸다.

### 2.3 W6-E4 — 기존 계약 유지 확인

W6은 새 계약을 추가하는 것이지 기존 계약을 버리는 것이 아니다. 이벤트 순서와 오류 매핑은 그대로
유지된 채 `INPUT_REQUIRED`가 추가된다.

W5에서 이것이 깨진 상태라면 W6에서 "원래 깨져 있었나 W6이 깨뜨렸나"를 구분할 수 없다.

### 2.4 W6-E5 — 변경 전 기준선

W6은 스냅샷 27건 중 **2건만 의도적으로 바꾼다.** 나머지 25건이 W5에서 이미 PASS여야 "2건만 바뀌었다"를
증명할 수 있다.

```
W5 완료 시점:  27건 PASS
W6 진행 중:    25건 PASS + 2건 FAIL(예상된 실패)
W6 완료 시점:  27건 PASS (2건은 새 기대값)
```

### 2.5 W6-E6 — 어댑터 판정

[tools/m51_legacy_adapter.py](../workmate-agent/tools/m51_legacy_adapter.py)는 우리 저장소다. 새
프로토콜을 옛 모양으로 번역할 수 있으면 오케스트레이터를 안 건드려도 된다.

**W6-T1에서 가장 먼저 판정한다.** 결과에 따라 승인 요청 여부가 갈린다.

| 판정 | 후속 |
| --- | --- |
| 흡수 가능 | 오케스트레이터 무수정. 승인 불필요 |
| 흡수 불가 | **승인 요청** 또는 축소안(D1의 C안) 검토 |

## 3. 착수 전 확인 명령

```bash
cd workmate-agent

# W6-E1
grep -rn "workflow_registry\|WorkflowRegistry" app/     # 출력 없음

# W6-E2
uv run python -c "
from app.graph.checkpointer import build_checkpointer
print(build_checkpointer())
"

# W6-E4, E5
WORKMATE_TEST_DATABASE_URL="postgresql://postgres:postgres@127.0.0.1:55432/workmate_test" \
  uv run python -m unittest discover -s tests -v

# 현재 확인 흐름 확인 (변경 대상)
grep -n "pending_action\|confirmed_skill_id" app/graph/skills/assistant_router.py
grep -n "INPUT_REQUIRED" app/ -r                        # 현재는 출력 없음
```

마지막 명령의 결과가 **출력 없음**이라는 사실이 W6의 출발점이다. `INPUT_REQUIRED`는 현재 agent에도
UI에도 존재하지 않는다.

## 4. 환경 전제

| 항목 | 이유 |
| --- | --- |
| 테스트 PostgreSQL | Checkpointer Postgres 경로 |
| **UI 로컬 실행 환경** | W6-V7 육안 검수 |
| 서버 로컬 실행 | 확인→재개 흐름 실제 확인 |

### 4.1 UI 환경이 필요한 이유

W6은 UI를 고치는 유일한 단계다([AssistantDrawer.tsx](../workmate-ui/app/views/AssistantDrawer.tsx)).
확인 UI가 실제로 뜨고 resume이 동작하는지는 **육안 검수**로만 확인할 수 있다.

이것이 W6-V7이며, `AGENTS.md`상 **자동 승인 대상이 아니다.**

## 5. 미충족 시 처리

| 조건 | 미충족 상황 | 처리 |
| --- | --- | --- |
| W6-E1 | Registry 호출 잔존 | W5로 복귀 |
| W6-E2 | Checkpointer 미동작 | W4 또는 W2로 복귀 |
| W6-E3 | 계약안 미승인 | **구현 착수 금지.** W6-T1에서 설계안 제시 후 대기 |
| W6-E4 | 기존 계약 깨짐 | W5로 복귀 |
| W6-E5 | 스냅샷 차이 | W5에서 해소 |
| W6-E6 | 흡수 불가 판정 | 승인 요청 또는 축소안 |

## 6. 선행 조건의 특수성

W6은 다른 단계와 달리 **사람의 승인이 선행 조건에 들어간다.**

| 단계 | 선행 조건의 성격 |
| --- | --- |
| W1~W5 | 전부 기술적 조건(테스트 PASS, 파일 존재) |
| **W6** | 기술적 조건 + **승인**(W6-E3) |
| W7 | 기술적 조건 |
| W9 | 기술적 조건 + 승인(문서 개정) |

W6-E3을 충족하지 못한 채 구현하면, 나중에 승인이 나지 않았을 때 되돌릴 범위가 크다(agent + UI +
어댑터 + 문서).

## 7. 후행 단계의 선행 조건에 미치는 영향

| W6 결과 | W7 선행 조건 | 관계 |
| --- | --- | --- |
| 확인·재개가 Graph에서 동작 | [W7-E2](30-7-w7-legacy-removal.md) | 삭제 전 마지막 기능 |
| 스냅샷 27건 PASS(2건 갱신) | W7-E3 | 삭제 후 대조의 기준선 |
| W6-V7 육안 검수 PASS | [W9-E3](30-9-w9-docs-evidence.md) | 최종 완료 조건 |

## 8. 참조

- [30-5-9](30-5-9-exit-criteria.md) — W5 완료 정의와 전달 사항
- [30-6-5](30-6-5-design.md) §5.1 — 계약안 C1~C5
- [30-6-10](30-6-10-approval.md) — 승인 경계
