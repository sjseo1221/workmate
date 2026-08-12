from __future__ import annotations

import base64
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from .storage import load_all, save


app = FastAPI(title="Meeting Recording Test Mock")
MEETINGS: dict[str, dict] = load_all()


@app.get("/health/live")
def health_live() -> dict[str, str]:
    return {"status": "alive"}


@app.get("/health/ready")
def health_ready() -> dict[str, str]:
    return {"status": "ready"}


class CompleteRequest(BaseModel):
    session_id: str


class AnalysisRequest(BaseModel):
    session_id: str
    transcript: str
    action_items: list[dict] = []


class ActionReviewRequest(BaseModel):
    decision: str
    changes: dict = {}


@app.post("/meetings")
def create_meeting() -> dict:
    meeting_id = f"meeting-{uuid4()}"
    session_id = f"session-{uuid4()}"
    MEETINGS[meeting_id] = {"meeting_id": meeting_id, "session_id": session_id, "last_chunk_no": -1, "chunks": {}, "status": "recording"}
    save(MEETINGS[meeting_id])
    return {"meeting_id": meeting_id, "recording_session_id": session_id}


@app.websocket("/meetings/{meeting_id}/recording")
async def recording_socket(websocket: WebSocket, meeting_id: str, session_id: str) -> None:
    await websocket.accept()
    meeting = MEETINGS.get(meeting_id)
    if not meeting or meeting["session_id"] != session_id:
        await websocket.close(code=4404, reason="recording session not found")
        return
    try:
        while True:
            payload = await websocket.receive_json()
            chunk_no = payload.get("chunk_no")
            encoded = payload.get("audio_base64")
            if not isinstance(chunk_no, int) or not isinstance(encoded, str):
                await websocket.send_json({"type": "error", "code": "INVALID_CHUNK"})
                continue
            if chunk_no in meeting["chunks"]:
                await websocket.send_json({"type": "chunk_ack", "chunk_no": chunk_no, "duplicate": True})
                continue
            if chunk_no > meeting["last_chunk_no"] + 1:
                await websocket.send_json({"type": "error", "code": "CHUNK_GAP", "expected": meeting["last_chunk_no"] + 1})
                continue
            try:
                audio = base64.b64decode(encoded, validate=True)
            except ValueError:
                await websocket.send_json({"type": "error", "code": "INVALID_AUDIO"})
                continue
            meeting["chunks"][chunk_no] = audio
            meeting["last_chunk_no"] = max(meeting["last_chunk_no"], chunk_no)
            save(meeting)
            await websocket.send_json({"type": "chunk_ack", "chunk_no": chunk_no, "duplicate": False, "last_chunk_no": meeting["last_chunk_no"]})
            await websocket.send_json({"type": "transcript.partial", "chunk_no": chunk_no, "text": f"chunk-{chunk_no}"})
    except WebSocketDisconnect:
        return


@app.post("/meetings/{meeting_id}/recording/complete")
def complete_recording(meeting_id: str, request: CompleteRequest) -> dict:
    meeting = MEETINGS.get(meeting_id)
    if not meeting or meeting["session_id"] != request.session_id:
        raise HTTPException(404, "recording session not found")
    meeting["status"] = "completed"
    meeting["task"] = {"id": f"task-{uuid4()}", "state": "TASK_STATE_WORKING", "created_at": datetime.now(timezone.utc).isoformat()}
    save(meeting)
    return {"meeting_id": meeting_id, "status": "completed", "chunk_count": len(meeting["chunks"]), "task": meeting["task"]}


@app.post("/meetings/{meeting_id}/analysis")
def finish_analysis(meeting_id: str, request: AnalysisRequest) -> dict:
    meeting = MEETINGS.get(meeting_id)
    if not meeting or meeting["session_id"] != request.session_id:
        raise HTTPException(404, "recording session not found")
    if meeting.get("status") != "completed":
        raise HTTPException(409, "recording is not completed")
    action_items = []
    for item in request.action_items:
        action_items.append({**item, "action_item_id": f"action-{uuid4()}", "approval_status": "pending", "task_id": None})
    meeting["analysis"] = {"transcript": request.transcript, "action_items": action_items, "artifact_type": "meeting_analysis"}
    meeting["task"]["state"] = "TASK_STATE_COMPLETED"
    meeting["task"]["completed_at"] = datetime.now(timezone.utc).isoformat()
    save(meeting)
    return {"meeting_id": meeting_id, "task": meeting["task"], "artifact": meeting["analysis"]}


