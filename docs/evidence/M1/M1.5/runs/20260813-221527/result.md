# M1.5-02 검수 결과

## 1. 기본 정보

- 마일스톤: M1.5 우선순위·브리핑
- 제목: PrioritySnapshot 저장 경계
- 담당자: Codex
- 검수자: 자동 승인(검증 명령)
- 상태: 완료
- 실행일: 2026-08-13
- 실행 ID: 20260813-221527
- 코드 버전: workmate-agent 작업 트리
- 입력 데이터 버전: 테스트 고정 Snapshot Fixture

## 2. 최신 실행과 승인

- latest_run_id: 20260813-221527
- latest_run_status: PASS
- latest_approved_run_id: 20260813-221527
- approved_at: 2026-08-13 22:15 Asia/Seoul

## 3. 목표와 완료 기준

- 목표: PrioritySnapshot의 내부 Domain·SQLite 계약·PostgreSQL Migration/Adapter 경계를 구현한다.
- 완료 기준: 사용자 격리, 점수 구성·순위·변경 사유 저장, 동일 사용자·`as_of`·Task 멱등 저장·재조회가 PASS한다.
- 백로그 범위: M1.5-02
- 미완료·보류 백로그: 실제 PostgreSQL 연결은 M1.5-05 통합 검수 범위

## 4. 구현 경로

- 구현 코드: [`app/domain/priority_snapshot.py`](../../../../../../workmate-agent/app/domain/priority_snapshot.py), [`app/repositories/priority.py`](../../../../../../workmate-agent/app/repositories/priority.py)
- Schema 또는 Migration: [`migrations/003_priority_snapshots.sql`](../../../../../../workmate-agent/migrations/003_priority_snapshots.sql)
- UI 코드: 해당 없음

## 5. 테스트 파일 경로

- 단위 테스트: [`tests/test_priority_repository.py`](../../../../../../workmate-agent/tests/test_priority_repository.py)
- 통합 테스트: 해당 없음 — 실제 PostgreSQL 연결은 M1.5-05에서 실행
- UI 테스트: 해당 없음
- Fixture/입력: 고정 `PrioritySnapshotRecord` Fixture
- 기대 결과: 사용자별 조회 격리와 동일 계산 시점의 멱등 갱신
- 모델 평가 Case: 해당 없음
- 모델 평가 결과: 해당 없음

## 6. 구현 요약

- `PrioritySnapshotRecord`가 점수와 `ScoreBreakdown.total` 일치, 양의 순위, timezone-aware 시각을 검증한다.
- SQLite Adapter는 사용자·`as_of`·Task 조합을 unique scope로 저장하고 재실행 시 기존 행을 갱신한다.
- PostgreSQL Adapter와 `003_priority_snapshots.sql`에 JSONB 점수 구성·근거, 사용자·Task 참조, 동일 계산 시점 unique 제약을 정의했다.
- 실제 PostgreSQL 연결은 미실행 상태이며 운영 DB 검증 완료로 간주하지 않는다.

## 7. 실행 명령과 결과

```text
cd C:\dev\workmate\workmate-agent
.\.venv\Scripts\python.exe -m unittest tests.test_priority_repository tests.test_priority_domain tests.test_task_repository -q
.\.venv\Scripts\python.exe -m compileall -q app tests
git diff --check
```

- 단위·회귀 테스트: PASS (15개)
- 구문 검사: PASS
- 문서 diff 검사: PASS
- 미실행·수동 검수·차단: 실제 PostgreSQL 연결은 M1.5-05로 명시적 이관

## 8. 검수 항목

| 항목 | 결과 | 근거 경로 |
| --- | --- | --- |
| Snapshot 값 불변식 | PASS | `test_invalid_score_breakdown_is_rejected` |
| 사용자 범위 격리 | PASS | `test_save_and_read_are_user_scoped` |
| 동일 계산 시점 멱등 갱신 | PASS | `test_same_user_as_of_task_is_idempotent` |
| 저장 범위 불일치 차단 | PASS | `test_scope_mismatch_is_rejected` |
| 기존 우선순위·Task 회귀 | PASS | 15개 통합 단위 테스트 |

## 9. 자동 진행 판정

- 자동 진행 판정: 자동 착수
- 자동 재작업 착수: 아니오
- 자동 진행 보류 사유: 없음 — 실제 PostgreSQL 연결은 이 백로그 완료 조건에서 제외하고 M1.5-05로 명시 이관
- 판정을 막은 검증 항목과 결과: 없음
- 미실행·수동 검수·차단 항목: 없음
- 필요한 조치 또는 사용자 승인: 없음
- 재개 조건: 해당 없음
- 다음 백로그: M1.5-03 `rank_priorities` Workflow/API

## 10. 최종 판단

- 승인 여부: 승인 — 자동 승인(검증 명령)
- 검수 의견: 정의된 M1.5-02 계약 검증이 모두 정확히 PASS하여 완료한다. 실제 PostgreSQL 연결은 M1.5-05 통합 검수에서 별도로 확인한다.
- 다음 조치: M1.5-03 `rank_priorities` Workflow/API 구현
