# M2.2-02 실제 LLM 평가 재검수 결과

## 1. 기본 정보

- 마일스톤: M2.2
- 제목: 제안·확정 의미 판정 및 LLM 평가 경계
- 담당자: Codex
- 검수자: 미정
- 상태: 재작업
- 실행일: 2026-08-13
- 실행 ID: 20260813-233641

## 2. 실행 내용

```text
\.venv\Scripts\python.exe run_eval.py --cases cases/full_cases.jsonl --models openai2 --repeat 1
```

- 대상: `full_cases.jsonl` 20건
- 모델 그룹: `openai2`
- 평가기: `metadata-v1`
- 원본 결과: `llm-evaluation/results/run-20260813-233641.jsonl`
- 요약 결과: `llm-evaluation/results/summary-20260813-233641.csv`

## 3. 결과

| 검수 항목 | 결과 | 근거 |
| --- | --- | --- |
| Case·Schema 사전 검증 | PASS | 20 Case와 Schema 로드 완료 |
| 실제 LLM Provider 호출 | FAIL | 20/20 `provider_failed`, `connection` |
| Schema 유효성 | 미실행 | Provider 응답 없음 |
| 의미 유효성 | 미실행 | Provider 응답 없음 |
| 수동 제안·확정 의미 검수 | 미실행 | 실제 모델 응답 부재 |

평가기는 정상 실행됐지만 실제 응답을 한 건도 받지 못해 모델 품질 PASS로 판정할 수 없다. Secret·Token·응답 원문은 이 증빙에 저장하지 않았다.

## 4. 문제와 원인

- 발견된 문제: `openai2` 20건이 모두 연결 오류로 실패했다.
- 원인: 평가 환경에서 `OPENAI_BASE_URL2` 호스트(`mlapi.run`)의 TCP 443 연결 확인이 실패했다.
- 확인 결과: `Test-NetConnection`이 False를 반환했으며, 평가 요약의 오류 유형도 모두 `connection`이었다.
- 재현 명령: 위 실행 명령과 `Test-NetConnection mlapi.run -Port 443`.

## 5. 자동 진행 판정

- 자동 승인: 불가
- 자동 진행: 중단
- latest_approved_run_id: 이전 승인 실행 `20260813-233115` 유지
- 재작업 조건: 평가 Provider Endpoint의 네트워크 연결을 복구한 뒤 동일 Case로 재실행
- 동일 실패 반복 여부: 동일 실행에서 20건 모두 같은 연결 실패가 발생해 추가 재시도하지 않음

## 6. 최종 판단

- 승인 여부: 보류
- 검수 의견: grounding validator와 로컬 평가기 테스트는 통과했지만 실제 LLM 평가가 연결 실패로 완료되지 않았다. M2.2-02는 `재작업`으로 유지한다.
