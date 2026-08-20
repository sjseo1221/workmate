"""`print_auth_url.py`(1/2)의 URL로 동의를 마친 뒤, 리다이렉트된 주소창의
`code=` 값을 이 스크립트에 넘겨 `token.json`을 만든다(2/2).

사용법: python exchange_code.py "<code 값>"
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from urllib.parse import unquote

from dotenv import load_dotenv
from google_auth_oauthlib.flow import Flow

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar.readonly",
]

REDIRECT_URI = "http://localhost"
VERIFIER_PATH = Path(__file__).resolve().parent / ".pkce_verifier"


def main() -> None:
    if len(sys.argv) != 2:
        print('사용법: python exchange_code.py "<code 값>"')
        raise SystemExit(1)
    # 주소창에 보이는 code는 URL 인코딩된 상태일 수 있다(예: %2F → /) — 그대로
    # 넘기면 Google이 거부하므로 여기서 디코딩한다.
    code = unquote(sys.argv[1])
    if not VERIFIER_PATH.exists():
        raise FileNotFoundError(
            f"{VERIFIER_PATH}가 없습니다 — print_auth_url.py를 먼저 실행해 새 URL부터 다시 받으세요"
            "(code 하나당 검증 값도 하나뿐이라, 검증 값이 없으면 이전에 받은 code는 재사용할 수 없습니다)."
        )
    code_verifier = VERIFIER_PATH.read_text(encoding="utf-8")

    load_dotenv()
    secret_path = Path(os.getenv("GOOGLE_CLIENT_SECRET_FILE", "client_secret.json"))
    token_path = Path(os.getenv("GOOGLE_TOKEN_FILE", "token.json"))
    if not secret_path.exists():
        raise FileNotFoundError(f"OAuth Client JSON이 없습니다: {secret_path}")

    flow = Flow.from_client_secrets_file(
        str(secret_path), scopes=SCOPES, redirect_uri=REDIRECT_URI, code_verifier=code_verifier
    )
    flow.fetch_token(code=code)
    VERIFIER_PATH.unlink(missing_ok=True)
    token_path.write_text(flow.credentials.to_json(), encoding="utf-8")
    print(f"저장 완료: {token_path}")
    print(f"scopes: {flow.credentials.scopes}")


if __name__ == "__main__":
    main()
