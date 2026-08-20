# M2.2-02 실제 LLM 평가 결과

## 1. 기본 정보

- 마일스톤: M2.2
- 제목: 제안·확정 의미 판정 및 LLM 평가 경계
- 담당자: Codex
- 검수자: 미정
- 상태: 검수 중
- 실행일: 2026-08-13
- 실행 ID: 20260813-234838
- 모델 그룹: `openai2`
- 모델: `openai/gpt-4.1-mini`

## 2. 실행 명령과 원본 결과

```text
.\.venv\Scripts\python.exe run_eval.py --cases cases/full_cases.jsonl --models openai2 --repeat 1
```

- 원본 JSONL: `llm-evaluation/results/run-20260813-234838.jsonl`
- 요약 CSV: `llm-evaluation/results/summary-20260813-234838.csv`
- 입력 Case: `llm-evaluation/cases/full_cases.jsonl` 20건
- 외부 Provider 연결: PASS

## 3. 검증 결과

| 검증 항목 | 결과 |
| --- | --- |
| 실행 완료 | 20/20 PASS |
| JSON Schema 검증 | 20/20 PASS |
| 의미 검증 | 20/20 PASS |
| 최종 점수 1.0 | 20/20 PASS |
| 평균 점수 | 1.00 |
| 재시도 | `weekly-004` 1건, 최종 PASS |
| Provider 오류 | 0건 |

Skill별 Case는 daily 5건, weekly 5건, meeting 5건, search 5건이다. 비용 산정은 Provider 가격 설정이 없어 기록하지 않았다.

## 4. 자동 진행 판정

- 자동 승인: 보류
- 자동 진행: 보류
- 최신 승인 실행: `20260813-233115` 유지
- 보류 사유: 모델 평가와 주간 계획의 제안·확정 의미는 사람의 수동 검수가 필요한 범위다.
- 수동 검수 대상: `weekly-001`~`weekly-005`의 `next_week_plans`가 source_refs 근거와 제안·확정 구분 규칙을 만족하는지 확인
- 재개 조건: 검수자가 의미 검수 PASS를 승인하면 M2.2-02를 완료 처리하고 M2.3-01로 진행

## 5. 최종 판단

- 자동 검증: PASS
- 수동 의미 검수: 대기
- 승인 여부: 보류
- 검수 의견: 실제 Provider 평가와 Schema·의미 검증은 모두 통과했으나 수동 의미 검수 전에는 M2.2-02를 완료로 표시하지 않는다.
