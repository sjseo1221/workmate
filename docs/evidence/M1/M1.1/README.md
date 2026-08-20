status: 완료
latest_run_id: 20260813-194043
latest_run_status: PASS (5 fixture tests; compileall/diff PASS)
latest_approved_run_id: 20260813-194043
approved_at: 2026-08-13 19:40 Asia/Seoul
reviewer: 자동 승인(검증 명령)

# M1.1 업무 DB 기반

## 계획 상태

`M0.4-03`이 실제 장기 Task 부재로 `보류(선행 M1.3 대기)`인 상태에서 M1.1 업무 DB 기반을 진행한다. M1.1-01 Migration 초안과 M1.1-02 Task Repository 경계는 승인되었으며, 동기화 상태 Repository와 M1.1 통합 검수는 아직 남아 있다.

## 백로그 범위

- M1.1-01 업무 도메인 Migration 초안
- M1.1-02 Task Repository 경계 (완료, 실행 `20260813-192221`)
- M1.1-03 외부 동기화 상태 Repository (완료, 실행 `20260813-193615`)
- M1.1-04 샘플 데이터·Fixture (완료, 실행 `20260813-194043`)
- M1.1-05 Migration·Repository 통합 검수 (완료, 실행 `20260813-193901`)

## 기준 문서

- [`docs/03-data-priority-rules.md`](../../../03-data-priority-rules.md)
- [`docs/06-delivery-plan.md`](../../../06-delivery-plan.md)
- [`docs/07-technical-specification.md`](../../../07-technical-specification.md)
- [`docs/02-a2a-interface.md`](../../../02-a2a-interface.md)

## 구현 전 확인 사항

- M0.1 A2A 인프라 Migration과 M1.1 업무 도메인 Migration의 책임을 분리한다.
- 모든 Repository 조회에 요청 `user_id`를 적용한다.
- Task Soft Delete와 원본 중복 방지를 데이터 경계에서 보장한다.
- 실제 업무 Workflow가 연결되기 전까지 운영 경로에 Mock·고정 샘플 응답을 추가하지 않는다.
- 공개 Schema·DDL 필드 또는 unique constraint 변경이 필요하면 구현 전에 별도 승인과 Contract Test 갱신을 받는다.

최신 실행 결과: [`20260813-194043/result.md`](runs/20260813-194043/result.md)

실행 결과가 생기면 이 폴더의 `runs/{run_id}/result.md`에 구현 요약·변경 전후 동작·테스트 명령·결과를 기록하고, 승인된 실행만 이 README의 `latest_approved_run_id`에 연결한다. M1.1-04는 `20260813-194043`에서 5개 Fixture 테스트와 정적 검사를 정확히 PASS하여 자동 승인했다. M1.1-01~05가 모두 승인되어 M1.1을 완료 처리했으며, Fixture는 운영 경로에 연결하지 않는다.
