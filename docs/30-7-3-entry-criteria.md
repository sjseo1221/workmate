# W7-3 — 선행 조건

> [30-7-w7-legacy-removal.md](30-7-w7-legacy-removal.md) §3의 상세 문서.

## 1. 선행 조건 목록

| ID | 조건 | 출처 | 확인 방법 | 미충족 시 |
| --- | --- | --- | --- | --- |
| W7-E1 | W5 완료 — 운영 경로가 Graph | [30-5-9](30-5-9-exit-criteria.md) | `grep -rn "workflow_registry" app/` | 착수 금지 |
| W7-E2 | **W6 완료 및 승인** — 확인·재개가 동작 | [30-6-9](30-6-9-exit-criteria.md) | 승인 기록 | **착수 금지** |
| W7-E3 | 스냅샷 27건 PASS(2건 갱신 후) | [30-6-7](30-6-7-verification.md) | 대조 실행 | 삭제 후 기준선 없음 |
| W7-E4 | `app/`에 `WorkflowRegistry` 호출자 없음 | W5-V1-3 | grep | 삭제 시 런타임 오류 |
| W7-E5 | `save_checkpoint` 호출자 없음 | W5-T3 | grep | 동상 |
| W7-E6 | 증빙 링크 대상 목록 확보 | W7-T1 | 조사 | 링크 정정 누락 |
| W7-E7 | **W6 검증 기간 경과** | — | 판단 | 롤백 기회 상실 |

## 2. 각 조건의 근거

### 2.1 W7-E2 — W6의 **승인**까지 필요하다

다른 선행 조건은 "완료"면 되지만, W7-E2는 **승인**을 요구한다.

W6은 자동 승인 대상이 아니다([30-6-9](30-6-9-exit-criteria.md) §3.1). UI 육안 검수와 공개 계약
변경이 사용자 판단을 필요로 한다.

**승인되지 않은 W6 위에 W7을 쌓으면**, 나중에 W6이 반려됐을 때 롤백 착지점(`app/workflows/`)이 이미
사라진 상태가 된다.

### 2.2 W7-E3 — 삭제 후 대조의 기준선

W7은 삭제가 동작을 바꾸지 않았음을 스냅샷으로 증명한다.

```
W6 완료: 27건 PASS (25건 유지 + 2건 갱신)
W7 완료: 27건 PASS   ← 삭제가 아무것도 바꾸지 않았다
```

W7에서 차이가 나면 **삭제한 코드가 여전히 쓰이고 있었다**는 뜻이다.

### 2.3 W7-E4·E5 — 호출자 부재

삭제 전에 아무도 안 쓰는지 확인한다. 이것이 W7-T1(잔여 참조 전수 조사)의 목적이다.

```bash
grep -rn "workflow_registry\|WorkflowRegistry" app/
grep -rn "from app.workflows\|import app.workflows" app/
grep -rn "save_checkpoint" app/
```

**테스트는 별개다.** 테스트가 `app.workflows`를 import하는 것은 정상이며, W7-T4에서 경로를 갱신한다.

### 2.4 W7-E6 — 증빙 링크 목록

삭제·이동 전에 어떤 문서가 무엇을 참조하는지 알아야 한다.

```bash
grep -rn "app/workflows" ../docs/ | grep -v "^../docs/30-"
grep -rln "external_sync\|weekly_classification" ../docs/evidence/
```

W0 조사에서 이미 일부 파악했다 — `docs/evidence/`에 `app/workflows/`를 참조하는 문서가 20개,
그중 `external_sync`를 참조하는 것이 2개.

### 2.5 W7-E7 — 검증 기간 (판단 항목)

기계적으로 확인할 수 없는 조건이다.

**W6 완료 직후 바로 W7로 가지 않는다.** W6은 UI·어댑터·계약이 함께 바뀐 단계이고, 문제가 있다면
실제로 써 봐야 드러난다.

