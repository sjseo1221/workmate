from __future__ import annotations

import argparse
import json
import os
import uuid
from datetime import datetime, timezone

from googleapiclient.discovery import build

from auth_flow import SCOPES, authenticate, load_config


def run(*, dry_run: bool, watch: bool) -> dict:
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

    credentials = authenticate()
    gmail = build("gmail", "v1", credentials=credentials, cache_discovery=False)
    calendar = build("calendar", "v3", credentials=credentials, cache_discovery=False)

    profile = gmail.users().getProfile(userId="me").execute()
    messages = gmail.users().messages().list(userId="me", maxResults=1).execute()
    history = gmail.users().history().list(
        userId="me", startHistoryId=profile["historyId"], maxResults=1
    ).execute()
    calendar_id = os.getenv("GOOGLE_CALENDAR_ID", "primary")
    events = calendar.events().list(calendarId=calendar_id, maxResults=1, singleEvents=True).execute()

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
        gmail_watch = gmail.users().watch(
            userId="me",
            body={"topicName": topic, "labelIds": ["INBOX"], "labelFilterBehavior": "INCLUDE"},
        ).execute()
        channel = calendar.events().watch(
            calendarId=calendar_id,
            body={
                "id": str(uuid.uuid4()),
                "type": "web_hook",
                "address": address,
                "token": os.getenv("GOOGLE_CALENDAR_WATCH_TOKEN", "oauth-test"),
            },
        ).execute()
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--watch", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run(dry_run=args.dry_run, watch=args.watch), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
