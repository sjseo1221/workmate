# M2.1-06 통합·부분 실패 검수 결과

## 1. 기본 정보

- 마일스톤: M2.1
- 제목: 실제 Repository·Provider 경계와 부분 실패 통합 검수
- 담당자: Codex
- 검수자: 자동 승인(검증 명령)
- 상태: 완료
- 실행일: 2026-08-13
- 실행 ID: 20260813-232643

## 2. 구현·검증 요약

- [`test_m2_1_integration.py`](../../../../../../workmate-agent/tests/test_m2_1_integration.py)를 추가해 SQLite Task Repository의 실제 저장·조회 결과를 주간 분류와 연결했다.
- 저장된 사용자 Task만 `weekly_report` 결과로 변환하고 다른 사용자 원본은 포함하지 않는지 검증했다.
- 승인된 `weekly_report` 결과 Envelope Schema를 실제 생성 데이터로 검증했다.
- Gmail Provider 실패 시 Calendar·Task 결과와 `warnings`를 유지하는 기존 M1.5 부분 실패 회귀를 함께 실행했다.

## 3. 검증 명령과 결과

```text
.\.venv\Scripts\python.exe -m unittest tests.test_m2_1_integration tests.test_weekly_classification tests.test_weekly_source_link tests.test_contract -v
.\.venv\Scripts\python.exe -m compileall -q app tests
git diff --check
```

| 검수 항목 | 결과 | 근거 |
| --- | --- | --- |
| 실제 SQLite Repository 연결·사용자 격리 | PASS | `test_repository_records_become_schema_valid_weekly_result` |
| weekly_report 결과 Schema | PASS | 동일 테스트의 `Draft202012Validator` |
| Provider 부분 실패·warnings 회귀 | PASS | `test_provider_partial_failure_contract_is_regression_covered` |
| 주간 단위·원본 연결 회귀 | PASS | 10 tests PASS |
| 공개 A2A Contract 회귀 | PASS | 10 tests PASS |
| Python compileall | PASS | `compileall -q app tests` |
| diff 형식 | PASS | `git diff --check` |

총 22개 테스트 PASS, FAIL 0, SKIP 0이며 외부 Secret·실제 Provider 호출·수동 UI 검수는 포함하지 않았다.

## 4. 자동 승인 및 다음 작업

- 자동 승인: 적용
- 자동 진행 판정: 정의된 검증 명령과 검수 항목이 모두 정확히 PASS
- 자동 진행 보류 사유: 없음
- 최신 승인 실행: `20260813-232643`
- 다음 착수 항목: M2.2-01 다음 주 계획 근거 추출 설계·구현
- 재개 조건: 해당 없음

## 5. 범위와 보류

- 이 검수는 로컬 SQLite Repository와 Provider 실패 Fixture를 사용했다. 운영 PostgreSQL·실제 Gmail/Calendar 호출은 이미 승인된 M1.2/M1.5 증빙 범위이며 여기서 Secret을 재사용하지 않았다.
- M2.1은 Task 분류·원본 연결·Artifact 입력 생성까지 완료했다. LLM 보고서 문장 생성과 다음 주 계획 판정은 M2.2/M2.3 범위다.

## 6. 최종 판단

- 승인 여부: 승인
- 승인 방식: 자동 승인(검증 명령)
- 검수 의견: 실제 Repository 경계, 사용자 격리, Schema 생성, Provider 부분 실패 회귀가 모두 PASS하여 M2.1 통합 기준을 충족했다.
