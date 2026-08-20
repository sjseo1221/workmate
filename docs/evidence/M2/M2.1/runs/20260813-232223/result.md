# M2.1-04 회의 Action Item 연결 경계 검수 결과

## 1. 기본 정보

- 마일스톤: M2.1
- 제목: 회의 Action Item 연결 경계
- 담당자: Codex
- 검수자: 자동 승인(검증 명령)
- 상태: 완료
- 실행일: 2026-08-13
- 실행 ID: 20260813-232223

## 2. 구현 요약

- [`weekly_classification.py`](../../../../../../workmate-agent/app/workflows/weekly_classification.py)에 `link_action_item_tasks`를 추가했다.
- 호출자가 조회한 `known_action_item_ids`에 존재하는 Action Item만 주간 Task로 연결하며, 미존재 `source_id`는 차단한다.
- 요청 `user_id`와 일치하지 않는 Task와 Soft Delete·`cancelled` Task는 제외한다.
- 연결 결과에는 Task ID와 Action Item 원본 ID를 `source_refs`로 보존하고 결정적인 순서로 정렬한다.
- 실제 회의 원본 저장소가 준비되기 전에는 외부 API나 Mock 회의 결과를 직접 호출하지 않고, 원본 ID 집합을 명시적으로 주입하는 경계만 제공한다.

## 3. 검증 명령과 결과

```text
.\.venv\Scripts\python.exe -m unittest tests.test_weekly_classification tests.test_weekly_source_link -v
.\.venv\Scripts\python.exe -m compileall -q app
git diff --check
```

| 검수 항목 | 결과 | 근거 |
| --- | --- | --- |
| Action Item 원본 존재 검증 | PASS | `test_action_item_source_must_exist_in_known_originals` |
| 사용자 범위 격리 | PASS | 다른 `assignee_user_id` 결과 제외 |
| 미존재 원본 차단 | PASS | `action-missing` 결과 제외 |
| 상태 분류 회귀 | PASS | 전체 9 tests PASS |
| Python compileall | PASS | `compileall -q app` |
| diff 형식 | PASS | `git diff --check` |

총 9개 테스트 PASS, FAIL 0, SKIP 0이며 수동 검수·외부 Secret·실제 Provider 호출은 포함하지 않았다.

## 4. 자동 승인 및 다음 작업

- 자동 승인: 적용
- 자동 진행 판정: 정의된 검증 명령과 검수 항목이 모두 정확히 PASS
- 자동 진행 보류 사유: 없음
- 최신 승인 실행: `20260813-232223`
- 다음 착수 항목: M2.1-05 주간 집계·Artifact 입력 생성
- 재개 조건: 해당 없음

## 5. 범위와 보류

- 실제 회의 Action Item 원본을 생성·동기화하는 기능은 M3 회의 Workflow 범위다. 이 백로그는 원본 ID가 이미 조회된 경우의 연결·차단 규칙만 검증한다.
- 공개 Schema와 데이터 모델 변경은 수행하지 않았다.

## 6. 최종 판단

- 승인 여부: 승인
- 승인 방식: 자동 승인(검증 명령)
- 검수 의견: Action Item 원본 존재·사용자 범위·상태 제외 규칙이 결정적으로 검증되었고, 정의된 검증 명령이 모두 PASS했다.
