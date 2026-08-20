# M1.5-04 실제 Provider 재검수 결과

## 1. 기본 정보

- 마일스톤: M1.5
- 제목: Gmail·Calendar 실제 `daily_briefing` 재검수
- 담당자: Codex
- 검수자: 사용자 승인 대기
- 상태: 검수 중
- 실행일: 2026-08-13
- 실행 ID: 20260813-224808

## 2. 최신 실행과 승인

- latest_run_id: 20260813-224808
- latest_run_status: PASS
- latest_approved_run_id: 20260813-222105
- approved_at: 2026-08-13 22:21 Asia/Seoul (M1.5-03)

## 3. 목표와 완료 기준

- 목표: 실제 Gmail·Calendar OAuth 자격 증명으로 `daily_briefing` Workflow를 실행한다.
- 완료 기준: 실제 Provider 응답, `mock=false`, 경고 없음, 관련 회귀 테스트와 문서 검사가 모두 PASS한다.
- 미완료·보류: 외부 Provider 검수 결과에 대한 사용자 승인.

## 4. 실행 결과

| 항목 | 결과 | 근거 |
| --- | --- | --- |
| Gmail readonly scope 및 API | PASS | `google-oauth-test/smoke_test.py`와 실제 Workflow |
| Calendar readonly scope 및 API | PASS | `google-oauth-test/smoke_test.py`와 실제 Workflow |
| `daily_briefing` typed result | PASS | `type=daily_briefing`, `mock=false` |
| Provider 경고 | PASS | `warning_codes=[]` |
| 관련 자동화 회귀 | PASS | 30 tests |
| Python 구문·문서 diff | PASS | `compileall`, `git diff --check` |

비식별 집계 결과는 Gmail 신호 100건, 오늘 범위 Calendar 이벤트 0건, 검수용 Task 0건, `source_refs` 100건이다. Token·메일 본문·일정 제목은 기록하지 않았다.

## 5. 실행 명령과 결과

```text
# OAuth helper는 google-oauth-test, Workflow는 workmate-agent 작업 디렉터리에서 실행
.\.venv\Scripts\python.exe -m unittest tests.test_daily_briefing tests.test_priority_workflow tests.test_priority_repository tests.test_priority_domain tests.test_google_adapters tests.test_contract -q
.\.venv\Scripts\python.exe -m compileall -q app tests
git diff --check
```

- 자동 재작업 착수: 예
- 이전 실패 해소: OAuth 토큰 로드와 Agent 실행의 작업 디렉터리를 분리하여 PASS
- Secret 처리: access token은 프로세스 환경 변수로만 전달하고 실행 후 제거

## 6. 최종 판단

- 승인 여부: 사용자 승인 대기
- 검수 의견: 정의된 기술 검증은 모두 PASS했다. 외부 OAuth·실제 Provider 검증은 정책상 자동 승인 대상이 아니므로 명시 승인을 기다린다.
- 다음 조치: 사용자 승인 후 M1.5-04 완료 처리 및 M1.5-05 통합·회귀 검수 착수.
