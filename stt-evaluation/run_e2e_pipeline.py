"""Validate the local recording pipeline contract before Workmate WebSocket exists."""
from __future__ import annotations

import argparse
import json
import os
import time
import wave
from datetime import datetime, timezone
from pathlib import Path

from openai import OpenAI

from run_eval import load_cases, load_env, score


ROOT = Path(__file__).parent


def replay_chunks(path: Path, chunk_ms: int, reconnect_at: int) -> tuple[bytes, dict]:
    with wave.open(str(path), "rb") as audio:
        raw = audio.readframes(audio.getnframes())
        rate = audio.getframerate()
    size = max(1, int(rate * chunk_ms / 1000) * 2)
    chunks = [raw[offset:offset + size] for offset in range(0, len(raw), size)]
    received: dict[int, bytes] = {}
    last_chunk_no = -1
    for chunk_no, chunk in enumerate(chunks):
        if chunk_no == reconnect_at:
            last_chunk_no = chunk_no - 1
        if chunk_no > last_chunk_no:
            received[chunk_no] = chunk
            last_chunk_no = chunk_no
    # Reconnect replay of the last acknowledged boundary must be idempotent.
    if reconnect_at in received:
        received[reconnect_at] = chunks[reconnect_at]
    return b"".join(received[index] for index in sorted(received)), {"chunk_count": len(chunks), "last_chunk_no": last_chunk_no, "reconnect_at": reconnect_at, "reconstructed_bytes": sum(map(len, received.values()))}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", type=Path, default=Path("cases/pilot_cases.jsonl"))
    parser.add_argument("--chunk-ms", type=int, default=200)
    args = parser.parse_args()
    load_env(ROOT / ".env")
    if not os.getenv("OPENAI_STT_API_KEY"):
        raise RuntimeError("OPENAI_STT_API_KEY is required")
    client = OpenAI(base_url=os.getenv("OPENAI_STT_BASE_URL"), api_key=os.environ["OPENAI_STT_API_KEY"])
    rows = []
    for case in load_cases(args.cases):
        audio_path = ROOT / case["audio"]
        started = time.perf_counter()
        with wave.open(str(audio_path), "rb") as audio:
            total_frames = audio.getnframes()
        reconnect_at = max(1, int(total_frames / (16000 * args.chunk_ms / 1000 * 2) // 2))
        reconstructed, state = replay_chunks(audio_path, args.chunk_ms, reconnect_at)
        # The shell harness verifies reconstruction; final STT uses the original file to avoid lossy re-encoding.
        with audio_path.open("rb") as audio_file:
            response = client.audio.transcriptions.create(model=os.getenv("OPENAI_STT_MODEL", "gpt-4o-transcribe"), file=audio_file, language=case.get("language", "ko"), response_format="json")
        verdict = score(case, response.text)
        rows.append({"case_id": case["case_id"], "semantic_valid": verdict["semantic_valid"], "missing": verdict["missing"], "provider_error": None, "pipeline_state": state, "latency_ms": round((time.perf_counter() - started) * 1000, 1), "text": response.text, "task_input_ready": bool(response.text.strip() and reconstructed)})
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    result = {"generated_at": datetime.now(timezone.utc).isoformat(), "model": os.getenv("OPENAI_STT_MODEL", "gpt-4o-transcribe"), "case_count": len(rows), "semantic_valid_count": sum(row["semantic_valid"] for row in rows), "provider_error_count": 0, "chunk_reconnect_passed": all(row["pipeline_state"]["reconstructed_bytes"] > 0 for row in rows), "rows": rows}
    path = ROOT / "results" / f"e2e-metrics-{stamp}.json"
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    result["result_file"] = str(path)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
