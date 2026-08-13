# M0.2 모델·OAuth 확정 증빙

status: 진행
latest_run_id: 20260813-121052
latest_run_status: PASS_WITH_CAVEAT (M0.2-03 STT 검수)
latest_approved_run_id: 20260813-114046 (M0.2-02)
approved_at: 2026-08-13 11:53 Asia/Seoul (M0.2-02)
reviewer: 사용자 승인 (M0.2-02)

## 목표

LLM·Embedding·STT 모델과 Gmail·Calendar OAuth Scope의 선택 근거, 평가 원본, 미검증 위험을 확인해 M0.2의 설계·검수 상태를 확정한다.

## 현재 범위

- M0.2-01 LLM 평가 원본·Schema·재평가 Trigger 검수: 완료
- M0.2-02 Embedding 평가: 완료
- M0.2-03 STT 평가: 검수 중, 사용자 승인 필요
- M0.2-04~05는 후속 백로그이며 M0.2 전체 완료 전까지 진행한다.
- OAuth Client Secret·Access Token·Refresh Token은 읽거나 증빙에 기록하지 않는다.

## 실행

- 최신 실행: [`runs/20260813-114046/result.md`](runs/20260813-114046/result.md)
- M0.2-02 최신 실행: [`runs/20260813-114046/result.md`](runs/20260813-114046/result.md)
- M0.2-03 최신 실행: [`runs/20260813-121052/result.md`](runs/20260813-121052/result.md)
- 코드·메타데이터 검증 실행: [`runs/20260813-082016/result.md`](runs/20260813-082016/result.md)
- 평가 계획: [`docs/11-llm-evaluation-plan.md`](../../../11-llm-evaluation-plan.md)
- 평가 원본: [`llm-evaluation/README.md`](../../../../llm-evaluation/README.md)

## 승인 조건

모델 평가는 사람의 판단이 필요한 항목이므로 자동 승인하지 않는다. M0.2-01과 M0.2-02는 각각 사용자 승인을 완료했다. M0.2-03은 합성 파일·Realtime·Chunk 재연결 결과가 통과했으나 실제 회의 음성 품질은 M3.3으로 이관하는 범위와 STT MVP 사양을 사용자 확인 중이다. M0.2 전체 상태는 `진행`으로 유지한다.
