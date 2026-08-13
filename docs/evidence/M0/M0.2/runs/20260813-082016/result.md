# M0.2-01 재현성 메타데이터 보완 검수 결과

## 1. 기본 정보

- 마일스톤: M0.2
- 제목: LLM 평가 실행 조건·Hash·비용 메타데이터 보완
- 담당자: Codex
- 검수자: 미정
- 상태: 검수 중
- 실행일: 2026-08-13
- 실행 ID: `20260813-082016`
- 코드 버전: 루트 작업 트리 기준, 평가기 메타데이터 보완 변경
- 입력 데이터 버전: 기존 Pilot·Full Case 1·Full Case 2

## 2. 최신 실행과 승인

- latest_run_id: `20260813-082016`
- latest_run_status: PASS (코드·단위 테스트·dry-run)
- latest_approved_run_id: null
- approved_at: null

## 3. 목표와 완료 기준

- 목표: 과거 LLM 평가의 재현성 누락을 해결하기 위해 새 평가 실행에서 생성 설정, Prompt·Schema·Case Hash, 평가기 버전, Retry 정책과 비용 상태를 기록한다.
- 완료 기준: 실제 Provider 요청과 결과 파일이 동일한 생성 설정을 사용하고, JSONL·CSV에 Secret 없이 실행 메타데이터가 남으며, 기존 Case와 Schema 검증이 계속 통과한다.
- 백로그 범위: `M0.2-01`
- 미완료·보류 백로그: 실제 Provider 재평가와 사람의 모델 선택 승인

## 4. 구현 경로

- 평가 실행기: [`llm-evaluation/run_eval.py`](../../../../../../llm-evaluation/run_eval.py)
- 평가기 테스트: [`llm-evaluation/tests/test_runner.py`](../../../../../../llm-evaluation/tests/test_runner.py)
- 설정 예시: [`llm-evaluation/.env.example`](../../../../../../llm-evaluation/.env.example)
- 평가 실행 안내: [`llm-evaluation/README.md`](../../../../../../llm-evaluation/README.md)
- 평가 계획: [`docs/11-llm-evaluation-plan.md`](../../../../../11-llm-evaluation-plan.md)

## 5. 구현 요약

- `openai`·`openai2` 요청에 `LLM_TEMPERATURE`, `LLM_TOP_P`, `LLM_MAX_TOKENS`, `stream=false`를 명시한다.
- JSONL의 각 결과에 `run_metadata`를 저장한다.
- `run_metadata`에 모델·Provider·Repeat·Timeout·Retry 정책, 생성 설정, 평가기 버전·Commit, Case 파일 Hash, Case·Prompt·정식 Schema·생성 Schema Hash를 기록한다.
- 비용표가 없으면 비용을 추정하지 않고 `pricing.status=unavailable`과 사유만 기록한다.
- CSV 요약에도 Hash·생성 설정·Retry·비용 상태 열을 추가했다.
- API Key·실제 Base URL은 메타데이터에 기록하지 않는다.

## 6. 실행 명령과 결과

```powershell
llm-evaluation/.venv/Scripts/python.exe -m py_compile llm-evaluation/run_eval.py llm-evaluation/tests/test_runner.py
llm-evaluation/.venv/Scripts/python.exe -m unittest discover -s llm-evaluation/tests
cd llm-evaluation
.venv\Scripts\python.exe run_eval.py --dry-run
.venv\Scripts\python.exe run_eval.py --cases cases/full_cases.jsonl --dry-run
.venv\Scripts\python.exe run_eval.py --cases cases/full_cases2.jsonl --dry-run
git diff --check
```

- Python 구문 검사: PASS
- 평가기 단위 테스트: PASS (23개)
- Pilot dry-run: PASS (4개)
- Full Case 1 dry-run: PASS (20개)
- Full Case 2 dry-run: PASS (20개)
- CSV·JSONL 메타데이터 보존: 단위 테스트 PASS
- 실제 Provider 재평가: 실행하지 않음. API Key를 사용하지 않는 코드·Fixture 검증 범위다.

## 7. 검수 항목

| 항목 | 결과 | 근거 경로 |
| --- | --- | --- |
| OpenAI 호환 요청 생성 설정 명시 | PASS | [`test_runner.py`](../../../../../../llm-evaluation/tests/test_runner.py) |
| Prompt·Schema·Case Hash 생성 | PASS | [`run_eval.py`](../../../../../../llm-evaluation/run_eval.py) 및 23개 테스트 |
| JSONL `run_metadata` 보존 | PASS | [`run_eval.py`](../../../../../../llm-evaluation/run_eval.py) |
| CSV 메타데이터 열 보존 | PASS | [`test_runner.py`](../../../../../../llm-evaluation/tests/test_runner.py) |
| Secret·Base URL 비기록 | PASS | 메타데이터 단위 테스트 및 구현 검토 |
| 기존 Case·Schema 검증 | PASS | Pilot·Full Case 1·2 dry-run |
| 과거 실제 평가 재현성 보완 | 부분 PASS | 새 실행기 준비 완료, 실제 Provider 재실행 대기 |

## 8. 문제와 수정 이력

- 발견된 문제: 2026-08-10 실제 결과에는 생성 설정과 Hash가 없었다.
- 원인: 이전 평가기가 Provider 기본 생성 설정을 사용하고 실행 메타데이터를 저장하지 않았다.
- 수정 내용: 생성 설정을 공통 함수로 고정하고, JSONL·CSV에 실행·입력·Schema 메타데이터를 기록하도록 변경했다.
- 재검수 실행 ID: 실제 Provider 재평가 후 새 실행 ID 발급

## 9. 최종 판단

- 승인 여부: 보류(검수 중)
- 검수 의견: 재현성 보완 코드는 구현·검증됐지만 실제 모델 재평가와 모델 선택은 사람의 판단이 필요하다.
- 다음 조치: API Key가 설정된 평가 환경에서 Pilot·Full Case 1·2를 새 실행기로 재실행하고 결과를 추가 검수한다.
