# M0.2-01 검수 결과

## 1. 기본 정보

- 마일스톤: M0.2
- 제목: LLM 평가 승인
- 담당자: Codex
- 검수자: 미정
- 상태: 검수 중
- 실행일: 2026-08-13
- 실행 ID: `20260813-075806`
- 코드 버전: 루트 문서 기준선 `bc0f05d`, 평가 원본 변경 없음
- 입력 데이터 버전: `sample_cases.jsonl`, `full_cases.jsonl`, `full_cases2.jsonl`, Workmate Skill Schema

## 2. 최신 실행과 승인

- latest_run_id: `20260813-075806`
- latest_run_status: PASS (dry-run·단위 테스트)
- latest_approved_run_id: null
- approved_at: null

## 3. 목표와 완료 기준

- 목표: 기본 LLM `openai/gpt-4.1-mini`의 기존 평가 원본과 평가기 검증 상태를 확인하고, 할당량 소진·계약 종료 시 동일 조건 재평가 Trigger를 기록한다.
- 완료 기준: Pilot·Full Case 1·Full Case 2의 결과와 Schema/의미 기준을 확인하고, 운영 모델·제약·미검증 위험을 승인 가능한 형태로 정리한다.
- 백로그 범위: `M0.2-01`
- 미완료·보류 백로그: 사람의 모델 품질 승인, 과거 실행의 생성 설정·Prompt/Schema Hash 보완, Provider 비용 확인

## 4. 구현·평가 경로

- 평가 실행기: [`llm-evaluation/run_eval.py`](../../../../../../llm-evaluation/run_eval.py)
- 평가 계획·이력: [`docs/11-llm-evaluation-plan.md`](../../../../../11-llm-evaluation-plan.md)
- 평가 실행 안내: [`llm-evaluation/README.md`](../../../../../../llm-evaluation/README.md)
- 승인 Schema: [`docs/schemas/workmate-skill-schemas.schema.json`](../../../../../schemas/workmate-skill-schemas.schema.json)
- Pilot Case: [`llm-evaluation/cases/sample_cases.jsonl`](../../../../../../llm-evaluation/cases/sample_cases.jsonl)
- Full Case 1: [`llm-evaluation/cases/full_cases.jsonl`](../../../../../../llm-evaluation/cases/full_cases.jsonl)
- Full Case 2: [`llm-evaluation/cases/full_cases2.jsonl`](../../../../../../llm-evaluation/cases/full_cases2.jsonl)

## 5. 검수에서 확인한 내용

- 운영 기본 모델은 OpenAI 호환 API의 `openai/gpt-4.1-mini` 하나로 고정되어 있으며 런타임 다중 Provider 전환은 범위에서 제외되어 있다.
- 평가기는 `schema_valid`와 `semantic_valid`를 분리하고 둘 다 통과한 경우에만 `final_score=1`로 집계한다.
- 우선순위·날짜·권한 값은 코드에서 사전 계산하며, 모델은 순위·점수·근거 ID를 변경하지 않는 조건으로 평가된다.
- Provider 오류와 모델 품질 오류를 분리하고 제한된 Retry·Schema 수정·의미 수정 결과를 원본 JSONL에 보존한다.
- 할당량 소진 또는 계약 종료 시 같은 Case·Schema·고정 조건으로 보류 후보를 재평가하고 수동 선정한다. 운영 런타임에서 다중 Provider 자동 전환은 추가하지 않는다.

## 6. 실행 명령과 결과

```powershell
cd C:\dev\workmate\llm-evaluation
.venv\Scripts\python.exe run_eval.py --dry-run
.venv\Scripts\python.exe run_eval.py --cases cases/full_cases.jsonl --dry-run
.venv\Scripts\python.exe run_eval.py --cases cases/full_cases2.jsonl --dry-run
.venv\Scripts\python.exe -m unittest discover -s tests
```

- Pilot Schema·입력 dry-run: PASS (4개)
- Full Case 1 Schema·입력 dry-run: PASS (20개)
- Full Case 2 Schema·입력 dry-run: PASS (20개)
- 평가기 단위 테스트: PASS (21개)
- 외부 Provider 재호출: 실행하지 않음. 기존 평가 원본을 검수 대상으로 사용했으며 API Key는 증빙에 기록하지 않는다.

## 7. 기존 평가 원본 요약

| 실행 | 결과 | 지표 | 근거 |
| --- | --- | --- | --- |
| Pilot, 2026-08-10 | 최종 4/4 | OpenAI 호환 단일 모델 | [`summary-20260810-103840.csv`](../../../../../../llm-evaluation/results/summary-20260810-103840.csv) |
| Full Case 1, 2026-08-10 | 최종 20/20, 최초 19/20 | 평균 4.36초, p95 7.35초, 21회 호출 | [`summary-20260810-111505.csv`](../../../../../../llm-evaluation/results/summary-20260810-111505.csv) |
| Full Case 2, 2026-08-10 | 최종 20/20, 최초 15/20 | 평균 6.86초, p95 17.40초, 26회 호출 | [`summary-20260810-113712.csv`](../../../../../../llm-evaluation/results/summary-20260810-113712.csv) |

## 8. 검수 항목

| 항목 | 결과 | 근거 경로 |
| --- | --- | --- |
| 기본 모델·Skill별 Case 구성 | PASS | [`docs/11-llm-evaluation-plan.md`](../../../../../docs/11-llm-evaluation-plan.md), Case 링크 |
| 정식 Schema·입력 규칙 dry-run | PASS | 실행 ID `20260813-075806` |
| 평가기 단위 테스트 | PASS | 실행 ID `20260813-075806`, 21개 |
| Full Case 1 최종 품질 기준 | PASS (기존 원본) | `summary-20260810-111505.csv` |
| Full Case 2 최종 품질 기준 | PASS (기존 원본) | `summary-20260810-113712.csv` |
| 생성 설정·Prompt/Schema Hash 기록 | 보완 필요 | 2026-08-10 이력에 미기록으로 명시됨 |
| Provider 비용 산정 | 보류 | 가격 정보 미확인으로 `null` |
| 사람의 모델 선택 승인 | 미승인 | 사용자 검토 필요 |

## 9. 문제와 수정 이력

- 발견된 문제: 과거 실제 평가 결과는 품질 기준을 충족하지만 Temperature·최대 출력 Token·Prompt/Schema Version 또는 Hash가 실행 메타데이터에 없고 Provider 비용은 `null`이다.
- 원인: 2026-08-10 실행기가 해당 메타데이터를 기록하지 않았다.
- 수정 내용: 이번 실행에서는 외부 API를 재호출하지 않고, 누락을 재평가 Trigger 조건으로 명시했다. 다음 실제 재평가 전에 실행 메타데이터 기록을 보완해야 한다.
- 재검수 실행 ID: 사용자 승인 후 동일 조건 재평가 시 새 실행 ID를 발급한다.

## 10. 최종 판단

- 승인 여부: 보류(검수 중)
- 검수 의견: 기존 LLM 평가 원본과 현재 평가기 검증은 확인됐고 기본 모델 선택 근거도 문서화돼 있다. 다만 모델 평가는 사람의 판단 대상이며, 과거 실행의 생성 설정·Hash·비용 누락이 남아 있어 자동 승인하지 않는다.
- 다음 조치: 사용자가 `openai/gpt-4.1-mini` 선택과 재평가 Trigger·메타데이터 보완 조건을 확인한 뒤 M0.2-01을 승인하거나 재평가를 요청한다.
