# M5.1 검수 결과

## 목적

담당 Orchestrator를 변경하지 않고 Workmate adapter만으로 회의 분석·검색 payload를 전달할 수 있는지 확인했다.

## 확인 결과

| 확인 항목 | 결과 | 근거 |
| --- | --- | --- |
| Orchestrator Task 입력 | 제한됨 | `TaskRequest`는 `request: str`만 수용 |
| Workmate 요청 생성 | 제한됨 | `build_agent_request()`가 `message`, `skill_id`, `mode` 중심으로 생성 |
| A2A HTTP+JSON 변환 | 확장 가능 | `A2AClient`가 `data` Part와 metadata를 생성 |
| 회의 분석 payload 전달 | 현재 불가 | `meeting_id`, 최종 Transcript가 없음 |
| 회의 검색 payload 전달 | 현재 불가 | `query`, filters와 DB/Embedding 설정이 없음 |
| Workmate 공개 계약 변경 없이 해결 | 가능 | Orchestrator 내부에 Skill별 payload builder를 추가하고 adapter는 전달만 담당 |

## 권장 변경 경계

1. Orchestrator `TaskRequest`에 선택적 `skill_id`와 `payload`를 추가한다.
2. `build_agent_request()`가 `daily_briefing`, `rank_priorities`, `weekly_report`, `analyze_meeting`, `search_meetings`별 `data` Part를 만든다.
3. `A2AClient`는 이미 JSON `data` Part를 지원하므로 Workmate 공개 Schema는 변경하지 않는다.
4. Compose 검수용으로만 비식별 meeting fixture와 PostgreSQL/pgvector를 제공한다.

## 결론

adapter만 수정해서는 회의 분석·검색을 실제 업무 Workflow로 검수할 수 없다. 담당 Orchestrator 내부의 선택적 구조화 payload 확장이 필요하다. 현재 코드는 변경하지 않았으며, 해당 계약 확장 전까지 M5.1 자동 착수를 중단한다.