@app.get("/meetings/{meeting_id}/analysis")
def get_analysis(meeting_id: str) -> dict:
    meeting = MEETINGS.get(meeting_id)
    if not meeting:
        raise HTTPException(404, "meeting not found")
    return {"meeting_id": meeting_id, "task": meeting.get("task"), "artifact": meeting.get("analysis")}


@app.post("/meetings/{meeting_id}/analysis/fail")
def fail_analysis(meeting_id: str, request: CompleteRequest) -> dict:
    meeting = MEETINGS.get(meeting_id)
    if not meeting or meeting["session_id"] != request.session_id:
        raise HTTPException(404, "recording session not found")
    meeting["task"]["state"] = "TASK_STATE_FAILED"
    meeting["task"]["error"] = {"code": "MOCK_PROVIDER_ERROR", "retryable": True}
    save(meeting)
    return {"task": meeting["task"]}


@app.post("/meetings/{meeting_id}/analysis/retry")
def retry_analysis(meeting_id: str, request: CompleteRequest) -> dict:
    meeting = MEETINGS.get(meeting_id)
    if not meeting or meeting["session_id"] != request.session_id:
        raise HTTPException(404, "recording session not found")
    task = meeting["task"]
    if task["state"] != "TASK_STATE_FAILED":
        raise HTTPException(409, "only failed Task can be retried")
    attempts = task.get("attempts", 0) + 1
    if attempts > 3:
        raise HTTPException(409, "retry limit exceeded")
    task["attempts"] = attempts
    task["state"] = "TASK_STATE_WORKING"
    task.pop("error", None)
    save(meeting)
    return {"task": task, "retryable": True}


@app.get("/meetings/{meeting_id}/actions")
def list_actions(meeting_id: str) -> dict:
    meeting = MEETINGS.get(meeting_id)
    if not meeting:
        raise HTTPException(404, "meeting not found")
    return {"meeting_id": meeting_id, "action_items": meeting.get("analysis", {}).get("action_items", [])}


@app.post("/meetings/{meeting_id}/actions/{action_item_id}/review")
def review_action(meeting_id: str, action_item_id: str, request: ActionReviewRequest) -> dict:
    meeting = MEETINGS.get(meeting_id)
    if not meeting:
        raise HTTPException(404, "meeting not found")
    if request.decision not in {"approve", "edit", "reject"}:
        raise HTTPException(400, "decision must be approve, edit, or reject")
    for item in meeting.get("analysis", {}).get("action_items", []):
        if item["action_item_id"] != action_item_id:
            continue
        if item["approval_status"] in {"approved", "rejected"} and request.decision == "approve" and item["approval_status"] == "approved":
            return {"action_item": item, "idempotent": True}
        if request.decision == "edit":
            item.update(request.changes)
        item["approval_status"] = {"approve": "approved", "edit": "pending", "reject": "rejected"}[request.decision]
        save(meeting)
        return {"action_item": item, "idempotent": False}
    raise HTTPException(404, "action item not found")


@app.post("/meetings/{meeting_id}/actions/{action_item_id}/register-task")
def register_task(meeting_id: str, action_item_id: str) -> dict:
    meeting = MEETINGS.get(meeting_id)
    if not meeting:
        raise HTTPException(404, "meeting not found")
    for item in meeting.get("analysis", {}).get("action_items", []):
        if item["action_item_id"] != action_item_id:
            continue
        if item["approval_status"] != "approved":
            raise HTTPException(409, "action item must be approved")
        if item.get("task_id"):
            return {"task_id": item["task_id"], "action_item_id": action_item_id, "idempotent": True}
        item["task_id"] = f"task-{uuid4()}"
        save(meeting)
        return {"task_id": item["task_id"], "action_item_id": action_item_id, "idempotent": False}
    raise HTTPException(404, "action item not found")