| 확인할 것 | 방법 |
| --- | --- |
| 확인 흐름이 실제로 잘 동작하는가 | 로컬에서 여러 시나리오 실행 |
| 오케스트레이터 통합이 깨지지 않았는가 | 어댑터 경유 확인 |
| 예상치 못한 문제가 없는가 | 일정 기간 사용 |

이 기간이 지나야 "이제 롤백 착지점을 없애도 된다"고 판단할 수 있다.

## 3. 착수 전 확인 명령

```bash
cd workmate-agent

# W7-E1, E4
grep -rn "workflow_registry\|WorkflowRegistry" app/        # 출력 없음
grep -rn "from app.workflows\|import app.workflows" app/   # 출력 없음

# W7-E5
grep -rn "save_checkpoint" app/                            # 출력 없음

# W7-E6
grep -rn "app/workflows" ../docs/ | grep -v "docs/30-"
grep -rln "external_sync\|weekly_classification" ../docs/

# W7-E3
WORKMATE_TEST_DATABASE_URL="postgresql://postgres:postgres@127.0.0.1:55432/workmate_test" \
  uv run python -m unittest tests.contracts.test_contract_snapshots -v

# 전체
WORKMATE_TEST_DATABASE_URL="..." uv run python -m unittest discover -s tests -v
```

## 4. 환경 전제

| 항목 | 이유 |
| --- | --- |
| 테스트 PostgreSQL | **Migration 적용·재적용 검증** |
| 테스트 DB 초기화 가능 | Migration 멱등성 확인 시 필요 |

### 4.1 Migration 검증 환경

W7-V5·V6은 실제 DB에 Migration을 적용해 확인한다.

```
1. 깨끗한 DB에 001~006 적용 → a2a_checkpoints 존재
2. 007 적용 → 테이블 없음
3. 007 재적용 → 오류 없음 (멱등)
```

SQLite 경로도 같은 확인이 필요한지 판단한다 — `PersistentTaskStore`는 `CREATE TABLE IF NOT EXISTS`를
코드에서 실행하므로 Migration 파일과 별개다([30-7-5](30-7-5-design.md) §5).

## 5. 미충족 시 처리

| 조건 | 미충족 상황 | 처리 |
| --- | --- | --- |
| W7-E1 | Registry 호출 잔존 | W5로 복귀 |
| W7-E2 | W6 미승인 | **착수 금지.** 승인 대기 |
| W7-E3 | 스냅샷 차이 | W6에서 해소 |
| W7-E4, E5 | 호출자 발견 | 해당 호출을 Graph로 교체(W5 잔여 작업) |
| W7-E6 | 목록 미확보 | W7-T1에서 조사 |
| W7-E7 | 검증 기간 부족 | **판단 항목.** 서두르지 않는다 |

## 6. 이 단계의 선행 조건이 엄격한 이유

| 단계 | 롤백 가능성 |
| --- | --- |
| W1~W4 | 파일 삭제로 완전 복구 |
| W5·W6 | revert + `app/workflows/` 복원으로 복구 |
| **W7 이후** | **`app/workflows/` 복원이 추가 작업이 된다. Migration은 복구 불가** |

W7-E2(W6 **승인**)와 W7-E7(검증 기간)이 다른 단계에 없는 이유다.

## 7. 후행 단계의 선행 조건에 미치는 영향

| W7 결과 | W8 선행 조건 | 관계 |
| --- | --- | --- |
| `app/workflows/` 부재 | [W8-E1](30-8-w8-retry-observability.md) | "실행 경로가 하나" |
| 부작용 노드 목록 | W8-T2 | 재시도 제외 대상 |
| 스냅샷 27건 PASS | W8의 기준선 | |

## 8. 참조

- [30-6-9](30-6-9-exit-criteria.md) — W6 완료 정의와 승인
- [30-7-5](30-7-5-design.md) — 삭제 순서
- [30-7-11](30-7-11-rollback.md) — 비가역 작업의 취급
