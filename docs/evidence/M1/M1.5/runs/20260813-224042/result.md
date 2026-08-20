# M1.5-04 실제 Provider 재검수 결과

## 1. 기본 정보

- 마일스톤: M1.5
- 제목: Gmail·Calendar scope 및 실제 `daily_briefing` 재검수
- 담당자: Codex
- 검수자: 미승인
- 상태: 재작업
- 실행일: 2026-08-13
- 실행 ID: 20260813-224042

## 2. 최신 실행과 승인

- latest_run_id: 20260813-224042
- latest_run_status: FAIL
- latest_approved_run_id: 20260813-222105
- approved_at: 2026-08-13 22:21 Asia/Seoul (M1.5-03)

## 3. 목표와 완료 기준

- 목표: 저장된 로컬 OAuth 자격 증명으로 Gmail·Calendar scope와 실제 `daily_briefing` 응답을 검증한다.
- 완료 기준: Gmail·Calendar 실호출과 `daily_briefing` Workflow가 모두 PASS한다.
- 미완료·보류: `daily_briefing` 실행 명령의 Python module path 수정 후 재검수.

## 4. 검수 결과

| 항목 | 결과 | 근거 |
| --- | --- | --- |
| Gmail readonly scope 및 profile/messages/history | PASS | `google-oauth-test/smoke_test.py` |
| Calendar readonly scope 및 events | PASS | `google-oauth-test/smoke_test.py` |
| 실제 `daily_briefing` Workflow | FAIL | `ModuleNotFoundError: No module named 'app'` |

Google 실호출의 비식별 결과는 Gmail message 1건, Calendar event 1건이었다. Secret과 Token 값은 기록하지 않았다.

## 5. 문제와 재개 조건

- 발견된 문제: 검수 명령을 `google-oauth-test` 작업 디렉터리에서 실행해 `workmate-agent/app`을 import하지 못했다.
- 원인: `PYTHONPATH` 또는 실행 작업 디렉터리가 `C:\dev\workmate\workmate-agent`로 지정되지 않았다.
- 재현 결과: `ModuleNotFoundError: No module named 'app'`
- 수정 방법: 토큰을 가져온 뒤 작업 디렉터리를 `workmate-agent`로 변경하거나 `PYTHONPATH=C:\dev\workmate\workmate-agent`를 설정한다.
- 재검수 조건: 동일 OAuth 자격 증명으로 수정된 명령을 실행하고 Gmail·Calendar 응답, `mock=false`, `warnings=[]`를 확인한다.

## 6. 최종 판단

- 승인 여부: 미승인
- 검수 의견: 실제 Google scope와 개별 API는 PASS했지만 `daily_briefing` 검수가 실행 전에 실패했으므로 M1.5-04를 승인하지 않는다.
- 다음 조치: 실행 작업 디렉터리를 수정한 뒤 M1.5-04 실제 Provider 재검수를 다시 실행한다.
