from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar.readonly",
]


def load_config() -> tuple[Path, Path]:
    load_dotenv()
    secret = Path(os.getenv("GOOGLE_CLIENT_SECRET_FILE", "client_secret.json"))
    token = Path(os.getenv("GOOGLE_TOKEN_FILE", "token.json"))
    return secret, token


def redirect_port() -> int:
    value = os.getenv("GOOGLE_REDIRECT_PORT", "0")
    try:
        port = int(value)
    except ValueError as error:
        raise ValueError("GOOGLE_REDIRECT_PORT는 정수여야 합니다.") from error
    if port < 0 or port > 65535:
        raise ValueError("GOOGLE_REDIRECT_PORT는 0~65535 범위여야 합니다.")
    return port


def authenticate(*, dry_run: bool = False) -> Credentials | None:
    secret_path, token_path = load_config()
    if dry_run:
        return None
    if not secret_path.exists():
        raise FileNotFoundError(
            f"OAuth Client JSON이 없습니다: {secret_path}. "
            "Google Cloud Desktop Client JSON을 이 경로에 두세요."
        )

    credentials = None
    if token_path.exists():
        credentials = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
    elif not credentials or not credentials.valid:
        flow = InstalledAppFlow.from_client_secrets_file(str(secret_path), SCOPES)
        credentials = flow.run_local_server(
            port=redirect_port(), access_type="offline", prompt="consent"
        )
    token_path.write_text(credentials.to_json(), encoding="utf-8")
    return credentials
