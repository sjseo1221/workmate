import os
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field


A2A_VERSION = "1.0"
SERVICE_TOKEN = os.getenv("SERVICE_TOKEN", "dev-service-token")
PUBLIC_BASE_URL = os.getenv(
    "PUBLIC_BASE_URL", "http://localhost:8001/a2a/v1"
).rstrip("/")

SKILLS = {
    "daily_briefing": "오늘 업무 브리핑 Stub이 정상 호출되었습니다.",
    "weekly_report": "주간 업무보고 Stub이 정상 호출되었습니다.",
    "analyze_meeting": "회의 분석 Stub이 정상 호출되었습니다.",
    "search_meetings": "회의록 검색 Stub이 정상 호출되었습니다.",
    "rank_priorities": "우선순위 계산 Stub이 정상 호출되었습니다.",
}


class MessagePart(BaseModel):
    data: dict[str, Any]
    mediaType: str


class Message(BaseModel):
    messageId: str
    role: str
    parts: list[MessagePart]


class SendMessageRequest(BaseModel):
    message: Message
    configuration: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


app = FastAPI(title="Workmate A2A Smoke Agent")


@app.get("/.well-known/agent-card.json")
def agent_card() -> dict[str, Any]:
    return {
        "name": "Workmate AI Smoke Test",
        "description": "A2A Skill 라우팅만 검증하는 Workmate Stub Agent",
        "supportedInterfaces": [
            {
                "url": PUBLIC_BASE_URL,
                "protocolBinding": "HTTP+JSON",
                "protocolVersion": A2A_VERSION,
            }
        ],
        "provider": {"organization": "Game Team", "url": PUBLIC_BASE_URL},
        "version": "0.1.0",
        "capabilities": {
            "streaming": False,
            "pushNotifications": False,
            "extendedAgentCard": False,
        },
        "securitySchemes": {
            "serviceBearer": {
                "httpAuthSecurityScheme": {
                    "description": "Smoke Test Service Token",
                    "scheme": "Bearer",
                    "bearerFormat": "opaque",
                }
            }
        },
        "securityRequirements": [
            {"schemes": {"serviceBearer": {"list": []}}}
        ],
        "defaultInputModes": ["application/json"],
        "defaultOutputModes": ["application/json", "text/markdown"],
        "skills": [
            {
                "id": skill_id,
                "name": summary.split(" Stub")[0],
                "description": summary,
                "tags": ["smoke-test"],
                "examples": [],
            }
            for skill_id, summary in SKILLS.items()
        ],
    }


@app.post("/a2a/v1/message:send")
def send_message(
    envelope: SendMessageRequest,
    authorization: str | None = Header(default=None),
    a2a_version: str | None = Header(default=None, alias="A2A-Version"),
) -> dict[str, Any]:
    if authorization != f"Bearer {SERVICE_TOKEN}":
        raise HTTPException(status_code=401, detail="Invalid service token")
    if a2a_version != A2A_VERSION:
        raise HTTPException(status_code=400, detail="A2A-Version must be 1.0")
    if not envelope.message.parts:
        raise HTTPException(status_code=400, detail="Message parts are required")

    data = envelope.message.parts[0].data
    skill_id = data.get("skill_id")
    if skill_id not in SKILLS:
        raise HTTPException(status_code=400, detail=f"Unknown skill_id: {skill_id}")

    now = datetime.now(timezone.utc).isoformat()
    result = {
        "type": "smoke_test",
        "invoked_skill": skill_id,
        "message": SKILLS[skill_id],
        "received": data,
    }
    return {
        "task": {
            "id": f"task-{uuid4()}",
            "contextId": f"context-{uuid4()}",
            "status": {"state": "TASK_STATE_COMPLETED", "timestamp": now},
            "artifacts": [
                {
                    "artifactId": f"artifact-{uuid4()}",
                    "name": f"{skill_id} smoke result",
                    "parts": [
                        {
                            "text": f"# Skill 호출 성공\n\n- `{skill_id}`\n- {SKILLS[skill_id]}",
                            "mediaType": "text/markdown",
                        },
                        {"data": result, "mediaType": "application/json"},
                    ],
                }
            ],
            "createdAt": now,
            "lastModified": now,
        }
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "workmate"}
