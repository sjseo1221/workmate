from __future__ import annotations

import json
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
        # 저장된 Token이 실제로 어떤 범위에 동의됐는지 원본 JSON에서 먼저 직접
        # 확인한다 — `Credentials.from_authorized_user_file(path, SCOPES)`처럼
        # `scopes`를 명시해서 불러오면 라이브러리가 파일의 실제 "scopes" 값을
        # 버리고 우리가 요청한 SCOPES로 덮어써 버린다. 그 상태에서는
        # `credentials.has_scopes(SCOPES)`가 실제로 동의받은 적 없는 범위(예:
        # Calendar)도 이미 있는 것처럼 항상 True를 반환해서, 동의 화면을 다시
        # 띄워야 하는 상황인데도 조용히 기존(불충분한) Token만 Refresh하고
        # 끝나 버렸다 — "아무것도 안 뜸"의 진짜 원인.
        granted = set(json.loads(token_path.read_text(encoding="utf-8")).get("scopes") or [])
        if set(SCOPES).issubset(granted):
            credentials = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
    elif not credentials or not credentials.valid:
        flow = InstalledAppFlow.from_client_secrets_file(str(secret_path), SCOPES)
        # open_browser=False로 자동 실행에 기대지 않고 항상 URL을 콘솔에 출력한다 —
        # 환경에 따라 webbrowser.open()이 조용히 실패해(다른 창 뒤에 열리거나 기본
        # 브라우저 연결 문제) 아무 창도 안 뜬 것처럼 보이는 경우가 있었다.
        credentials = flow.run_local_server(
            port=redirect_port(), access_type="offline", prompt="consent", open_browser=False
        )
    token_path.write_text(credentials.to_json(), encoding="utf-8")
    return credentials
