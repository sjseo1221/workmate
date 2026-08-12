from __future__ import annotations

import json
import os
import sqlite3
import base64
from pathlib import Path


DB_PATH = Path(os.getenv("RECORDING_DB_PATH", Path(__file__).parents[1] / "results" / "recording-test.db"))


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.execute("CREATE TABLE IF NOT EXISTS meetings (meeting_id TEXT PRIMARY KEY, payload TEXT NOT NULL)")
    return connection


def load_all() -> dict[str, dict]:
    with _connect() as connection:
        return {meeting_id: json.loads(payload, object_hook=_decode) for meeting_id, payload in connection.execute("SELECT meeting_id, payload FROM meetings")}


def save(meeting: dict) -> None:
    with _connect() as connection:
        connection.execute("INSERT OR REPLACE INTO meetings(meeting_id, payload) VALUES (?, ?)", (meeting["meeting_id"], json.dumps(meeting, ensure_ascii=False, default=_encode)))


def _encode(value: object) -> object:
    if isinstance(value, bytes):
        return {"__bytes__": base64.b64encode(value).decode()}
    raise TypeError(type(value).__name__)


def _decode(value: dict) -> object:
    if "__bytes__" in value:
        return base64.b64decode(value["__bytes__"])
    return value


def clear() -> None:
    with _connect() as connection:
        connection.execute("DELETE FROM meetings")
