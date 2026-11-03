# W7-9 — 완료 정의

> [30-7-w7-legacy-removal.md](30-7-w7-legacy-removal.md) §9의 상세 문서.

## 1. 완료 조건 (Exit criteria)

| # | 조건 | 판정 근거 |
| --- | --- | --- |
| E-1 | W7-V1~V10 전부 PASS | 각 검증 |
| E-2 | `app/workflows/`가 저장소에 없고, 이동한 두 모듈이 새 위치에서 동작한다 | W7-V1~V3 |
| E-3 | `a2a_checkpoints`가 DROP되고 Migration이 멱등하다 | W7-V5, V6 |
| E-4 | **승인 증빙의 링크가 전부 유효하며 본문은 변경되지 않았다** | W7-V7, V8 |
| E-5 | 부작용 노드 목록이 W8 전달용으로 확정됐다 | 증빙 |

### 1.1 E-4가 W7 고유 조건인 이유

W7은 **승인된 과거 기록을 건드리는 유일한 단계**다. `AGENTS.md`가 두 가지를 동시에 요구하는 상황
([30-7-5](30-7-5-design.md) §4.1)이므로, 둘 다 지켰음을 명시적으로 확인한다.

| 확인 | 검증 |
| --- | --- |
| 링크가 실재 파일을 가리킨다 | W7-V7 |
| 서술·판정·승인 정보가 불변이다 | W7-V8 |

### 1.2 E-5 — W8로 넘기는 것

W3에서 작성한 부작용 노드 목록([30-3-5](30-3-5-design.md) §3.4)을 W7에서 최종 확정한다. W8이
`RetryPolicy` 적용 대상을 고를 때 **제외 목록**으로 쓴다.

부작용 노드에 재시도를 붙이면 Task가 중복 생성되거나 승인이 중복 처리된다.

## 2. 산출물 체크리스트

### 2.1 코드

```
[ ] app/workflows/                          삭제 (8개 파일)
[ ] app/domain/weekly_classification.py     이동
[ ] app/sync/__init__.py                    신설
[ ] app/sync/external_sync.py               이동
[ ] app/a2a/persistence.py                  save_checkpoint 제거, CREATE TABLE 제거
[ ] app/graph/skills/weekly_report.py       import 갱신
```

### 2.2 Migration

```
[ ] migrations/007_drop_a2a_checkpoints.sql
[ ] tests/test_migration.py                 007 DROP 검증 추가, 001에 이력 주석
```

### 2.3 테스트

```
[ ] tests/ import 경로 갱신 (W7-T1 조사 결과의 목록)
[ ] tests/test_persistence.py               Checkpoint 테스트 제거
[ ] tests/ui_working_fixture.py             Fake의 save_checkpoint 제거
```

### 2.4 문서

```
[ ] docs/06-delivery-plan.md                링크 2줄
[ ] docs/evidence/ 2건                      링크
```

### 2.5 증빙

```
[ ] docs/evidence/langgraph/W7/runs/{run_id}/result.md
[ ] docs/evidence/langgraph/README.md       W7 행
[ ] HANDOFF.md
[ ] 증빙 링크 정정 내역 (무엇을 바꾸고 무엇을 안 바꿨는지)
[ ] 부작용 노드 목록 (W8 전달)
[ ] 발견한 다른 죽은 코드 (기록만, 후속 백로그)
```

## 3. 승인 절차

### 3.1 자동 승인 대상 여부

| 조건 | W7 해당 여부 |
| --- | --- |
| 외부 OAuth·실제 Provider 호출 | 없음 |
| 공개 Schema·데이터 모델 변경 | **판단 필요** — §3.2 |
| UI 육안 검수 | 없음 |
| 모델 평가 | 없음 |
| 원격 Push | 없음 |

### 3.2 `a2a_checkpoints` DROP은 데이터 모델 변경인가

`AGENTS.md`: "사용자 승인 없이 데이터 모델과 공개 A2A Schema를 변경하지 않는다."

| 관점 | 판단 |
| --- | --- |
| 데이터 모델 변경인가 | **그렇다** — 테이블 제거 |
| 승인받았는가 | **그렇다** — D6=B(2026-09-23 사용자 결정) |
| 추가 승인이 필요한가 | **아니다** — 결정 시점에 "이전 데이터 다 지워져도 상관없음"을 확인했다 |

→ **D6=B로 이미 승인된 범위이므로 자동 승인 가능하다.**

단, 비가역 작업이므로 증빙에 명시하고 실행 전 [W7-T7](30-7-6-wbs.md)의 관문을 반드시 통과한다.

### 3.3 자동 승인 시 기록

