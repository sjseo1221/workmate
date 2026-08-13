# M0.2 모델·OAuth 확정 증빙

status: 재작업
latest_run_id: 20260813-130230
latest_run_status: FAIL (M0.2-05 실제 OAuth 재검증 timeout)
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
- M0.2-05 Calendar OAuth: 재작업, `AuthorizedSession` 전환 후 사용자 로컬 실제 OAuth·Watch 재검증 필요
- OAuth Client Secret·Access Token·Refresh Token은 읽거나 증빙에 기록하지 않는다.

## 실행

- 최신 실행: [`runs/20260813-130230/result.md`](runs/20260813-130230/result.md)
- M0.2-02 최신 실행: [`runs/20260813-114046/result.md`](runs/20260813-114046/result.md)
- M0.2-03 최신 실행: [`runs/20260813-121052/result.md`](runs/20260813-121052/result.md)
- M0.2-04 최신 실행: [`runs/20260813-122007/result.md`](runs/20260813-122007/result.md)
- M0.2-05 최신 실행: [`runs/20260813-122321/result.md`](runs/20260813-122321/result.md)
- M0.2-05 최신 재검수: [`runs/20260813-130230/result.md`](runs/20260813-130230/result.md)
- 코드·메타데이터 검증 실행: [`runs/20260813-082016/result.md`](runs/20260813-082016/result.md)
- 평가 계획: [`docs/11-llm-evaluation-plan.md`](../../../11-llm-evaluation-plan.md)
- 평가 원본: [`llm-evaluation/README.md`](../../../../llm-evaluation/README.md)

## 승인 조건

모델 평가와 외부 OAuth는 사람의 판단이 필요한 항목이므로 자동 승인하지 않는다. 이전 승인 실행 `20260813-122321`은 보존하지만 최신 재검수 `20260813-130230`에 실제 API FAIL과 Watch 미실행이 있어 M0.2-05를 `재작업`으로 유지한다. 모든 항목이 정확히 PASS인 새 실행 전에는 M0.2 통합 검수로 이동하지 않는다.
