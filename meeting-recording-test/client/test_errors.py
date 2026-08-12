from __future__ import annotations

import argparse
import asyncio
import base64
import json
import wave
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import websockets


def create(base: str) -> dict:
    with urlopen(Request(f"{base}/meetings", method="POST"), timeout=10) as response:
        return json.loads(response.read())


async def main_async(base: str, audio_path: str) -> None:
    meeting = create(base)
    with wave.open(audio_path, "rb") as audio:
        chunk = audio.readframes(max(1, int(audio.getframerate() * 0.2)))
    uri = base.replace("http://", "ws://") + f"/meetings/{meeting['meeting_id']}/recording?session_id={meeting['recording_session_id']}"
    async with websockets.connect(uri) as socket:
        payload = lambda number: json.dumps({"chunk_no": number, "audio_base64": base64.b64encode(chunk).decode(), "sample_rate": 16000, "format": "pcm16"})
        await socket.send(payload(1))
        gap = json.loads(await socket.recv())
        assert gap["code"] == "CHUNK_GAP", gap
        await socket.send(payload(0))
        first = json.loads(await socket.recv())
        if first.get("type") == "transcript.partial":
            first = json.loads(await socket.recv())
        assert first["duplicate"] is False, first
        partial = json.loads(await socket.recv())
        assert partial.get("type") == "transcript.partial", partial
        await socket.send(payload(0))
        duplicate = json.loads(await socket.recv())
        if duplicate.get("type") == "transcript.partial":
            duplicate = json.loads(await socket.recv())
        assert duplicate["duplicate"] is True, duplicate
    bad = Request(f"{base}/meetings/{meeting['meeting_id']}/recording/complete", data=json.dumps({"session_id": "wrong"}).encode(), headers={"Content-Type": "application/json"}, method="POST")
    try:
        urlopen(bad, timeout=10)
    except HTTPError as error:
        assert error.code == 404, error.code
    else:
        raise AssertionError("invalid session was accepted")
    print(json.dumps({"chunk_gap_rejected": True, "duplicate_ack": True, "invalid_session_rejected": True}, ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8010")
    parser.add_argument("--audio", required=True)
    args = parser.parse_args()
    asyncio.run(main_async(args.base_url, args.audio))


if __name__ == "__main__":
    main()
