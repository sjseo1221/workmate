# M0.2 모델·OAuth 확정 증빙

status: 재작업
latest_run_id: 20260813-133446
latest_run_status: BLOCKED (M0.2 통합 검수에서 PASS_WITH_CAVEAT·FAIL·보류 발견)
latest_approved_run_id: 20260813-131903 (M0.2-05 개별 승인; M0.2 통합 미승인)
approved_at: 2026-08-13 13:19 Asia/Seoul (M0.2-05)
reviewer: 자동 검수 중단(통합 승인 불가)

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
- M0.2 통합 최신 실행: [`runs/20260813-133446/result.md`](runs/20260813-133446/result.md)
- 코드·메타데이터 검증 실행: [`runs/20260813-082016/result.md`](runs/20260813-082016/result.md)
- 평가 계획: [`docs/11-llm-evaluation-plan.md`](../../../11-llm-evaluation-plan.md)
- 평가 원본: [`llm-evaluation/README.md`](../../../../llm-evaluation/README.md)

## 승인 조건

M0.2-05 개별 실행은 모든 결과가 정확히 `PASS`여서 자동 승인됐다. 그러나 M0.2 통합 검수 `20260813-133446`에서 M0.2-02·03·04의 `PASS_WITH_CAVEAT`, `FAIL`, `보류`가 확인되어 통합 자동 승인 규칙에 따라 즉시 중단했다. M0.2 상위 상태는 `재작업`이며, M0.2-02·03·04의 차단 항목을 해소하기 전에는 전체 완료로 표시하지 않는다.
