status: 검수 중
latest_run_id: 20260813-160824
latest_run_status: PASS (UI 육안 검수 대기)
latest_approved_run_id: 20260813-160540
approved_at: 2026-08-13 16:05 Asia/Seoul
reviewer: 사용자 확인

# M0.4 내부 검증 UI

M0.4-01 최소 입력 UI를 구현하고 사용자 육안 검수를 완료했다. 페이지는 OIDC Bearer
Token을 저장하지 않고 현재 브라우저 요청에만 사용하며, Skill 목록·자연어/JSON 입력을
기존 내부 API에 전달한다.

- 최신 실행: [`20260813-160540/result.md`](runs/20260813-160540/result.md)
- 승인된 백로그: M0.4-01 Skill·입력 UI
- 승인된 백로그: M0.4-01 Skill·입력 UI
- 검수 중 백로그: M0.4-02 결과·상태 UI
- 다음 착수 항목: M0.4-02 UI 육안 검수

현재 runtime bootstrap 응답은 내부 Artifact에 `mock: true`, `business_result: false`로 표시한다. 이 응답은 API 경계 테스트에만 사용하며 실제 업무 결과·완료 증빙으로 승인하지 않는다.
