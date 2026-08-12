from __future__ import annotations

import argparse
import asyncio
import base64
import json
import os
import wave
from urllib.request import Request, urlopen

import websockets


def load_env(path: str) -> None:
    try:
        for line in open(path, encoding="utf-8"):
            if "=" in line and not line.lstrip().startswith("#"):
                key, value = line.strip().split("=", 1)
                os.environ.setdefault(key, value.strip().strip('"'))
    except FileNotFoundError:
        pass


def create_meeting(base_url: str) -> dict:
    request = Request(f"{base_url}/meetings", method="POST")
    with urlopen(request, timeout=10) as response:
        return json.loads(response.read())


def post_json(url: str, payload: dict) -> dict:
    request = Request(url, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}, method="POST")
    with urlopen(request, timeout=10) as response:
        return json.loads(response.read())


async def run(base_url: str, audio_path: str, chunk_ms: int, real_stt: bool, llm_analysis: bool) -> None:
    meeting = create_meeting(base_url)
    meeting_id, session_id = meeting["meeting_id"], meeting["recording_session_id"]
    with wave.open(audio_path, "rb") as audio:
        raw = audio.readframes(audio.getnframes())
        frame_bytes = max(1, int(audio.getframerate() * chunk_ms / 1000) * audio.getsampwidth() * audio.getnchannels())
    chunks = [raw[offset:offset + frame_bytes] for offset in range(0, len(raw), frame_bytes)]
    uri = base_url.replace("http://", "ws://").replace("https://", "wss://") + f"/meetings/{meeting_id}/recording?session_id={session_id}"
    reconnect_at = max(1, len(chunks) // 2)
    acknowledged = set()
    partial_count = 0
    for start, end in ((0, reconnect_at), (reconnect_at, len(chunks))):
        async with websockets.connect(uri) as socket:
            for chunk_no in range(start, end):
                await socket.send(json.dumps({"chunk_no": chunk_no, "audio_base64": base64.b64encode(chunks[chunk_no]).decode(), "sample_rate": 16000, "format": "pcm16"}))
                while True:
                    event = json.loads(await socket.recv())
                    if event.get("type") == "transcript.partial":
                        partial_count += 1
                        continue
                    if event.get("type") != "chunk_ack":
                        raise RuntimeError(event)
                    acknowledged.add(event["chunk_no"])
                    if not event.get("duplicate"):
                        partial = json.loads(await socket.recv())
                        if partial.get("type") == "transcript.partial":
                            partial_count += 1
                    break
            if start == reconnect_at:
                await socket.send(json.dumps({"chunk_no": reconnect_at - 1, "audio_base64": base64.b64encode(chunks[reconnect_at - 1]).decode(), "sample_rate": 16000, "format": "pcm16"}))
                duplicate = json.loads(await socket.recv())
                assert duplicate["duplicate"] is True
    request = Request(f"{base_url}/meetings/{meeting_id}/recording/complete", data=json.dumps({"session_id": session_id}).encode(), headers={"Content-Type": "application/json"}, method="POST")
    with urlopen(request, timeout=10) as response:
        completed = json.loads(response.read())
    transcript = "Mock 최종 transcript"
    action_items = []
    if real_stt:
        load_env("../stt-evaluation/.env")
        from openai import OpenAI
        client = OpenAI(base_url=os.getenv("OPENAI_STT_BASE_URL"), api_key=os.environ["OPENAI_STT_API_KEY"])
        with open(audio_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(model=os.getenv("OPENAI_STT_MODEL", "gpt-4o-transcribe"), file=audio_file, language="ko", response_format="json").text
    if llm_analysis:
        load_env("../llm-evaluation/.env")
        from openai import OpenAI
        llm = OpenAI(base_url=os.getenv("OPENAI_BASE_URL2"), api_key=os.environ["OPENAI_API_KEY2"])
        prompt = "회의 transcript에서 명시적으로 담당자와 기한이 드러난 Action Item만 JSON으로 추출하라. 없으면 빈 배열을 반환하라. 형식: {\\\"action_items\\\":[{\\\"title\\\":string,\\\"assignee\\\":string|null,\\\"due_at\\\":string|null,\\\"evidence_text\\\":string}]}"
        response = llm.chat.completions.create(model=os.environ["OPENAI_MODEL2"], messages=[{"role": "system", "content": prompt}, {"role": "user", "content": transcript}], temperature=0)
        raw = response.choices[0].message.content or "{}"
        try:
            action_items = json.loads(raw).get("action_items", [])
        except json.JSONDecodeError:
            action_items = []
    analysis = post_json(f"{base_url}/meetings/{meeting_id}/analysis", {"session_id": session_id, "transcript": transcript, "action_items": action_items})
    with urlopen(f"{base_url}/meetings/{meeting_id}/analysis", timeout=10) as response:
        status = json.loads(response.read())
    assert analysis["task"]["state"] == "TASK_STATE_COMPLETED"
    assert status["artifact"]["transcript"] == transcript
    retry = None
    if llm_analysis:
        failed = post_json(f"{base_url}/meetings/{meeting_id}/analysis/fail", {"session_id": session_id})
        resumed = post_json(f"{base_url}/meetings/{meeting_id}/analysis/retry", {"session_id": session_id})
        assert failed["task"]["state"] == "TASK_STATE_FAILED"
        assert resumed["task"]["state"] == "TASK_STATE_WORKING"
        retry = {"failed": failed, "resumed": resumed}
    review = None
    if llm_analysis and status["artifact"]["action_items"]:
        first = status["artifact"]["action_items"][0]["action_item_id"]
        edited = post_json(f"{base_url}/meetings/{meeting_id}/actions/{first}/review", {"decision": "edit", "changes": {"assignee": "user-456"}})
        approved = post_json(f"{base_url}/meetings/{meeting_id}/actions/{first}/review", {"decision": "approve"})
        repeated = post_json(f"{base_url}/meetings/{meeting_id}/actions/{first}/review", {"decision": "approve"})
        assert approved["action_item"]["approval_status"] == "approved"
        assert repeated["idempotent"] is True
        registered = post_json(f"{base_url}/meetings/{meeting_id}/actions/{first}/register-task", {})
        duplicate_task = post_json(f"{base_url}/meetings/{meeting_id}/actions/{first}/register-task", {})
        assert duplicate_task["idempotent"] is True
        assert duplicate_task["task_id"] == registered["task_id"]
        review = {"edited": edited, "approved": approved, "repeated_idempotent": repeated["idempotent"], "task_registration": registered, "duplicate_task": duplicate_task}
    print(json.dumps({"meeting_id": meeting_id, "chunk_count": len(chunks), "acknowledged": len(acknowledged), "partial_count": partial_count, "duplicate_ack": True, "complete": completed, "analysis": analysis, "action_review": review, "retry": retry, "stt_mode": "real" if real_stt else "mock", "llm_mode": "real" if llm_analysis else "mock", "status_check": "completed"}, ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8010")
    parser.add_argument("--audio", required=True)
    parser.add_argument("--chunk-ms", type=int, default=200)
    parser.add_argument("--real-stt", action="store_true")
    parser.add_argument("--llm-analysis", action="store_true")
    args = parser.parse_args()
    asyncio.run(run(args.base_url, args.audio, args.chunk_ms, args.real_stt, args.llm_analysis))


if __name__ == "__main__":
    main()
