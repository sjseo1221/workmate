# M0.2-01 실제 Provider 재평가 검수 결과

## 1. 기본 정보

- 마일스톤: M0.2
- 제목: LLM 평가 메타데이터 적용 후 실제 Provider 재평가
- 담당자: Codex
- 검수자: 사용자 승인
- 상태: 완료
- 실행일: 2026-08-13
- 실행 ID: `20260813-093322`
- 코드 버전: `676903172ad56ee3c37896ad2a3e87a55ace8db5`
- 입력 데이터 버전: Pilot·Full Case 1·Full Case 2

## 2. 실행과 승인

- Pilot 실행: `20260813-083705`
- Full Case 1 실행: `20260813-085733`
- Full Case 2 실행: `20260813-091405`
- latest_run_status: PASS
- latest_approved_run_id: `20260813-093322`
- approved_at: 2026-08-13 09:35 Asia/Seoul

## 3. 목표와 완료 기준

- 목표: 재현성 메타데이터를 적용한 평가기로 기본 LLM을 실제 Provider에서 재평가한다.
- 완료 기준: Provider 응답, Schema·의미 점수, 생성 설정·Hash·Retry 메타데이터를 모두 기록하고 Full Case 품질 기준을 통과한다.
- 백로그 범위: `M0.2-01`
- 미완료·보류 백로그: 사람의 기본 모델 선택 승인, Provider 가격표 입력

## 4. 구현·평가 경로

- 평가 실행기: [`llm-evaluation/run_eval.py`](../../../../../../llm-evaluation/run_eval.py)
- 평가기 테스트: [`llm-evaluation/tests/test_runner.py`](../../../../../../llm-evaluation/tests/test_runner.py)
- Pilot 원본: [`run-20260813-083705.jsonl`](../../../../../../llm-evaluation/results/run-20260813-083705.jsonl)
- Full Case 1 원본: [`run-20260813-085733.jsonl`](../../../../../../llm-evaluation/results/run-20260813-085733.jsonl)
- Full Case 2 원본: [`run-20260813-091405.jsonl`](../../../../../../llm-evaluation/results/run-20260813-091405.jsonl)
- Pilot 요약: [`summary-20260813-083705.csv`](../../../../../../llm-evaluation/results/summary-20260813-083705.csv)
- Full Case 1 요약: [`summary-20260813-085733.csv`](../../../../../../llm-evaluation/results/summary-20260813-085733.csv)
- Full Case 2 요약: [`summary-20260813-091405.csv`](../../../../../../llm-evaluation/results/summary-20260813-091405.csv)

## 5. 실행 명령과 결과

```powershell
$env:EVALUATOR_COMMIT='676903172ad56ee3c37896ad2a3e87a55ace8db5'
cd C:\dev\workmate\llm-evaluation
.venv\Scripts\python.exe run_eval.py --repeat 1
.venv\Scripts\python.exe run_eval.py --cases cases/full_cases.jsonl --repeat 1
.venv\Scripts\python.exe run_eval.py --cases cases/full_cases2.jsonl --repeat 1
```

| 세트 | 결과 | 평균 지연 | p95 지연 | 평균 호출 수 |
| --- | --- | ---: | ---: | ---: |
| Pilot 4 Case | 최종 4/4, Schema 4/4, 의미 4/4 | 45.87초 | 47.45초 | 1.00 |
| Full Case 1 20 Case | 최종 20/20, Schema 20/20, 의미 20/20 | 48.44초 | 64.66초 | 1.05 |
| Full Case 2 20 Case | 최종 20/20, Schema 20/20, 의미 20/20 | 57.12초 | 92.85초 | 1.25 |

- Provider 실패: 0건
- 생성 설정: `temperature=0`, `top_p=1`, `max_tokens=1024`, `stream=false`
- 메타데이터: 각 결과에 Prompt·정식/생성 Schema·Case Hash, 평가기 Commit, Retry 정책 기록
- 비용: Provider 가격표 미설정으로 `estimated_cost_usd=null`; 비용 미산정 사유를 기록함

## 6. 검수 항목

| 항목 | 결과 | 근거 경로 |
| --- | --- | --- |
| Pilot 최종 통과율 | PASS (4/4) | `summary-20260813-083705.csv` |
| Full Case 1 최종 통과율 | PASS (20/20) | `summary-20260813-085733.csv` |
| Full Case 2 최종 통과율 | PASS (20/20) | `summary-20260813-091405.csv` |
| Schema 검증 | PASS (44/44) | 세 CSV 요약 |
| 의미 검증 | PASS (44/44) | 세 CSV 요약 |
| 입력 외 Source ID·우선순위 변형 | 0건 | JSONL expectation 결과 |
| 실행 메타데이터 기록 | PASS | JSONL `run_metadata`, CSV 열 |
| 비용 산정 | 승인(미산정) | Provider 가격표 미설정과 `estimated_cost_usd=null` 사유를 승인 |
| 모델 선택 승인 | PASS | 사용자 승인: `openai/gpt-4.1-mini` 기본 모델 확정 |

## 7. 문제와 수정 이력

- 이전 실행 `20260813-082329`·`082349`·`082520`은 Windows 소켓 권한으로 차단됐다.
- 외부 Provider 전송 승인 후 동일 Case를 분리 실행해 완료했다.
- 실제 실행은 Case당 최대 3회까지 수정 요청할 수 있어 Full Case 2 평균 호출 수가 1.25회였다.
- Provider 가격표를 확인할 수 없어 비용은 산정하지 않았다.

## 8. 최종 판단

- 승인 여부: 승인
- 검수 의견: 기본 모델 `openai/gpt-4.1-mini`은 새 메타데이터 조건의 실제 Pilot·Full Case 1·2에서 모두 품질 기준을 통과했다. 사용자가 기본 모델 선택과 비용 미산정 사유를 승인했다.
- 다음 조치: M0.2-02 Embedding 평가 승인으로 이동한다.
