# M0.2 모델·OAuth 확정 증빙

status: 진행
latest_run_id: 20260813-122007
latest_run_status: PASS_WITH_CAVEAT (M0.2-04 Gmail OAuth 검수)
latest_approved_run_id: 20260813-121052 (M0.2-03)
approved_at: 2026-08-13 12:14 Asia/Seoul (M0.2-03)
reviewer: 사용자 승인 (M0.2-03)

## 목표

LLM·Embedding·STT 모델과 Gmail·Calendar OAuth Scope의 선택 근거, 평가 원본, 미검증 위험을 확인해 M0.2의 설계·검수 상태를 확정한다.

## 현재 범위

- M0.2-01 LLM 평가 원본·Schema·재평가 Trigger 검수: 완료
- M0.2-02 Embedding 평가: 완료
- M0.2-03 STT 평가: 완료
- M0.2-04 Gmail OAuth: 검수 중, 기존 성공 이력 사용자 확인 필요
- M0.2-05 Calendar OAuth: 대기
- OAuth Client Secret·Access Token·Refresh Token은 읽거나 증빙에 기록하지 않는다.

## 실행

- 최신 실행: [`runs/20260813-114046/result.md`](runs/20260813-114046/result.md)
- M0.2-02 최신 실행: [`runs/20260813-114046/result.md`](runs/20260813-114046/result.md)
- M0.2-03 최신 실행: [`runs/20260813-121052/result.md`](runs/20260813-121052/result.md)
- M0.2-04 최신 실행: [`runs/20260813-122007/result.md`](runs/20260813-122007/result.md)
- 코드·메타데이터 검증 실행: [`runs/20260813-082016/result.md`](runs/20260813-082016/result.md)
- 평가 계획: [`docs/11-llm-evaluation-plan.md`](../../../11-llm-evaluation-plan.md)
- 평가 원본: [`llm-evaluation/README.md`](../../../../llm-evaluation/README.md)

## 승인 조건

모델 평가와 외부 OAuth는 사람의 판단이 필요한 항목이므로 자동 승인하지 않는다. M0.2-01~03은 각각 사용자 승인을 완료했다. M0.2-04는 기존 Gmail API·Watch 성공 이력이 있으나 현재 환경의 외부 재실행이 네트워크 차단으로 보류되어 사용자 확인 전까지 `검수 중`으로 유지한다. M0.2 전체 상태는 `진행`이다.
