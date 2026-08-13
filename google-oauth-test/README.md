# Google OAuth Scope Test

Gmail readonly와 Google Calendar readonly Scope를 Workmate에 적용하기 전 검증하는 독립 테스트다. 실제 Client Secret, Access Token, Refresh Token과 메일·일정 원문은 저장소에 넣지 않는다.

## 준비

```powershell
cd C:\dev\workmate\google-oauth-test
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Google Cloud에서 Gmail API, Google Calendar API를 활성화하고 Desktop OAuth Client JSON을 내려받아 `.env`의 `GOOGLE_CLIENT_SECRET_FILE` 경로에 둔다. 테스트 계정은 별도로 사용한다.

Google API 호출은 `google-auth`의 `AuthorizedSession`과 REST endpoint를 사용한다. `google-api-python-client`의 `httplib2` 전송은 IPv6 연결 timeout 뒤 IPv4로 fallback하지 않는 환경 차이가 확인돼 사용하지 않는다.

`GOOGLE_REDIRECT_PORT=0`이면 운영체제가 비어 있는 localhost 포트를 자동 선택한다. 특정 포트를 써야 할 때만 값으로 변경한다. 고정 포트가 Windows 정책이나 다른 프로세스에 의해 차단되면 `WinError 10013`이 발생할 수 있다.

## Scope

```text
https://www.googleapis.com/auth/gmail.readonly
https://www.googleapis.com/auth/calendar.readonly
```

## 실행

인증 없이 설정과 코드만 검사한다.

```powershell
python smoke_test.py --dry-run
python -m unittest discover -s tests
```

실제 OAuth와 readonly API를 호출한다. 첫 실행은 브라우저 동의 화면을 연다.

```powershell
python smoke_test.py
```

Gmail Watch와 Calendar Watch는 Pub/Sub·공개 HTTPS Callback이 준비된 뒤 별도로 실행한다.

```powershell
python smoke_test.py --watch
```

## 통과 기준

- OAuth 동의·localhost redirect·Refresh Token 갱신 성공
- Gmail profile/message/history 조회 성공
- Calendar list/events 조회 성공
- Watch 사용 시 Gmail historyId와 Calendar syncToken 흐름 확인
- 권한 철회·만료 오류를 민감정보 없이 기록
