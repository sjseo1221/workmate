# M2.1-01 주간 기간·사용자 범위 정규화 결과

## 1. 기본 정보

- 마일스톤: M2.1
- 제목: 주간 기간·사용자 범위 정규화
- 담당자: Codex
- 검수자: 자동 승인(검증 명령)
- 상태: 완료
- 실행일: 2026-08-13
- 실행 ID: 20260813-231130

## 2. 구현 요약

- [`app/domain/weekly.py`](../../../../../workmate-agent/app/domain/weekly.py)에 `WeeklyPeriod`, `WeeklyScope`, `normalize_week_scope`를 추가했다.
- ISO 날짜 또는 `date`를 사용자 timezone의 현지 자정 기준 반열린 7일 범위로 정규화한다.
- DST 전환 주에도 현지 달력 경계를 유지한다.
- `user_id`를 trim·검증해 이후 Repository 조회의 사용자 범위로 전달한다.
- `as_of`는 timezone-aware ISO 시각만 허용하고 조회 timezone으로 정규화한다.

## 3. 검증 명령과 결과

```text
python -m unittest tests.test_weekly_classification -v
python -m compileall -q app tests
git diff --check
```

| 검수 항목 | 결과 | 근거 |
| --- | --- | --- |
| ISO 날짜·7일 반열린 범위 | PASS | `test_iso_date_creates_local_half_open_seven_day_period` |
| DST 현지 달력 경계 | PASS | `test_dst_keeps_local_calendar_boundaries` |
| 빈 사용자·잘못된 날짜·timezone·naive as_of 거부 | PASS | `test_invalid_scope_values_are_rejected` |
| 단위 테스트 | PASS | 3개 PASS, 0개 FAIL, 0개 SKIP |
| Python 컴파일 | PASS | `compileall` |
| diff 형식 | PASS | `git diff --check` |

## 4. 자동 진행 판정

- 자동 승인: 예
- 자동 진행 판정: 모든 정의 검증 항목이 정확히 PASS
- 자동 진행 보류 사유: 없음
- 다음 작업: M2.1-02 Task 상태 분류
- 재개 조건: 해당 없음

## 5. 최종 판단

- 승인 여부: 승인
- 승인 방식: 자동 승인(검증 명령)
- 의도적으로 제외한 범위: Task 상태 분류·외부 원본 연결·주간 집계는 M2.1-02~06에서 수행한다.
