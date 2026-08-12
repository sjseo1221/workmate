import json
import os
from urllib.request import Request, urlopen


ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_URL", "http://localhost:9000")
SKILLS = (
    "daily_briefing",
    "weekly_report",
    "analyze_meeting",
    "search_meetings",
    "rank_priorities",
)


for skill_id in SKILLS:
    request = Request(
        f"{ORCHESTRATOR_URL}/invoke",
        data=json.dumps({"skill_id": skill_id}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=15) as response:
        result = json.load(response)

    data = result["task"]["artifacts"][0]["parts"][1]["data"]
    assert data["invoked_skill"] == skill_id
    print(f"PASS {skill_id}: {data['message']}")
