# M0.2 모델·OAuth 확정 증빙

status: 진행
latest_run_id: 20260813-122321
latest_run_status: PASS_WITH_CAVEAT (M0.2-05 Calendar OAuth 사용자 승인)
latest_approved_run_id: 20260813-122321 (M0.2-05)
approved_at: 2026-08-13 12:27 Asia/Seoul (M0.2-05)
reviewer: 사용자 승인 (M0.2-05)

## 목표

LLM·Embedding·STT 모델과 Gmail·Calendar OAuth Scope의 선택 근거, 평가 원본, 미검증 위험을 확인해 M0.2의 설계·검수 상태를 확정한다.

## 현재 범위

- M0.2-01 LLM 평가 원본·Schema·재평가 Trigger 검수: 완료
- M0.2-02 Embedding 평가: 완료
- M0.2-03 STT 평가: 완료
- M0.2-04 Gmail OAuth: 완료
- M0.2-05 Calendar OAuth: 완료
- OAuth Client Secret·Access Token·Refresh Token은 읽거나 증빙에 기록하지 않는다.

## 실행

- 최신 실행: [`runs/20260813-114046/result.md`](runs/20260813-114046/result.md)
- M0.2-02 최신 실행: [`runs/20260813-114046/result.md`](runs/20260813-114046/result.md)
- M0.2-03 최신 실행: [`runs/20260813-121052/result.md`](runs/20260813-121052/result.md)
- M0.2-04 최신 실행: [`runs/20260813-122007/result.md`](runs/20260813-122007/result.md)
- M0.2-05 최신 실행: [`runs/20260813-122321/result.md`](runs/20260813-122321/result.md)
- 코드·메타데이터 검증 실행: [`runs/20260813-082016/result.md`](runs/20260813-082016/result.md)
- 평가 계획: [`docs/11-llm-evaluation-plan.md`](../../../11-llm-evaluation-plan.md)
- 평가 원본: [`llm-evaluation/README.md`](../../../../llm-evaluation/README.md)

## 승인 조건

모델 평가와 외부 OAuth는 사람의 판단이 필요한 항목이므로 자동 승인하지 않는다. M0.2-01~05는 각각 사용자 승인을 완료했다. M0.2-05의 현재 환경 외부 API 재실행 보류는 증빙에 남겼다. M0.2 하위 백로그는 모두 완료됐으며 통합 검수로 이동한다.
