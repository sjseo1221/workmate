import os
from typing import Any
from uuid import uuid4

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


A2A_VERSION = "1.0"
SERVICE_TOKEN = os.getenv("SERVICE_TOKEN", "dev-service-token")
WORKMATE_BASE_URL = os.getenv(
    "WORKMATE_BASE_URL", "http://host.docker.internal:8001/a2a/v1"
).rstrip("/")


class InvokeRequest(BaseModel):
    skill_id: str
    user_id: str = "test-user"
    workspace_id: str = "test-workspace"
    payload: dict[str, Any] = Field(default_factory=dict)


app = FastAPI(title="A2A Smoke Orchestrator")


@app.post("/invoke")
async def invoke(request: InvokeRequest) -> dict[str, Any]:
    envelope = {
        "message": {
            "messageId": f"msg-{uuid4()}",
            "role": "ROLE_USER",
            "parts": [
                {
                    "data": {
                        "schema_version": "1.0",
                        "skill_id": request.skill_id,
                        "user_id": request.user_id,
                        "workspace_id": request.workspace_id,
                        **request.payload,
                    },
                    "mediaType": "application/json",
                }
            ],
        },
        "configuration": {
            "acceptedOutputModes": ["application/json", "text/markdown"]
        },
        "metadata": {"request_id": f"req-{uuid4()}"},
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                f"{WORKMATE_BASE_URL}/message:send",
                json=envelope,
                headers={
                    "Authorization": f"Bearer {SERVICE_TOKEN}",
                    "A2A-Version": A2A_VERSION,
                },
            )
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail=f"Workmate connection failed: {exc}") from exc

    if response.is_error:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()


@app.get("/workmate/agent-card")
async def get_workmate_agent_card() -> dict[str, Any]:
    agent_root = WORKMATE_BASE_URL.removesuffix("/a2a/v1")
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(f"{agent_root}/.well-known/agent-card.json")
            response.raise_for_status()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Agent Card lookup failed: {exc}") from exc
    return response.json()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "orchestrator"}
