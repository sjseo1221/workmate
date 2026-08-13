# M0.2 모델·OAuth 확정 증빙

status: 진행
latest_run_id: 20260813-131903
latest_run_status: PASS (사용자 로컬 실제 OAuth·Watch 결과)
latest_approved_run_id: 20260813-131903 (M0.2-05)
approved_at: 2026-08-13 13:19 Asia/Seoul (M0.2-05)
reviewer: 자동 승인(모든 검증 결과 PASS)

## 목표

LLM·Embedding·STT 모델과 Gmail·Calendar OAuth Scope의 선택 근거, 평가 원본, 미검증 위험을 확인해 M0.2의 설계·검수 상태를 확정한다.

## 현재 범위

- M0.2-01 LLM 평가 원본·Schema·재평가 Trigger 검수: 완료
- M0.2-02 Embedding 평가: 완료
- M0.2-03 STT 평가: 완료
- M0.2-04 Gmail OAuth: 완료
- M0.2-05 Calendar OAuth: 완료, `AuthorizedSession` 전환 후 사용자 로컬 실제 OAuth·Watch PASS
- OAuth Client Secret·Access Token·Refresh Token은 읽거나 증빙에 기록하지 않는다.

## 실행

- 최신 실행: [`runs/20260813-131903/result.md`](runs/20260813-131903/result.md)
- M0.2-02 최신 실행: [`runs/20260813-114046/result.md`](runs/20260813-114046/result.md)
- M0.2-03 최신 실행: [`runs/20260813-121052/result.md`](runs/20260813-121052/result.md)
- M0.2-04 최신 실행: [`runs/20260813-122007/result.md`](runs/20260813-122007/result.md)
- M0.2-05 이전 승인 실행: [`runs/20260813-122321/result.md`](runs/20260813-122321/result.md)
- M0.2-05 실패 재검수: [`runs/20260813-130230/result.md`](runs/20260813-130230/result.md)
- M0.2-05 최신 승인 실행: [`runs/20260813-131903/result.md`](runs/20260813-131903/result.md)
- 코드·메타데이터 검증 실행: [`runs/20260813-082016/result.md`](runs/20260813-082016/result.md)
- 평가 계획: [`docs/11-llm-evaluation-plan.md`](../../../11-llm-evaluation-plan.md)
- 평가 원본: [`llm-evaluation/README.md`](../../../../llm-evaluation/README.md)

## 승인 조건

모델 평가와 외부 OAuth는 원칙적으로 사람의 판단이 필요한 항목이지만, 이번 실행은 사용자가 제공한 실제 로컬 실행에서 모든 검증 결과가 정확히 `PASS`이고 미실행·경고·보류·차단이 없으므로 자동 승인 규칙을 적용했다. 이전 승인 실행 `20260813-122321`과 실패 실행 `20260813-130230`은 보존하며, 최신 승인 실행은 `20260813-131903`이다. M0.2-05는 `완료`로 전환하고 M0.2 전체 통합 검수로 이동한다.
