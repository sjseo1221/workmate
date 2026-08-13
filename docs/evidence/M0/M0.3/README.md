status: 완료
latest_run_id: 20260813-153001
latest_run_status: PASS
latest_approved_run_id: 20260813-153001
approved_at: 2026-08-13 15:30 Asia/Seoul
reviewer: 자동 승인(검증 명령)

# M0.3 내부 챗봇 API

M0.3-01의 입력 경계와 M0.3-02의 공통 Workflow 호출 경계를 구현·검수한다.
M0.3-04의 인증·Schema·사용자 범위·부분 실패 경계까지 운영 OIDC 코드 경로와
로컬 JWKS Contract Test로 검증했다. 정의된 검증 명령이 모두 PASS하여 자동 승인했다.

- 최신 실행: [`20260813-153001/result.md`](runs/20260813-153001/result.md)
- 승인된 백로그: M0.3-01, M0.3-02, M0.3-03, M0.3-04
- 다음 착수 항목: M0.4-01 Skill·입력 UI
- 운영 경로는 공유 Workflow 경계를 호출하며, 실제 Gmail·Calendar·업무 DB 결과는 후속 M1~M4에서 연결한다.
