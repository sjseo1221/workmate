from __future__ import annotations

import argparse
import json
import os
import uuid
from datetime import datetime, timezone
from urllib.parse import quote

from google.auth.transport.requests import AuthorizedSession

from auth_flow import SCOPES, authenticate, load_config


def request_json(session: AuthorizedSession, method: str, url: str, **kwargs) -> dict:
    """Google REST API를 호출하고 성공한 JSON 응답을 반환한다."""
    response = session.request(method, url, timeout=30, **kwargs)
    response.raise_for_status()
    return response.json()


def run(*, dry_run: bool, watch: bool) -> dict:
    """OAuth 설정 또는 Gmail·Calendar readonly API 계약을 검증한다."""
    secret_path, token_path = load_config()
    result = {
        "scopes": SCOPES,
        "dry_run": dry_run,
        "client_secret_present": secret_path.exists(),
        "token_present_before": token_path.exists(),
        "checks": {},
    }
    if dry_run:
        result["checks"] = {"config": "pass", "secret_not_required": "pass"}
        return result

    topic = os.getenv("GOOGLE_GMAIL_PUBSUB_TOPIC")
    address = os.getenv("GOOGLE_CALENDAR_WATCH_ADDRESS")
    if watch and (not topic or not address):
        raise RuntimeError(
            "Watch 검증에는 GOOGLE_GMAIL_PUBSUB_TOPIC과 "
            "GOOGLE_CALENDAR_WATCH_ADDRESS(공개 HTTPS)가 필요합니다."
        )

    session = AuthorizedSession(authenticate())
    gmail_base = "https://gmail.googleapis.com/gmail/v1/users/me"
    profile = request_json(session, "GET", f"{gmail_base}/profile")
    messages = request_json(
        session, "GET", f"{gmail_base}/messages", params={"maxResults": 1}
    )
    history = request_json(
        session,
        "GET",
        f"{gmail_base}/history",
        params={"startHistoryId": profile["historyId"], "maxResults": 1},
    )
    calendar_id = os.getenv("GOOGLE_CALENDAR_ID", "primary")
    calendar_url = (
        "https://www.googleapis.com/calendar/v3/calendars/"
        f"{quote(calendar_id, safe='')}/events"
    )
    events = request_json(
        session,
        "GET",
        calendar_url,
        params={"maxResults": 1, "singleEvents": "true"},
    )

    result["checks"] = {
        "gmail_profile": "pass",
        "gmail_messages": "pass",
        "gmail_history": "pass",
        "calendar_events": "pass",
    }
    result["gmail"] = {
        "message_count": len(messages.get("messages", [])),
        "history_id_present": bool(profile.get("historyId")),
        "history_page_present": bool(history),
    }
    result["calendar"] = {"event_count": len(events.get("items", []))}

    if watch:
        gmail_watch = request_json(
            session,
            "POST",
            f"{gmail_base}/watch",
            json={
                "topicName": topic,
                "labelIds": ["INBOX"],
                "labelFilterBehavior": "INCLUDE",
            },
        )
        channel = request_json(
            session,
            "POST",
            f"{calendar_url}/watch",
            json={
                "id": str(uuid.uuid4()),
                "type": "web_hook",
                "address": address,
                "token": os.getenv("GOOGLE_CALENDAR_WATCH_TOKEN", "oauth-test"),
            },
        )
        result["watch"] = {
            "gmail_history_id_present": bool(gmail_watch.get("historyId")),
            "gmail_expiration_present": bool(gmail_watch.get("expiration")),
            "calendar_resource_id_present": bool(channel.get("resourceId")),
            "calendar_expiration_present": bool(channel.get("expiration")),
        }
        result["checks"]["watch"] = "pass"
    result["checked_at"] = datetime.now(timezone.utc).isoformat()
    return result


def main() -> None:
    """명령행 옵션을 읽어 OAuth 검증 결과를 JSON으로 출력한다."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--watch", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run(dry_run=args.dry_run, watch=args.watch), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
