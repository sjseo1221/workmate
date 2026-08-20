status: 완료
latest_run_id: 20260813-225921
latest_run_status: PASS
latest_approved_run_id: 20260813-225921
approved_at: 2026-08-13 22:59 Asia/Seoul
reviewer: 자동 승인(검증 명령)

# M1.5 우선순위·브리핑

## 계획 검토 상태

M1.5 구현 전 문서·Schema·기존 M1 승인 경계를 대조한 뒤 M1.5-01~04를 구현·검수하고 M1.5-05 통합·회귀 검수를 완료했다.

## 확인한 기준

- [`docs/03-data-priority-rules.md`](../../../03-data-priority-rules.md)
- [`docs/02-a2a-interface.md`](../../../02-a2a-interface.md)
- [`docs/04-scenarios.md`](../../../04-scenarios.md)
- [`docs/07-technical-specification.md`](../../../07-technical-specification.md)
- [`docs/schemas/workmate-skill-schemas.schema.json`](../../../schemas/workmate-skill-schemas.schema.json)
- 승인된 M1.1·M1.2·M1.3·M1.4 증빙

## 계획 검토 결론

구현 전 다음 경계를 고정해야 한다.

1. 공식 점수식과 `priority_hint`(0~10)→중요도(0~20) 매핑
2. 사용자 timezone·`as_of`·DST·동점 정렬
3. `PrioritySnapshot` Migration·Repository와 이전 Snapshot 비교
4. Calendar 연관성 판정 및 `calendar_relevance` 시간 창
5. `blocked_or_overdue` 동시 조건과 Task 스키마 밖 정보의 처리
6. `rank_priorities`의 Gmail 미호출 및 인증 subject/user_id 일치
7. `daily_briefing`의 Provider 부분 실패·`warnings`·데이터 최신성

상세 백로그는 [`docs/06-delivery-plan.md`의 M1.5 계획](../../../06-delivery-plan.md#216-m15-우선순위브리핑-구현-계획-검토)에 기록했다.

## 다음 단계

최신 실행 결과: [`M1.5-05 통합·회귀 검수 결과`](runs/20260813-225921/result.md)

M1.5-04 `daily_briefing` Workflow의 실제 Provider 실행은 이전 실행에서 사용자 승인되었다. M1.5-05에서 PostgreSQL 통합 5개, 기존 M0/M1 회귀 80개, 컴파일·diff·성능 검사를 모두 PASS했다. 자동 승인 규칙에 따라 M1.5를 완료 처리하고 M2.1을 다음 작업으로 착수한다.
