# M2.1-05 주간 집계·Artifact 입력 생성 검수 결과

## 1. 기본 정보

- 마일스톤: M2.1
- 제목: 주간 집계·Artifact 입력 생성
- 담당자: Codex
- 검수자: 자동 승인(검증 명령)
- 상태: 완료
- 실행일: 2026-08-13
- 실행 ID: 20260813-232437

## 2. 구현 요약

- [`weekly_classification.py`](../../../../../../workmate-agent/app/workflows/weekly_classification.py)에 `build_weekly_report_data`를 추가했다.
- 완료·진행·지연 Task를 `weekly_report`의 `WorkItem` 구조로 집계하고, 주간 `period`, 결정적 summary, `source_refs`를 생성한다.
- 미구현 원장에 해당하는 `unresolved_issues`와 `next_week_plans`는 임의의 내용을 만들지 않고 빈 배열로 명시한다.
- Task와 외부 승인 원본의 ID는 각 WorkItem과 최상위 `source_refs`에 중복 없이 보존한다.
- [`test_weekly_source_link.py`](../../../../../../workmate-agent/tests/test_weekly_source_link.py)에 기간·목록·source_refs 생성 검증을 추가했다.

## 3. 검증 명령과 결과

```text
.\.venv\Scripts\python.exe -m unittest tests.test_weekly_classification tests.test_weekly_source_link -v
.\.venv\Scripts\python.exe -m unittest tests.test_contract -v
.\.venv\Scripts\python.exe -m compileall -q app
git diff --check
```

| 검수 항목 | 결과 | 근거 |
| --- | --- | --- |
| 주간 집계 period·세 목록 | PASS | `test_builds_weekly_report_data_from_linked_items` |
| source_refs 보존·중복 제거 | PASS | 동일 테스트 및 source link 회귀 |
| 승인된 공개 weekly_report Schema 회귀 | PASS | `tests.test_contract` 10 tests PASS |
| 전체 주간 단위 검증 | PASS | 10 tests PASS |
| Python compileall | PASS | `compileall -q app` |
| diff 형식 | PASS | `git diff --check` |

총 20개 테스트 PASS, FAIL 0, SKIP 0이며 수동 검수·외부 Secret·실제 Provider 호출은 포함하지 않았다.

## 4. 자동 승인 및 다음 작업

- 자동 승인: 적용
- 자동 진행 판정: 정의된 검증 명령과 검수 항목이 모두 정확히 PASS
- 자동 진행 보류 사유: 없음
- 최신 승인 실행: `20260813-232437`
- 다음 착수 항목: M2.1-06 통합·부분 실패 검수
- 재개 조건: 해당 없음

## 5. 범위와 보류

- 다음 주 계획과 미해결 이슈는 근거 원장이 준비되지 않아 빈 배열로 유지했다. 근거 없는 계획을 확정 결과로 만들지 않는 현재 계약을 따른다.
- 실제 Repository·Provider 부분 실패와 회귀는 M2.1-06에서 통합 검증한다.

## 6. 최종 판단

- 승인 여부: 승인
- 승인 방식: 자동 승인(검증 명령)
- 검수 의견: 주간 목록·기간·source_refs가 승인된 `weekly_report` 구조에 맞게 결정적으로 생성되었고 모든 검증 명령이 PASS했다.
