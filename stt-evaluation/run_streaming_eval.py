"""Replay 16 kHz PCM WAV chunks through OpenAI Realtime transcription."""
from __future__ import annotations

import argparse
from array import array
import asyncio
import base64
import json
import os
import time
import wave
from datetime import datetime, timezone
from pathlib import Path

import websockets

from run_eval import load_cases, load_env, score


ROOT = Path(__file__).parent


def resample_pcm16(raw: bytes, source_rate: int, target_rate: int = 24000) -> bytes:
    if source_rate == target_rate:
        return raw
    source = array("h"); source.frombytes(raw)
    output = array("h")
    for index in range(round(len(source) * target_rate / source_rate)):
        position = index * source_rate / target_rate
        left = min(int(position), len(source) - 1)
        right = min(left + 1, len(source) - 1)
        output.append(round(source[left] + (source[right] - source[left]) * (position - left)))
    return output.tobytes()


async def evaluate_case(case: dict, url: str, key: str, model: str, chunk_ms: int) -> dict:
    path = ROOT / case["audio"]
    started = time.perf_counter()
    partials: list[str] = []
    completed_parts: list[str] = []
    first_result_ms = None
    async with websockets.connect(url, additional_headers={"Authorization": f"Bearer {key}"}, max_size=16 * 1024 * 1024) as socket:
        await socket.send(json.dumps({"type": "session.update", "session": {"type": "transcription", "audio": {"input": {"format": {"type": "audio/pcm", "rate": 24000}, "transcription": {"model": model, "language": case.get("language", "ko")}}}}}))
        with wave.open(str(path), "rb") as audio:
            if audio.getnchannels() != 1 or audio.getsampwidth() != 2:
                raise ValueError(f"{path.name} must be mono 16-bit WAV")
            raw = resample_pcm16(audio.readframes(audio.getnframes()), audio.getframerate())
            frames = max(1, int(24000 * chunk_ms / 1000))
            for offset in range(0, len(raw), frames * 2):
                chunk = raw[offset:offset + frames * 2]
                await socket.send(json.dumps({"type": "input_audio_buffer.append", "audio": base64.b64encode(chunk).decode()}))
                await asyncio.sleep(chunk_ms / 1000)
            await socket.send(json.dumps({"type": "input_audio_buffer.commit"}))
        deadline = time.perf_counter() + 45
        while time.perf_counter() < deadline:
            try:
                event = json.loads(await asyncio.wait_for(socket.recv(), timeout=5))
            except asyncio.TimeoutError:
                if completed_parts:
                    break
                continue
            kind = event.get("type", "")
            if kind.endswith(".delta") and "transcription" in kind:
                partials.append(event.get("delta", ""))
                first_result_ms = first_result_ms or round((time.perf_counter() - started) * 1000, 1)
            elif kind == "conversation.item.input_audio_transcription.completed":
                completed_parts.append(event.get("transcript", ""))
                if len(completed_parts) >= 1:
                    deadline = time.perf_counter() + 5
            elif kind.endswith(".failed") or kind == "error":
                raise RuntimeError(event.get("error", event))
    completed = " ".join(completed_parts)
    verdict = score(case, completed)
    return {"case_id": case["case_id"], "semantic_valid": verdict["semantic_valid"], "missing": verdict["missing"], "text": completed, "partial_count": len(partials), "first_result_ms": first_result_ms, "final_result_ms": round((time.perf_counter() - started) * 1000, 1), "provider_error": None}


async def main_async(args: argparse.Namespace) -> None:
    load_env(ROOT / ".env")
    cases = load_cases(args.cases)
    url = os.getenv("OPENAI_STT_REALTIME_URL", "wss://api.openai.com/v1/realtime?intent=transcription")
    key = os.getenv("OPENAI_STT_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_STT_API_KEY is required")
    rows = []
    for case in cases:
        try:
            rows.append(await evaluate_case(case, url, key, os.getenv("OPENAI_STT_MODEL", "gpt-4o-transcribe"), args.chunk_ms))
        except Exception as exc:
            rows.append({"case_id": case["case_id"], "semantic_valid": False, "missing": [], "text": "", "partial_count": 0, "first_result_ms": None, "final_result_ms": None, "provider_error": str(exc)})
    valid = sum(row["semantic_valid"] for row in rows)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    result = {"generated_at": datetime.now(timezone.utc).isoformat(), "model": os.getenv("OPENAI_STT_MODEL", "gpt-4o-transcribe"), "case_count": len(rows), "semantic_valid_count": valid, "semantic_valid_rate": valid / len(rows), "provider_error_count": sum(bool(row["provider_error"]) for row in rows), "rows": rows}
    output = ROOT / "results" / f"streaming-metrics-{stamp}.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    result["result_file"] = str(output)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--chunk-ms", type=int, default=200)
    asyncio.run(main_async(parser.parse_args()))


if __name__ == "__main__":
    main()
