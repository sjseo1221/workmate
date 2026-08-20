# M1.1-01 검수 결과

## 1. 기본 정보

- 마일스톤: M1.1 업무 DB 기반
- 제목: 업무 도메인 Migration 초안
- 담당자: Codex
- 검수자: 사용자 Schema 검수 대기
- 상태: 검수 중
- 실행일: 2026-08-13
- 실행 ID: `20260813-165857`
- 코드 버전: `workmate-agent` 작업 트리
- 입력 데이터 버전: 해당 없음 (DDL 계약 테스트)
- 작업 유형: DB·Migration

## 2. 최신 실행과 승인

- latest_run_id: `20260813-165857`
- latest_run_status: PASS (자동 테스트·compileall·diff 검사)
- latest_approved_run_id: null
- approved_at: null

## 3. 목표와 완료 기준

- 목표: M0.1 A2A 인프라와 분리된 Task·User·외부 동기화 상태 PostgreSQL 업무 도메인 Migration 초안 작성
- 완료 기준: 업무 테이블·사용자 범위·Soft Delete·원본 중복 방지·Gmail/Calendar Cursor 계약을 SQL로 선언하고 계약 테스트가 PASS
- 백로그 범위: M1.1-01
- 미완료·보류 백로그: PostgreSQL 실제 적용·재실행 검증 및 공개 DDL/제약 사용자 검수

## 4. 구현 요약

- `users`: 사용자 표시명·IANA timezone과 생성·수정 시각을 저장한다.
- `tasks`: 담당 사용자, 상태, 마감, 출처, Soft Delete를 저장하고 상태·출처 조합을 검사한다.
- `tasks_source_unique_idx`: 삭제 여부와 관계없이 사용자별 원본 Task 중복 생성을 차단한다.
- `source_sync_states`: Gmail `historyId`, Calendar `nextSyncToken`, Watch 식별자·만료·동기화 상태를 사용자·소스별로 저장한다.
- A2A 인프라 테이블은 새 Migration에서 생성하거나 수정하지 않았다.
- Secret·Token·API Key·샘플 데이터 INSERT는 Migration에 포함하지 않았다.

## 5. 구현·Schema·테스트 경로

- 구현 Migration: [`002_work_domain.sql`](../../../../../workmate-agent/migrations/002_work_domain.sql)
- 계약 테스트: [`test_work_domain_migration.py`](../../../../../workmate-agent/tests/test_work_domain_migration.py)
- 기존 Migration 회귀 테스트: [`test_migration.py`](../../../../../workmate-agent/tests/test_migration.py)
- 관련 결정: [`03-data-priority-rules.md`](../../../../03-data-priority-rules.md), [`07-technical-specification.md`](../../../../07-technical-specification.md)

## 6. 실행 명령과 결과

```text
cd workmate-agent
$env:WORKMATE_INTERNAL_CHAT_ENABLED='true'
.\.venv\Scripts\python.exe -m unittest tests/test_work_domain_migration.py tests/test_migration.py
.\.venv\Scripts\python.exe -m compileall -q app
git diff --check
```

- 계약·회귀 테스트: PASS (5 tests)
- `compileall`: PASS
- `git diff --check`: PASS
- PostgreSQL 실제 적용: 미실행 (M1.1-05 통합 검수 범위)

## 7. 검수 항목

| 항목 | 결과 | 근거 경로 |
| --- | --- | --- |
| 업무 도메인 테이블 선언 | PASS | `test_declares_only_m11_work_domain_tables` |
| Task 사용자 범위·Soft Delete·원본 중복 계약 | PASS | `test_task_contract_contains_scope_soft_delete_and_source_deduplication` |
| Gmail/Calendar Cursor·Watch 계약 | PASS | `test_sync_state_contract_contains_provider_cursors_and_watch_fields` |
| Secret·샘플 데이터 미포함 | PASS | `test_migration_does_not_embed_secret_or_sample_values` |
| 기존 M0.1 Migration 회귀 | PASS | `tests/test_migration.py` |
| PostgreSQL 실제 적용·재실행 | 미실행 | M1.1-05에서 수행 |
| 공개 DDL·제약 사용자 검수 | 사용자 확인 필요 | 공개 데이터 모델 변경 범위 |

## 8. 문제와 수정 이력

- 발견된 문제: 없음
- 보완 사항: 실제 PostgreSQL 적용과 DDL 제약 검수는 별도 통합 단계로 분리했다.
- 재검수 조건: 사용자가 Schema를 확인하고 M1.1-05 PostgreSQL 통합 검수를 실행할 수 있어야 한다.

## 9. 최종 판단

- 승인 여부: 미승인
- 검수 의견: 자동 검증은 모두 PASS했지만 공개 업무 데이터 모델 Migration은 사람의 Schema 검수가 필요한 항목이므로 자동 승인하지 않는다.
- 다음 조치: M1.1-01 DDL Schema 검수 후 M1.1-02 Task Repository 경계 구현 여부를 확인한다.
