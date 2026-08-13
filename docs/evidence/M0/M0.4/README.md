status: 검수 중
latest_run_id: 20260813-155933
latest_run_status: PASS (UI 육안 검수 대기)
latest_approved_run_id: null
approved_at: null
reviewer: null

# M0.4 내부 검증 UI

M0.4-01 최소 입력 UI를 구현했다. 페이지는 OIDC Bearer Token을 저장하지 않고
현재 브라우저 요청에만 사용하며, Skill 목록·자연어/JSON 입력을 기존 내부 API에
전달한다. UI 육안 검수 전까지 M0.4를 완료 처리하지 않는다.

- 최신 실행: [`20260813-155933/result.md`](runs/20260813-155933/result.md)
- 검수 중 백로그: M0.4-01 Skill·입력 UI
- 다음 착수 항목: M0.4-01 UI 육안 검수 승인 후 M0.4-02 결과·상태 UI

현재 runtime bootstrap 응답은 내부 Artifact에 `mock: true`, `business_result: false`로 표시한다. 이 응답은 API 경계 테스트에만 사용하며 실제 업무 결과·완료 증빙으로 승인하지 않는다.
