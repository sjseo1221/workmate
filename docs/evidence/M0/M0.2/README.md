# M0.2 모델·OAuth 확정 증빙

status: 완료
latest_run_id: 20260813-135158
latest_run_status: PASS (M0.2 통합 재검수)
latest_approved_run_id: 20260813-135158
approved_at: 2026-08-13 13:52 Asia/Seoul
reviewer: 자동 승인(검증 명령)

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

- 최신 실행: [`runs/20260813-134129/result.md`](runs/20260813-134129/result.md)
- M0.2-02 최신 실행: [`runs/20260813-114046/result.md`](runs/20260813-114046/result.md)
- M0.2-02 재검수 승인 실행: [`runs/20260813-134129/result.md`](runs/20260813-134129/result.md)
- M0.2-03 최신 실행: [`runs/20260813-121052/result.md`](runs/20260813-121052/result.md)
- M0.2-03 재검수 승인 실행: [`runs/20260813-134542/result.md`](runs/20260813-134542/result.md)
- M0.2-04 최신 실행: [`runs/20260813-122007/result.md`](runs/20260813-122007/result.md)
- M0.2-04 재검수 승인 실행: [`runs/20260813-134915/result.md`](runs/20260813-134915/result.md)
- M0.2 통합 재검수 승인 실행: [`runs/20260813-135158/result.md`](runs/20260813-135158/result.md)
- M0.2-05 이전 승인 실행: [`runs/20260813-122321/result.md`](runs/20260813-122321/result.md)
- M0.2-05 실패 재검수: [`runs/20260813-130230/result.md`](runs/20260813-130230/result.md)
- M0.2-05 최신 승인 실행: [`runs/20260813-131903/result.md`](runs/20260813-131903/result.md)
- M0.2 통합 최신 실행: [`runs/20260813-133446/result.md`](runs/20260813-133446/result.md)
- M0.2 통합 차단 해소 계획: [`remediation-plan.md`](remediation-plan.md)
- 코드·메타데이터 검증 실행: [`runs/20260813-082016/result.md`](runs/20260813-082016/result.md)
- 평가 계획: [`docs/11-llm-evaluation-plan.md`](../../../11-llm-evaluation-plan.md)
- 평가 원본: [`llm-evaluation/README.md`](../../../../llm-evaluation/README.md)

## 승인 조건

M0.2 통합 재검수 `20260813-135158`에서 M0.2-01~05의 최신 승인 실행이 모두 정확히 `PASS`임을 확인했다. 이전 `PASS_WITH_CAVEAT`, `FAIL`, `보류`는 새 개별 재검수로 해소됐고, 이전 실행은 모두 보존된다. M0.2는 `완료`로 전환한다.
