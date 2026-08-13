# Google OAuth Scope Test 이력

실제 OAuth Token, Client Secret, Gmail 원문과 Calendar 상세 데이터는 기록하지 않는다.

## 2026-08-11 — 테스트 하네스 구성

- 대상 Scope: Gmail readonly, Google Calendar readonly
- 별도 테스트 폴더와 `.env.example`, Secret 제외 규칙 구성
- OAuth·Gmail Profile/Message/History·Calendar Events 호출 실행기 구성
- `--dry-run`과 설정 단위 테스트 경로 구성
- 실제 Google API Client 라이브러리 설치 완료
- `smoke_test.py --dry-run` 통과
- 설정 단위 테스트 2건과 Python 구문 검사 통과
- 실제 OAuth 실행 결과: `client_secret.json` 미제공으로 브라우저 인증 전 중단
- 상태: Google Cloud Desktop OAuth Client JSON과 테스트 계정 인증이 필요함

## 2026-08-11 — 실제 OAuth 전 준비 검증

- 검증된 항목: Scope 목록, 설정 경로, Secret 제외 규칙, OAuth 실행기, Gmail·Calendar API 호출 코드
- 미실행 항목: OAuth 동의, Refresh Token, Gmail Message/History, Calendar Events, Gmail Watch, Calendar Watch
- 중단 원인: 저장소에 OAuth Client JSON을 두지 않았으며 실제 Secret을 자동 생성하거나 추측하지 않음

## 2026-08-11 — OAuth Redirect Port 오류 수정

- 오류: 고정 포트 8765 바인딩 시 Windows `WinError 10013`
- 원인: 해당 포트가 사용 중이거나 OS 정책상 예약되어 localhost Redirect Server가 열리지 않음
- 수정: `GOOGLE_REDIRECT_PORT`를 추가하고 기본값을 `0`으로 설정해 빈 포트를 자동 선택

## 2026-08-11 — 기본 OAuth·Readonly API 검증

- 실행 결과: 사용자가 제공한 실제 실행 결과 기준 통과
- Scope: Gmail readonly, Google Calendar readonly
- OAuth Client JSON: 존재
- Token: 기존 Token 사용 및 API 호출 성공
- Gmail: Profile·Message·History 조회 통과
- Calendar: Events 조회 통과
- Gmail Message 1건, Calendar Event 1건 조회 확인
- 결과 시각: `2026-08-11T05:41:51Z`
- 상태: 기본 OAuth와 Readonly API 통과

## 2026-08-11 — Watch 검증 보류

- Gmail Pub/Sub Topic: 미설정
- Calendar 공개 HTTPS Callback: 미설정
- `smoke_test.py --watch`는 설정 누락을 먼저 검증하도록 보정
- Gmail Watch·Calendar Watch와 실제 증분 알림은 Pub/Sub Topic 및 공개 HTTPS Callback 준비 후 재개
- 상태: OAuth 기본 검증 통과, Push/증분 동기화 검증 보류

## 2026-08-11 — Gmail·Calendar Watch 등록 검증

- 실행: `smoke_test.py --watch`
- Gmail Profile·Message·History 조회: 통과
- Gmail Watch 등록: 통과 (`historyId`, `expiration` 반환 확인)
- Calendar Events 조회: 통과
- Calendar Events Watch 등록: 통과 (`resourceId`, `expiration` 반환 확인)
- 실제 변경 이벤트를 발생시켜 Callback 수신까지 확인하는 단계는 readonly Scope 특성상 수동 변경 이벤트가 필요함
- 상태: OAuth·Readonly API·Watch Channel 등록 통과; 실제 Push 전달과 증분 재동기화는 수동 이벤트로 추가 확인 필요

## 2026-08-13 — `httplib2` IPv6 fallback 문제와 전송 경로 교체

- 사용자 로컬 venv에서 같은 Gmail Profile URL을 `requests`로 호출하면 HTTP 401 응답을 받았으나 `httplib2`는 timeout이 발생함
- `httplib2`의 주소 조회를 IPv4로 제한하면 같은 URL에서 HTTP 401 응답을 확인해 IPv6 timeout 뒤 IPv4 fallback 실패를 원인으로 확정함
- `site-packages` 수정이나 전역 socket monkeypatch 대신 `google.auth.transport.requests.AuthorizedSession` 기반 REST 호출로 테스트 하네스를 교체함
- 설정·readonly·Watch Fake 회귀 테스트 3건, dry-run, Python 구문 검사 통과
- Codex 관리형 실행 환경의 실제 OAuth 재검증은 120초 timeout으로 미완료이며 사용자 로컬 재실행 필요
- 상태: 전송 경로 수정 완료, 실제 OAuth·Watch 재검증 전까지 재작업

## 기록 양식

```text
실행 일시:
테스트 계정:
Scope:
OAuth 결과:
Gmail 결과:
Calendar 결과:
Watch/History/syncToken 결과:
Refresh Token 결과:
실패와 원인:
최종 판단:
```
