status: 완료
latest_run_id: 20260814-170010
latest_run_status: PASS
latest_approved_run_id: 20260814-170010
approved_at: 2026-08-14
reviewer: 자동 승인(검증 명령)

# M5.4 시나리오 시연

8개 업무 시나리오를 Main Orchestrator API로 실행하고, 각 장기 Task가 `succeeded`에 도달하는지 검증한다.

| 시나리오 | 결과 |
| --- | --- |
| 오늘 브리핑 | PASS |
| 주간 업무보고 | PASS |
| 회의 분석 | PASS |
| 이전 회의록 검색 | PASS |
| 우선순위 재계산 | PASS |
| 할 일 등록 | PASS |
| Task 상태 조회 | PASS |
| Task 재시도 | PASS |

추가로 실제 `POST /api/tasks/{task_id}/retry`를 호출해 `running → succeeded` 전이를 확인했다.

## 실행 조건

- Orchestrator: `http://127.0.0.1:8000`
- Workmate adapter: `http://127.0.0.1:8012`
- 사용자 Fixture: `00000000-0000-0000-0000-000000000001`
- 회의 Fixture: `00000000-0000-0000-0000-000000000101`
- 모든 시나리오 최종 상태: `succeeded`
- Secret·Token·응답 원문: 저장하지 않음
