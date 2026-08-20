status: 완료
latest_run_id: 20260813-232643
latest_run_status: PASS
latest_approved_run_id: 20260813-232643
approved_at: 2026-08-13 23:26 Asia/Seoul
reviewer: 자동 승인(검증 명령)

# M2.1 주간 데이터 분류

## 1. 착수 정보

- 목표: 승인된 Task·Gmail·Calendar·회의 Action Item을 사용자별 주간 기간으로 분류하고 `weekly_report` 입력용 구조화 결과를 만든다.
- 상태: 완료
- 착수일: 2026-08-13
- 담당자: Codex
- 선행 조건: M1.5 완료 (`20260813-225921`)
- 다음 승인 단위: M2.2 다음 주 계획 근거 추출

## 2. 범위

- 포함: 주간 기간·timezone 정규화, Task 상태 분류, 승인된 외부 원본 연결, Action Item source ID 연결, 네 목록 집계, 부분 실패 `warnings`.
- 제외: LLM 보고서 문장 생성·Artifact 최종 생성(M2.3), 다음 주 계획 확정(M2.2), 보고서 UI(M2.4).
- 보안: 모든 조회는 요청 `user_id`로 제한하고 승인되지 않은 Provider 신호와 다른 사용자 source ID는 제외한다.
- Mock 정책: Mock은 단위·계약 Fixture에만 허용하며 운영 Workflow에는 고정 보고서 응답이나 Mock fallback을 두지 않는다.

## 3. 백로그

상세 구현·검수 계획은 [`docs/06-delivery-plan.md`의 M2.1 계획](../../../06-delivery-plan.md#217-m21-주간-데이터-분류-백로그-정의-및-구현-계획)을 기준으로 한다.

| ID | 작업 | 상태 | 완료 조건 |
| --- | --- | --- | --- |
| M2.1-01 | 주간 기간·사용자 범위 정규화 | 완료 | timezone·DST·주 경계·user_id 테스트 PASS |
| M2.1-02 | Task 상태 분류 | 완료 | 완료·진행·지연·취소·삭제 분류 PASS |
| M2.1-03 | Gmail·Calendar 승인 Task 연결 | 완료 | [`M2.1-03 실행 결과`](runs/20260813-231904/result.md) · 승인 원본·source_refs·사용자 격리 PASS |
| M2.1-04 | 회의 Action Item 연결 경계 | 완료 | [`M2.1-04 실행 결과`](runs/20260813-232223/result.md) · action_item source ID 검증 PASS |
| M2.1-05 | 주간 집계·Artifact 입력 생성 | 완료 | [`M2.1-05 실행 결과`](runs/20260813-232437/result.md) · 목록·기간·source_refs Schema PASS |
| M2.1-06 | 통합·부분 실패 검수 | 완료 | [`M2.1-06 실행 결과`](runs/20260813-232643/result.md) · 실제 Repository·부분 실패·회귀 모두 PASS |

## 4. 검수 기록 규칙

- 작업 시작 전 이 README를 준비하고, 실행 결과가 생긴 뒤 `runs/{run_id}/result.md`를 작성한다.
- 정의된 검증 명령과 검수 항목이 모두 정확히 `PASS`이고 `SKIP`·수동 검수·차단이 없으면 자동 승인하고 다음 백로그를 즉시 착수한다.
- `PASS`가 아닌 결과가 나오면 정규 후속 착수를 멈추고 실패 원인·재현 명령·재개 조건을 기록한다.
- 실제 Provider·UI 육안 검수·공개 Schema 변경·원격 Push는 별도 승인 없이는 자동 착수하지 않는다.