```
latest_run_id:          {run_id}
latest_run_status:      PASS
latest_approved_run_id: {run_id}
approved_at:            {날짜} Asia/Seoul
reviewer:               자동 승인(검증 명령)
자동 재작업 착수:        예/아니오
자동 진행 판정:          진행 — W8 자동 착수
비가역 작업:            a2a_checkpoints DROP 적용 완료 (D6=B 승인 범위)
삭제:                   app/workflows/ 8개 파일 약 2,800줄
이동:                   2개 모듈
증빙 링크 정정:          N건 (본문 불변 확인)
```

### 3.4 자동 승인이 불가한 경우

| 상황 | 처리 |
| --- | --- |
| **W7-V9(스냅샷) FAIL** | **Migration 적용 금지.** 삭제가 동작을 바꿨다 |
| W7-V8(증빙 본문 불변) FAIL | `AGENTS.md` 위반. 즉시 되돌린다 |
| W7-V7(링크) FAIL | 정정 누락. 보완 |
| 삭제 중 예상 밖 의존 발견 | 조사 후 보고 |
| Migration이 다른 테이블에 영향 | 보고 |

## 4. 완료 후 상태

| 항목 | W7 완료 시점 |
| --- | --- |
| 운영 경로 | Root Graph (유일) |
| **`app/workflows/`** | **없음** |
| **`a2a_checkpoints`** | **없음** |
| Checkpoint | LangGraph Checkpointer만 |
| 확인 흐름 | `interrupt`/resume |
| 코드량 | 약 2,800줄 감소 |
| **W5·W6 롤백** | **복원 작업이 추가로 필요** |

### 4.1 이 시점의 의미

[계획서 §9](30-langgraph-migration-plan.md)의 완료 기준 9개 중 다섯이 충족된다.

| # | 기준 | 상태 |
| --- | --- | --- |
| 1 | `app/workflows/`·`WorkflowRegistry` 부재 | **W7에서 달성** |
| 2 | Skill 11개가 Graph 경로, Mock 없음 | W3·W5에서 달성 |
| 3 | 전체 테스트 PASS | 유지 |
| 4 | interrupt·resume·취소 | W6에서 달성 |
| 5 | `a2a_checkpoints` DROP, Checkpointer 실증 | **W7에서 달성** |
| 6 | 재시도 정책 | W8 |
| 7 | 스냅샷 차이 없음 | 유지 |
| 8 | 문서 갱신 | W9 |
| 9 | 증빙 기록 | 진행 중 |

남은 것은 W8(재시도)과 W9(문서·판정)뿐이다.

## 5. 완료 판정 체크리스트

```
[ ] 1.  W7-T1 조사 결과 (운영·테스트·문서 참조 목록)
[ ] 2.  W7-V1  레거시 부재 (5종 grep)
[ ] 3.  W7-V2  패키지 삭제
[ ] 4.  W7-V3  이동 모듈 + 내용 무수정 확인
[ ] 5.  W7-V4  compileall + 앱 기동
[ ] 6.  W7-V9  스냅샷 27건 PASS
[ ] 7.  W7-V10 전체 회귀
[ ] ★  여기까지 통과해야 Migration 적용 (W7-T7 관문)
[ ] 8.  W7-V5  테이블 DROP (Postgres + SQLite 경로)
[ ] 9.  W7-V6  Migration 멱등성
[ ] 10. W7-V10 전체 회귀 재실행
[ ] 11. W7-V7  증빙 링크 유효성
[ ] 12. W7-V8  증빙 본문 불변 (git diff 검토)
[ ] 13. git diff --stat 으로 범위 확인 (W7-R8)
[ ] 14. 부작용 노드 목록 확정
[ ] 15. result.md, evidence README, HANDOFF
[ ] 16. 자동 승인 판정 후 W8 착수
```

**7번이 비가역 작업 전의 관문이다.** 체크리스트에서 눈에 띄게 표시한다.

## 6. 다음 단계 전달 사항

| 전달 항목 | 받는 단계 | 용도 |
| --- | --- | --- |
| "실행 경로가 하나" 상태 | [W8](30-8-w8-retry-observability.md) | 재시도를 붙일 대상이 명확 |
| **부작용 노드 목록** | W8-T2 | **재시도 제외 대상** |
| 실패 파급 규칙표 | W8 | 정책 기준 |
| 스냅샷 27건 PASS | W8 | 기준선 |
| 증빙 링크 정정 내역 | [W9](30-9-w9-docs-evidence.md) | 문서 정합성 확인 |
| 발견한 다른 죽은 코드 | W9 | 후속 백로그 |
| 코드량 변화 | W9 | 전환 결과 보고 |

## 7. 참조

- [30-7-7](30-7-7-verification.md) — 검증 항목
- [30-7-11](30-7-11-rollback.md) — 완료하지 못했을 때
- [`AGENTS.md`](../AGENTS.md) — 완료 규칙, 증빙 규칙
