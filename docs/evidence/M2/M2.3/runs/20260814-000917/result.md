# M2.3-01 재검수 결과

## 1. 기본 정보

- 마일스톤: M2.3 보고서 생성
- 하위 백로그: M2.3-01 주간 보고 입력 조립·LLM 생성 Workflow
- 담당자: Codex
- 검수자: 미정
- 상태: 재작업
- 실행일: 2026-08-14
- 실행 ID: `20260814-000917`
- 입력 데이터: 임시 PostgreSQL `postgres:16-alpine` + 승인된 `001~003` Migration

## 2. 최신 실행과 승인

- latest_run_id: `20260814-000917`
- latest_run_status: 재작업 (전체 회귀 FAIL/ERROR)
- latest_approved_run_id: null
- approved_at: null

## 3. 실행 결과

### M2.3 대상 테스트

```text
.\.venv\Scripts\python.exe -m unittest tests.test_weekly_report_generation tests.test_weekly_plan_grounding tests.test_weekly_source_link tests.test_weekly_classification -v
```

- 결과: 16개 PASS, 0 FAIL, 0 ERROR, 0 SKIP

### PostgreSQL 통합 테스트

```text
$env:DATABASE_URL='postgresql://workmate:workmate_test@127.0.0.1:55432/workmate'
.\.venv\Scripts\python.exe -m unittest tests.test_m1_1_integration tests.test_m1_5_integration tests.test_postgres_integration tests.test_postgres_sync_state_integration -v
```

- 결과: 5개 PASS, 0 FAIL, 0 ERROR
- 검증: 임시 PostgreSQL 컨테이너 기동, 승인된 `001~003` Migration 적용, 컨테이너 제거 완료

### `DATABASE_URL`을 사용한 전체 회귀

```text
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

- 결과: 2개 FAIL, 10개 ERROR
- 원인: 기존 SQLite/Contract Fixture가 `alice`, `contract-user` 같은 비 UUID 사용자 ID를 사용하지만 PostgreSQL 업무 Schema의 `users.user_id`가 UUID 타입임
- 영향: `daily_briefing`, `weekly_report`, priority 및 Contract 경로가 전체 회귀에서 실패

### 정적 검사

```text
.\.venv\Scripts\python.exe -m compileall -q app tests
git diff --check
```

- 결과: PASS

## 4. 검수 판단

| 항목 | 결과 | 근거 |
| --- | --- | --- |
| M2.3 Workflow 대상 테스트 | PASS | 16개 PASS |
| PostgreSQL 저장소 통합 경계 | PASS | 5개 PASS |
| 전체 회귀 | FAIL | 2 FAIL·10 ERROR |
| 자동 승인 | 중단 | 전체 회귀가 PASS가 아님 |

## 5. 문제와 재개 조건

- 발견된 문제: PostgreSQL DSN을 설정한 전체 회귀에서 SQLite/Contract용 비 UUID 사용자 ID가 PostgreSQL UUID 컬럼에 전달됨.
- 원인: 테스트 Fixture와 운영 PostgreSQL 사용자 식별자 계약이 동일 실행에서 혼용됨.
- 수정 내용: 없음. 기존 공개 Schema·데이터 모델을 임의 변경하지 않고 중단함.
- 재개 조건: SQLite/Contract Fixture와 PostgreSQL 통합 Fixture의 사용자 ID 계약을 분리한 후 전체 회귀를 다시 실행한다.
- 현재 상태: `재작업`; 다음 백로그는 착수하지 않는다.
