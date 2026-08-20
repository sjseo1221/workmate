# M1.5-04 실제 Provider 재검수 결과

## 1. 기본 정보

- 마일스톤: M1.5
- 제목: 올바른 Agent 경로에서 실제 `daily_briefing` 재검수
- 담당자: Codex
- 검수자: 미승인
- 상태: 재작업
- 실행일: 2026-08-13
- 실행 ID: 20260813-224350

## 2. 최신 실행과 승인

- latest_run_id: 20260813-224350
- latest_run_status: FAIL
- latest_approved_run_id: 20260813-222105
- approved_at: 2026-08-13 22:21 Asia/Seoul (M1.5-03)

## 3. 실행 결과

| 항목 | 결과 | 근거 |
| --- | --- | --- |
| `workmate-agent/app` import 경로 | PASS | `workdir=C:\dev\workmate\workmate-agent` |
| OAuth access token 로드 | FAIL | OAuth Client JSON 상대 경로 해석 실패 |
| 실제 `daily_briefing` | 미실행 | 토큰 로드 단계에서 중단 |

## 4. 문제와 재개 조건

- 발견된 문제: `auth_flow.load_config()`가 `.env`와 상대 파일 경로를 현재 작업 디렉터리 기준으로 해석한다.
- 오류: `FileNotFoundError: OAuth Client JSON이 없습니다: client_secret.json`
- 원인: OAuth helper는 `google-oauth-test`에서 실행되어야 하지만, Agent import를 위해 전체 명령의 작업 디렉터리를 `workmate-agent`로 변경했다.
- 해결 방법: 별도 하위 프로세스에서 OAuth 작업 디렉터리를 `google-oauth-test`로 고정해 토큰을 얻은 뒤, 토큰 값만 환경 변수로 전달하여 Agent Workflow는 `workmate-agent`에서 실행한다.
- 재검수 조건: 토큰 로드와 Workflow 실행의 작업 디렉터리를 각각 고정하고 `mock=false`, `warnings=[]`, Gmail·Calendar 응답 건수를 확인한다.

## 5. 최종 판단

- 승인 여부: 미승인
- 검수 의견: 공개 Secret은 노출되지 않았으며 실제 Provider 호출 전에 실패했다. 검수 명령 FAIL로 즉시 중단했다.
- 다음 조치: OAuth helper와 Agent Workflow의 작업 디렉터리를 분리한 검수 명령으로 재실행한다.
