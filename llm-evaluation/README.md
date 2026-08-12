# Workmate LLM Evaluation

기본 LLM은 OpenAI 호환 API의 `openai/gpt-4.1-mini`로 확정했다. 평가기는 `.env`의 `OPENAI_BASE_URL2`, `OPENAI_API_KEY2`, `OPENAI_MODEL2`로 이 모델을 평가한다. 기존 모델 Adapter는 보류 상태로 코드에만 유지하며, 현재 API 할당량이 소진되면 같은 Case와 Schema로 후보를 다시 평가한다.

평가 계획, 결과와 수정 이유는 [LLM 모델 평가 계획과 개선 이력](../docs/11-llm-evaluation-plan.md)에 날짜순으로 기록한다.

## 1. 준비

Python 3.11 이상이 필요하다. API Key는 채팅이나 Git에 공유하지 않는다.

```powershell
cd C:\dev\workmate\llm-evaluation
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

`.env`를 직접 열어 `OPENAI_BASE_URL2`, `OPENAI_API_KEY2`, `OPENAI_MODEL2`를 입력한다. Base URL에는 `/v1`까지 포함하고 실행기는 `/chat/completions`를 추가한다. 이 API는 OpenAI 호환 `response_format=json_schema`를 지원해야 한다. Timeout·429·502·503·504는 한 번 재시도한다. 정상 응답이 Schema를 위반하면 한 번, Schema는 맞지만 업무 의미 검증에 실패하면 한 번만 각각 수정 요청한다.

## 2. Case와 Schema만 검사

API나 Ollama를 호출하지 않는다. JSON Schema와 함께 Case의 사전 계산 우선순위 값 및 점수 합계도 검증한다.

```powershell
python run_eval.py --dry-run
python -m unittest discover -s tests
```

## 3. Pilot 평가

먼저 4개 샘플을 한 번 실행한다. 기본 모델이 `openai2` 하나이므로 `--models`를 생략할 수 있다.

```powershell
python run_eval.py --repeat 1
```

명시적으로 선택하려면 다음처럼 실행한다.

```powershell
python run_eval.py --models openai2 --repeat 1
```

정상 동작 후 제공된 20개 Case를 두 번 실행한다.

```powershell
python run_eval.py --cases cases/full_cases.jsonl --models openai2 --repeat 2
```

기존 세트와 겹치지 않는 두 번째 20개 Case는 다음처럼 실행한다.

```powershell
python run_eval.py --cases cases/full_cases2.jsonl --models openai2 --repeat 1
```

결과는 `results/run-*.jsonl`과 Excel에서 바로 열 수 있는 `results/summary-*.csv`로 생성된다. JSONL에는 시도별 토큰·오류, Schema/의미 검증 결과와 메모리 측정값이 저장된다. Provider 실패는 `provider_error`로 분리하며 Schema와 의미 점수를 비워 모델 품질 집계에서 제외한다. `final_score`는 정상 응답이 Schema와 의미 검증을 모두 통과한 경우에만 기대값 점수를 사용하고, 하나라도 실패하면 0점이다.

실제 평가 결과에는 `run_metadata`로 모델·Provider·Repeat·Timeout·Retry 정책, Temperature·Top P·최대 출력 Token, Case 파일·Case·Prompt·정식/생성 Schema Hash, 평가기 버전·Commit과 비용 산정 상태를 기록한다. `EVALUATOR_COMMIT`은 실행한 평가기 Commit을 입력하고, `LLM_PRICING_SOURCE`는 가격표 출처를 입력한다. API Key와 실제 Base URL은 결과에 저장하지 않는다.

## 4. Case 형식

한 줄에 JSON 객체 하나를 쓰는 JSONL 형식이다.

```json
{
  "case_id": "meeting-001",
  "skill_id": "analyze_meeting",
  "schema_def": "MeetingAnalysisResult",
  "instruction": "회의 원문에서 Action Item 후보를 추출하라.",
  "input": {},
  "expectations": {
    "must_include": ["반드시 포함할 문구"],
    "forbidden": ["만들면 안 되는 문구"],
    "expected_source_ids": ["meeting-1"],
    "expected_next_week_plan_source_ids": ["task-2"],
    "answer_must_include": ["답변 자체에 포함할 문구"],
    "source_quote_must_include": ["출처 인용문에 포함할 문구"],
    "evidence_texts": ["원문과 정확히 같아야 하는 근거 문장"],
    "expected_values": {"insufficient_evidence": false}
  }
}
```

`schema_def`는 `docs/schemas/workmate-skill-schemas.schema.json`의 `$defs` 이름을 사용한다. 현재 샘플은 네 주요 LLM 기능을 한 건씩 포함하며, 최종 평가는 기능별 20개 Case로 확장한다.

브리핑의 우선순위 숫자는 LLM이 계산하지 않는다. `input.precomputed_priorities`에 Priority Service가 계산한 rank, title, score, score_breakdown과 reasons를 넣고, LLM이 값을 변경하지 않고 설명하는지를 평가한다. 출처는 최상위 `source_refs`뿐 아니라 Task ID, 회의 ID, transcript와 근거 Chunk ID 같은 전용 필드에서도 수집하고 입력에 없는 ID가 생성됐는지 별도로 검증한다.
