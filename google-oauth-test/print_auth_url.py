"""`run_local_server()`(로컬 서버+브라우저 자동 실행)가 원인 불명으로 계속 조용히
실패하는 환경을 위한 수동 대체 스크립트 1/2.

이 스크립트는 인증 URL만 출력한다. 브라우저에 붙여넣어 Google 로그인·동의를
마치면 `http://localhost/...?code=...`로 리다이렉트되는데, 그 페이지 자체는
아무것도 안 떠도(로컬에 서버가 없으므로 정상) 주소창의 `code=` 값만 복사해
`python exchange_code.py <code>`에 넘기면 된다(2/2).
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from google_auth_oauthlib.flow import Flow

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar.readonly",
]

REDIRECT_URI = "http://localhost"


VERIFIER_PATH = Path(__file__).resolve().parent / ".pkce_verifier"


def main() -> None:
    load_dotenv()
    secret_path = Path(os.getenv("GOOGLE_CLIENT_SECRET_FILE", "client_secret.json"))
    if not secret_path.exists():
        raise FileNotFoundError(f"OAuth Client JSON이 없습니다: {secret_path}")
    flow = Flow.from_client_secrets_file(str(secret_path), scopes=SCOPES, redirect_uri=REDIRECT_URI)
    auth_url, _ = flow.authorization_url(access_type="offline", prompt="consent")
    # `authorization_url()`이 자동 생성한 PKCE code_verifier는 이 Flow 인스턴스
    # 안에만 있다 — `exchange_code.py`는 별도 프로세스라 이걸 모르면 Google이
    # "Missing code verifier"로 거부한다. 다음 단계가 읽을 수 있게 저장해 둔다.
    VERIFIER_PATH.write_text(flow.code_verifier, encoding="utf-8")
    print(auth_url)


if __name__ == "__main__":
    main()
