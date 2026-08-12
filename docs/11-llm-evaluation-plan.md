# Workmate LLM 모델 평가 계획 및 개선 이력

[← 기술 상세 설계](07-technical-specification.md) · [목차](README.md)

## 1. 목적

Workmate의 브리핑, 주간 보고, 회의 분석과 회의 검색 답변에 사용할 LLM을 동일한 Case와 JSON Schema로 평가한다. 모델의 형식 준수와 업무 의미 정확도를 분리해서 측정하고, 선정 이후에도 Prompt·Case·평가기 변경 이유와 재평가 결과를 보존한다.

최종 산출물은 다음과 같다.

- 운영 LLM Provider와 모델 ID
- Skill별 Prompt와 구조화 출력 규칙
- Retry·Schema 수정·의미 수정 요청 규칙
- 품질·지연·Token·비용 기준선
- 모델 교체 조건과 재평가 기록

## 2. 평가 대상

| 구분 | 모델 | 실행 방식 | 상태 |
| --- | --- | --- | --- |
| 기본 LLM | `openai/gpt-4.1-mini` | OpenAI 호환 API | 확정 |
| 보류 후보 | `gpt-5.4-mini-2026-03-17` | API | 재평가 대기 |
| 보류 후보 | `qwen2.5:3b` | 로컬 Ollama | 재평가 대기 |
| 보류 후보 | `meta/llama-3.3-70b-instruct` | NVIDIA API | 재평가 대기 |
| 보류 후보 | `google/gemma-4-31b-it` | NVIDIA API | 재평가 대기 |

현재 API 할당량이 소진되거나 계약이 종료될 때 보류 후보를 같은 조건으로 다시 평가한다. 운영 Workmate에는 단일 Provider Client만 구현하며 런타임 다중 Provider 전환은 만들지 않는다.

## 3. 평가 기능과 데이터

| Skill | 핵심 평가 항목 |
| --- | --- |
| `daily_briefing` | 사전 계산 Top 3 보존, 메일·일정 신호 요약, 출처 ID |
| `weekly_report` | 완료·진행·지연 분류, 다음 주 계획 근거, 출처 ID |
| `analyze_meeting` | 통합 요약, 명시적 Action Item, 근거 원문과 구간 |
| `search_meetings` | 제공 Context 안의 답변, 회의·Chunk 출처, 근거 부족 처리 |

Pilot은 Skill별 1건씩 4개 Case를 사용한다. 본 평가는 Skill별 5건씩 구성한 `full_cases.jsonl` 20개와 내용이 겹치지 않는 `full_cases2.jsonl` 20개를 사용한다. 정답과 기대값은 사람이 원문과 업무 규칙을 확인해 확정한다.

### 3.1 Case 세트 구성

| 세트 | 파일 | 구성 | 용도 |
| --- | --- | --- | --- |
| Pilot | [sample_cases.jsonl](../llm-evaluation/cases/sample_cases.jsonl) | Skill별 1건, 총 4건 | Provider 연결과 기본 출력 계약 확인 |
| Full Case 1 | [full_cases.jsonl](../llm-evaluation/cases/full_cases.jsonl) | Skill별 5건, 총 20건 | 상태·근거·출처와 주요 경계조건 평가 |
| Full Case 2 | [full_cases2.jsonl](../llm-evaluation/cases/full_cases2.jsonl) | Skill별 5건, 총 20건 | 다른 업무 내용에서도 평가 결과가 일반화되는지 확인 |

Pilot과 Full Case 1은 `daily-001`, `weekly-001`, `meeting-001`, `search-001` ID를 함께 사용하지만 입력 Version이 항상 같다고 가정하지 않는다. 두 세트의 결과는 실행 결과 파일과 실행 시각으로 구분한다.

### 3.2 Pilot Case 설명

| Case ID | 테스트 목적 | 핵심 입력 상황 | 주요 검증 항목 |
| --- | --- | --- | --- |
| `daily-001` | 브리핑과 Top 3 기본 계약 | 진행·지연·예정 Task와 일정·메일 신호 혼합 | 사전 계산 순위·점수 보존, Task 출처, 금지 내용 |
| `weekly-001` | 주간 상태 분류 | 완료·진행·차단·다음 주 Task와 회의 결정 혼합 | 업무 분류, 다음 주 계획, Task·Meeting 출처 |
| `meeting-001` | 명시적 Action Item 추출 | 담당자의 원인 분석 약속과 후속 공유 요청 | Action Item, Chunk ID, 원문 `evidence_text` 일치 |
| `search-001` | 근거 기반 회의 검색 답변 | QA 빌드 날짜가 명시된 단일 회의 Context | 날짜·회의명 답변, Meeting·Chunk 출처, 인용문 |

### 3.3 Full Case 1 설명

| Case ID | 테스트 목적 | 주요 검증 항목 |
| --- | --- | --- |
| `daily-001` | 세 Task와 Calendar가 있는 일반 브리핑 | Top 3 순서·점수·출처 보존 |
| `daily-002` | Task가 두 건뿐인 긴급 브리핑 | 존재하는 Task만 반환하고 완료 상태를 만들지 않음 |
| `daily-003` | 장애 대응 Task와 일정의 결합 | 세 Task 순서와 장애 미해결 상태 보존 |
| `daily-004` | 차단·진행·일반 Task 혼합 | 차단 Task를 포함한 사전 계산 Top 3 보존 |
| `daily-005` | Task가 한 건뿐인 브리핑 | Top 3를 억지로 채우지 않고 한 건만 반환 |
| `weekly-001` | 모든 상태와 회의 계획이 있는 주간 보고 | 완료·진행·지연·이슈·다음 주 계획 및 출처 |
| `weekly-002` | 완료·진행·차단·차주 Task 혼합 | 차단 업무와 다음 시즌 계획 분류 |
| `weekly-003` | 완료 업무만 있는 주간 보고 | 근거 없는 장애나 다음 주 계획 생성 방지 |
| `weekly-004` | 진행·차단·차주 업무 혼합 | 결제 지연 이슈와 다음 주 기획안 누락 방지 |
| `weekly-005` | 회의에서 다음 주 계획이 보강되는 보고 | Task와 Meeting 출처를 함께 유지 |
| `meeting-001` | 담당자가 명시한 단일 Action Item | 근거 Chunk와 원문 일치 |
| `meeting-002` | 마감 표현이 포함된 재계산 약속 | 명시적 Action Item만 추출하고 출시 확정 금지 |
| `meeting-003` | 논의만 있고 담당 약속이 없는 회의 | 근거 없는 Action Item 생성 방지 |
| `meeting-004` | 서로 다른 담당자의 Action Item 두 건 | 두 근거 Chunk와 원문을 각각 보존 |
| `meeting-005` | 상대 날짜가 포함된 프로파일링 약속 | 원문 근거와 Transcript Version 보존, 임의 날짜 금지 |
| `search-001` | QA 빌드 날짜 검색 | 날짜·회의명·출처·인용문 검증 |
| `search-002` | 정기 점검 날짜와 시간 검색 | 답변 본문과 출처의 책임 분리, 잘못된 시간 금지 |
| `search-003` | 결제 오류 원인 검색 | 원인과 회의 출처 반환, 다른 장애 원인 생성 금지 |
| `search-004` | 이벤트 보상 지급일 검색 | 날짜와 회의 근거 보존 |
| `search-005` | 신규 서버 담당자 검색 | 담당자와 회의 출처 반환, 다른 담당자 생성 금지 |

### 3.4 Full Case 2 설명

| Case ID | 테스트 목적 | 주요 검증 항목 |
| --- | --- | --- |
| `daily-006` | 보안·CDN·번역 Task 혼합 | 차단·진행·예정 Task의 Top 3 보존 |
| `daily-007` | 메일 신호와 두 Task가 있는 브리핑 | 인증서 위험 반영, 존재하지 않는 세 번째 Task 생성 금지 |
| `daily-008` | 단일 플랫폼 Task 브리핑 | 한 건만 반환하고 완료로 단정하지 않음 |
| `daily-009` | 보상 일정과 세 Task의 연계 | Calendar 신호를 참고하되 Task 순위 보존 |
| `daily-010` | 개인정보·FAQ·온콜 업무 혼합 | 차단 업무 우선 반영과 완료 환각 방지 |
| `weekly-006` | 모든 상태와 회의 계획이 있는 독립 보고 | 차단 이슈와 프리로딩 차주 계획·출처 |
| `weekly-007` | 진행·차단·차주 Task 보고 | 가격 동기화 이슈를 해결로 잘못 표시하지 않음 |
| `weekly-008` | 완료 업무만 있는 독립 보고 | 근거 없는 다음 주 확정 계획 생성 방지 |
| `weekly-009` | 완료·진행 Task와 회의 계획 결합 | 금칙어 검토 계획과 Meeting 출처 유지 |
| `weekly-010` | 차단 업무와 두 차주 업무·회의 결합 | 미해결 결제 이슈와 할로윈 계획 분류 |
| `meeting-006` | 인프라 점검 약속과 공유 요청 | 명시적 점검 Action Item과 원문 근거 |
| `meeting-007` | 접근성 관련 Action Item 두 건 | 두 Action Item과 각각의 근거 Chunk 보존 |
| `meeting-008` | 관찰 필요성만 제시된 회의 | 담당자 없는 Action Item 생성 방지 |
| `meeting-009` | 마감일이 명시된 절차 문서 약속 | 담당 약속과 근거 원문 보존 |
| `meeting-010` | 라이선스 확인과 법무 전달 연속 업무 | 두 근거 문장·Chunk 보존, 승인 완료 환각 방지 |
| `search-006` | 로그 중단 날짜·시간·기간 검색 | 세 시간 정보와 정확한 인용문 반환 |
| `search-007` | 트레일러 검수 담당자 검색 | 담당자와 Meeting·Chunk 출처 검증 |
| `search-008` | 저사양 기기 설정 결정 검색 | 설정 변경 수준을 과장하지 않음 |
| `search-009` | 단계적 배포 비율 검색 | 10% 수치와 출처 유지, 50% 환각 금지 |
| `search-010` | macOS 베타 공개일 검색 | 플랫폼·날짜·회의 출처 반환 |

## 4. 고정 조건

- 동일한 입력, System Prompt와 Workmate JSON Schema 사용
- 날짜·권한·우선순위 점수는 코드에서 사전 계산
- 모델은 사전 계산값을 변경하지 않고 설명만 작성
- 입력에 없는 Task·Meeting·Transcript·Chunk ID 생성 금지
- `evidence_text`는 회의 원문과 정확히 일치
- Temperature와 Token 한도를 고정하고 기록
- Case당 동일한 Repeat 횟수 적용
- 모델 ID, Provider와 실행 시각 기록

Provider가 Strict JSON Schema 전체를 지원하지 않으면 생성용 호환 Schema를 사용할 수 있다. 최종 결과는 항상 정식 Workmate Schema로 다시 검증한다.

## 5. 평가 단계

### 5.1 사전 검증

API 호출 전에 Case JSONL, Schema 참조, 사전 계산 우선순위의 점수 범위·합계와 Case ID 중복을 검사한다.

```powershell
cd C:\dev\workmate\llm-evaluation
python run_eval.py --dry-run
python -m unittest discover -s tests
```

### 5.2 Pilot 평가

Sample 4개를 한 번 실행해 Provider 연결, 구조화 출력과 Skill별 기본 응답을 확인한다.

```powershell
python run_eval.py --models openai2 --repeat 1
```

### 5.3 Full Case 평가

Pilot 통과 후 두 개의 독립적인 20개 세트를 실행한다.

```powershell
python run_eval.py --cases cases/full_cases.jsonl --models openai2 --repeat 2
python run_eval.py --cases cases/full_cases2.jsonl --models openai2 --repeat 1
```

### 5.4 실패 분석과 재평가

실패를 `모델`, `Prompt`, `Case`, `평가기`, `Provider`로 분류한다. 평가 기준을 낮춰 실패를 통과시키지 않는다. 수정 후에는 같은 Case로 다시 실행하고 변경 전후 결과를 모두 보존한다.

## 6. 지표와 통과 기준

| 구분 | 지표 | 기준 |
| --- | --- | --- |
| API | `execution_status` | Provider 실패와 모델 품질 실패 분리 |
| 형식 | `schema_valid` | 100% 목표 |
| 의미 | `semantic_valid` | Full Case별 90% 이상 |
| 최종 | `final_score` | Schema와 의미를 모두 통과한 경우만 1 |
| 최초 응답 | 수정 요청 전 통과율 | 최종 통과율과 별도 기록 |
| 수정 요청 | Schema·의미 수정 횟수 | 유형별 횟수 기록 |
| 호출 효율 | Case당 평균 API 호출 수 | 후보 비교값 기록 |
| 출처 | 입력에 없는 Source ID | 0건 |
| 근거 | `evidence_text` 원문 일치 | 100% |
| 우선순위 | 사전 계산값 변형 | 0건 |
| 성능 | 지연 p50·p95, Token, 비용 | 후보 비교값 기록 |

Provider Timeout·429·502·503·504는 한 번 재시도한다. 정상 응답의 Schema 오류와 의미 오류는 각각 한 번만 수정 요청하며, 최초 응답과 모든 수정 시도를 결과에 기록한다.

## 7. 모델 선정과 교체 규칙

1. 출처 환각이나 사전 계산값 변형이 반복되는 후보 제외
2. 두 Full Case 중 하나라도 최종 통과율 90% 미만이면 원인 분석 후 재평가
3. 품질 기준을 통과한 후보의 지연, 비용과 운영 제약 비교
4. 품질 차이가 작으면 비용과 Provider 안정성이 좋은 모델 선택
5. 모델을 교체하면 Pilot과 두 Full Case를 모두 다시 실행

## 8. 결과 파일

실행 결과는 `llm-evaluation/results/run-*.jsonl`과 `llm-evaluation/results/summary-*.csv`에 저장한다. 상세 시도, 오류, Token, Schema·의미 검증 결과와 메모리 사용량은 JSONL에 보존한다.

2026-08-10까지의 `openai2` 결과에는 Temperature와 최대 출력 Token을 명시적으로 전달하지 않아 Provider 기본값이 사용됐다. 실행 결과에도 Case 파일 경로, Repeat 번호, Prompt·Schema Version 또는 Hash가 저장되지 않았고 Provider 가격을 알 수 없어 비용은 `null`이다. 다음 재평가 전에는 이 값을 실행 메타데이터로 기록해 결과 재현성을 보완한다. 실제 API Base URL과 Key는 결과나 문서에 기록하지 않는다.

## 9. 평가 및 수정 이력

모델 결과, 평가기, Prompt와 Case 수정 이유를 날짜순으로 기록한다. 과거 결과 파일은 수정하지 않으며, 변경 전후 결과가 직접 비교 가능한 경우와 평가 기준이 달라진 경우를 구분한다.

### 기록 원칙

- `모델`: 모델 또는 Provider 변경
- `Prompt`: 모델 지시문 변경
- `Case`: 입력 데이터나 기대값 수정
- `평가기`: Schema·의미 검증, Retry와 결과 기록 변경
- `Provider`: API 호환성, Timeout과 오류 처리 변경
- 평가기나 Case가 변경된 실행은 모델 자체 성능 향상으로 단정하지 않는다.

### 실행 결과 요약

| 실행 시각 | 대상 | 결과 | 주요 의미 |
| --- | --- | --- | --- |
| 2026-08-08 16:32 | OpenAI·Llama·Qwen, Sample 4개 | 실행 계약 오류 | 생성용 Schema가 Provider 제약과 충돌 |
| 2026-08-08 20:09 | OpenAI·Llama·Qwen, Sample 4개 | Schema 통과 7/12 | 생성용 Schema 변환 후 후속 검증 문제 발견 |
| 2026-08-08 21:21 | OpenAI·Llama·Qwen, Sample 4개 | 최종 3/12 | 의미 검증을 포함한 첫 비교 결과 |
| 2026-08-08 22:27 | OpenAI·Qwen·NVIDIA Qwen, Sample 4개 | NVIDIA Qwen 실행 불가 | 선택 모델이 NVIDIA Catalog에 없음 |
| 2026-08-08 23:45 | OpenAI·Qwen·NVIDIA Llama, Sample 4개 | 최종 3/12 | NVIDIA Llama Timeout과 형식 오류 확인 |
| 2026-08-09 00:35 | NVIDIA Llama, Sample 4개 | 최종 1/4 | Retry 후에도 속도·형식 불안정 |
| 2026-08-09 16:52 | NVIDIA Gemma, Sample 4개 | 최종 3/4, Provider 실패 1건 | Gemma Adapter 첫 평가 |
| 2026-08-09 17:22 | 4개 모델, Sample 4개 | OpenAI 4/4, Gemma 3/4, Llama 1/4, Qwen 0/4 | 동일 실행기의 최종 후보 비교 |
| 2026-08-10 10:26 | OpenAI 호환 API 모델, Sample 4개 | 최종 3/4 | 주간 보고 의미 분류 누락 발견 |
| 2026-08-10 10:38 | OpenAI 호환 API 모델, Sample 4개 | 최종 4/4 | 주간 규칙과 의미 오류 1회 재요청 적용 |
| 2026-08-10 10:42 | OpenAI 호환 API 모델, Full 20개 | 최종 16/20 | Case·Schema 충돌 3건과 과도한 검색 기대값 1건 발견 |
| 2026-08-10 11:15 | OpenAI 호환 API 모델, 수정된 Full Case 1 20개 | 최초 19/20, 최종 20/20 | 평가 데이터 수정 후 전체 통과 |
| 2026-08-10 11:37 | OpenAI 호환 API 모델, 독립 Full Case 2 20개 | 최초 15/20, 최종 20/20 | 일반화 세트 통과, 수정 요청 6회 발생 |

### 2026-08-08

#### 초기 평가 실행과 생성용 Schema 호환 처리

- 근거 결과: [run-20260808-163205.jsonl](../llm-evaluation/results/run-20260808-163205.jsonl)
- 문제:
  - OpenAI Structured Output이 `uniqueItems` 등 일부 JSON Schema Keyword를 거절했다.
  - 선택 필드가 `required`에 없어서 Strict Schema 생성이 거절됐다.
  - Ollama Grammar 초기화도 같은 복잡한 Schema에서 실패했다.
- 수정 이유: 정식 Workmate Schema를 약화하지 않으면서 Provider가 생성 단계에서 처리할 공통 Schema가 필요했다.
- 반영:
  - Provider 요청에는 호환 Keyword만 남긴 생성용 Schema를 사용한다.
  - 선택 필드는 생성용 Schema에서 required·nullable로 만들고, 응답 후 null을 제거한다.
  - 최종 결과는 원래 Workmate Schema로 다시 검증한다.
- 분류: `평가기`, `Provider`

#### 정식 Schema와 의미 검증 강화

- 근거 결과: [run-20260808-200934.jsonl](../llm-evaluation/results/run-20260808-200934.jsonl), [summary-20260808-212115.csv](../llm-evaluation/results/summary-20260808-212115.csv)
- 문제:
  - 빈 문자열, 점수 범위 초과와 근거 문장 변형이 단순 포함 검사만으로 충분히 구분되지 않았다.
  - Schema만 통과해도 업무 분류와 출처가 틀릴 수 있었다.
- 수정 이유: 형식 준수와 실제 업무 정답을 분리해 평가해야 했다.
- 반영:
  - `schema_valid`와 `semantic_valid`를 분리했다.
  - 필수 문구, 금지 문구, Source ID와 회의 근거 원문 일치를 평가했다.
  - Schema와 의미 검증이 모두 통과해야 `final_score=1`이 되도록 했다.
- 결과: OpenAI 2/4, Qwen 1/4, 로컬 Llama 0/4로 모델별 의미 정확도 차이가 드러났다.
- 분류: `평가기`

#### NVIDIA 후보 연결 점검

- 근거 결과: [summary-20260808-222737.csv](../llm-evaluation/results/summary-20260808-222737.csv), [summary-20260808-234530.csv](../llm-evaluation/results/summary-20260808-234530.csv)
- 문제:
  - `qwen/qwen3-next-80b-a3b-instruct`가 NVIDIA 모델 목록에서 확인되지 않았다.
  - 대체한 `meta/llama-3.3-70b-instruct`는 장시간 Timeout과 날짜·공백 형식 오류가 발생했다.
- 수정 이유: 존재하지 않는 모델을 본 평가에 포함하지 않고 Provider 실패를 모델 품질 실패와 분리해야 했다.
- 반영:
  - 평가 시작 전 NVIDIA `/models` 확인을 추가했다.
  - NVIDIA Qwen 대신 NVIDIA Llama 후보를 연결했다.
  - Timeout·HTTP 오류 관찰값을 결과에 남겼다.
- 분류: `모델`, `Provider`, `평가기`

### 2026-08-09

#### Provider 실패·Retry·상태 기록 보강

- 근거 결과: [summary-20260809-003518.csv](../llm-evaluation/results/summary-20260809-003518.csv)
- 문제:
  - Timeout이나 HTTP 5xx가 Schema 실패처럼 보이면 모델 출력 품질이 왜곡됐다.
  - 재시도별 시간과 Token을 확인하기 어려웠다.
- 수정 이유: 모델이 답하지 못한 경우와 답했지만 틀린 경우를 분리해야 했다.
- 반영:
  - `execution_status`, `provider_error_type`과 `attempt_details`를 추가했다.
  - Timeout·429·502·503·504를 제한적으로 재시도했다.
  - Provider 실패는 Schema·의미 점수를 비워 품질 집계에서 제외했다.
- 결과: NVIDIA Llama는 4건 모두 응답을 완료했지만 최종 1/4이고 평균 지연이 매우 커 후보 우선순위가 낮아졌다.
- 분류: `Provider`, `평가기`

#### Full Case 20개와 Skill별 의미 검증 확대

- 파일: [full_cases.jsonl](../llm-evaluation/cases/full_cases.jsonl)
- 문제: Sample 4건만으로는 기능별 변동성과 예외 상황을 판단하기 어려웠다.
- 수정 이유: 일일 브리핑, 주간 보고, 회의 분석과 회의 검색을 각각 여러 입력으로 검증해야 했다.
- 반영:
  - Skill별 5건, 총 20건의 Case를 구성했다.
  - 우선순위 보존, 주간 분류, 회의 근거 구간, 검색 답변과 인용문 검사를 추가했다.
- 분류: `Case`, `평가기`

#### NVIDIA Gemma Adapter와 4개 후보 비교

- 근거 결과: [summary-20260809-165224.csv](../llm-evaluation/results/summary-20260809-165224.csv), [summary-20260809-172227.csv](../llm-evaluation/results/summary-20260809-172227.csv)
- 문제:
  - Gemma는 일반 Strict `response_format`과 다른 요청 제약, 비동기 `202` 응답과 thought 접두사 처리가 필요했다.
  - 첫 실행에서 연결 종료로 일일 브리핑 1건이 Provider 실패했다.
- 수정 이유: Provider 특성 때문에 모델 품질이 왜곡되지 않게 Adapter를 맞춰야 했다.
- 반영:
  - Gemma Schema를 Prompt에 제공하고 반환값은 동일한 정식 Schema로 검증했다.
  - thinking 비활성화, thought 접두사 제거와 `202` 상태 조회를 추가했다.
  - 네 모델을 동일 Sample Case로 다시 비교했다.
- 결과: OpenAI 4/4, NVIDIA Gemma 3/4, NVIDIA Llama 1/4, 로컬 Qwen 0/4였다.
- 분류: `모델`, `Provider`, `평가기`

### 2026-08-10

#### OpenAI 호환 API 단일 모델 평가 전환

- 근거 결과: [summary-20260810-102623.csv](../llm-evaluation/results/summary-20260810-102623.csv)
- 문제: 기존 네 후보를 잠시 보류하고 별도 OpenAI 호환 Endpoint의 모델 하나만 평가할 필요가 있었다.
- 수정 이유: 과거 OpenAI 결과와 새 Provider 결과를 같은 그룹으로 섞지 않고 비교 가능하게 남기기 위해서다.
- 반영:
  - `OPENAI_BASE_URL2`, `OPENAI_API_KEY2`, `OPENAI_MODEL2`를 사용하는 `openai2` 모델 그룹을 추가했다.
  - 기본 평가 대상을 `openai2` 하나로 변경했다.
  - 가격 정보를 알 수 없어 비용 값은 계산하지 않았다.
- 결과: API·Schema 4/4, 의미 검증 3/4였고 주간 보고에서 blocked 업무와 다음 주 계획이 누락됐다.
- 분류: `모델`, `Provider`, `평가기`

#### 주간 보고 규칙과 의미 오류 재요청

- 근거 결과: [summary-20260810-103840.csv](../llm-evaluation/results/summary-20260810-103840.csv)
- 문제:
  - blocked Task가 `unresolved_issues`에서 누락됐다.
  - 다음 주 마감 Task가 `next_week_plans`에서 누락됐다.
  - 기존 실행기는 Schema 오류만 재요청하고 의미 오류는 재요청하지 않았다.
- 수정 이유: 평가 기준을 낮추지 않고 실제 운영의 검증·수정 흐름을 재현하기 위해서다.
- 반영:
  - blocked·기한 초과·다음 주 마감·Source ID 규칙을 System Prompt에 명시했다.
  - Schema 오류 1회와 의미 오류 1회를 각각 수정 요청하도록 했다.
  - `repair_type`으로 최초·Schema 수정·의미 수정을 구분했다.
- 결과: 동일 Sample 4건이 4/4 통과했다.
- 분류: `Prompt`, `평가기`

#### Full Case 1차 평가에서 발견된 평가 데이터 오류 수정

- 근거 결과: [summary-20260810-104253.csv](../llm-evaluation/results/summary-20260810-104253.csv)
- 변경 전 결과: API 20/20, 최종 16/20, 평균 기대치 96.65%.
- 발견된 문제:
  - `daily-002`의 `importance=30`, `blocked_or_overdue=20`이 Schema 최대 20·15를 초과했다.
  - `daily-003`의 `importance=25`가 최대 20을 초과했다.
  - `daily-004`의 `importance=25`, `blocked_or_overdue=20`이 최대 20·15를 초과했다.
  - 모델이 Schema를 맞추면 사전 계산값 보존 검사를 실패하게 되는 상충 조건이었다.
  - `search-002`는 회의명이 `sources`에 있는데도 `answer` 본문에 다시 포함하도록 강제했다.
  - 마지막 의미 수정 결과가 실패해도 `attempt_details.error_type`이 비어 보였다.
- 수정 이유: 모델 오류와 잘못된 평가 데이터·로그 오류를 분리하기 위해서다.
- 반영:
  - 세 일일 Case의 점수 구성값과 총점을 Schema 범위 및 합계에 맞췄다.
  - `search-002.answer_must_include`는 질문에 대한 날짜·시간만 요구하고 회의명은 전체 출력과 출처에서 검증하도록 바꿨다.
  - dry-run에서 `precomputed_priorities`의 Schema 범위와 점수 합계를 검증하도록 했다.
  - 최종 의미 실패도 `attempt_details`에 `semantic` 오류로 기록하도록 했다.
- 검증: 단위 테스트 20개, Python 구문 검사, Full Case 20개 dry-run 통과.
- 수정 후 실제 모델 결과:
  - 근거: [summary-20260810-111505.csv](../llm-evaluation/results/summary-20260810-111505.csv), [run-20260810-111505.jsonl](../llm-evaluation/results/run-20260810-111505.jsonl)
  - 네 Skill 모두 최종 5/5로 전체 20/20을 통과했다.
  - 최초 응답은 19/20이었고 `weekly-004`가 의미 수정 1회 후 통과했다.
  - 전체 호출 21회, Case당 평균 1.05회였다.
  - 평균 지연 4.36초, p50 3.17초, p95 7.35초였다.
  - 입력 Token 17,983개, 출력 Token 4,843개였으며 Provider 가격 정보가 없어 비용은 계산하지 않았다.
- 분류: `Case`, `평가기`

#### 독립적인 Full Case 2 세트 추가

- 파일: [full_cases2.jsonl](../llm-evaluation/cases/full_cases2.jsonl)
- 추가 이유: 첫 번째 Full Case에 맞춘 Prompt나 평가기 변경이 다른 입력에서도 일반화되는지 확인하기 위해서다.
- 반영:
  - 기존 Case ID, Task 제목, 회의 내용과 검색 질문을 재사용하지 않았다.
  - 일일 브리핑, 주간 보고, 회의 분석과 회의 검색을 각각 5건씩 구성했다.
  - 사전 계산 우선순위는 정식 Schema 범위와 점수 합계를 만족하도록 작성했다.
  - 두 Case 세트의 ID와 Task 제목이 겹치지 않는지 자동 테스트를 추가했다.
- 실제 모델 결과:
  - 근거: [summary-20260810-113712.csv](../llm-evaluation/results/summary-20260810-113712.csv), [run-20260810-113712.jsonl](../llm-evaluation/results/run-20260810-113712.jsonl)
  - 네 Skill 모두 최종 5/5로 전체 20/20을 통과했다.
  - 최초 응답은 15/20이었고 Schema 수정 3회와 의미 수정 3회가 발생했다.
  - 전체 호출 26회, Case당 평균 1.30회였다. `meeting-010`은 두 차례 수정되어 총 3회 호출됐다.
  - 평균 지연 6.86초, p50 5.58초, p95 17.40초였다.
  - 입력 Token 24,655개, 출력 Token 6,825개였으며 Provider 가격 정보가 없어 비용은 계산하지 않았다.
- 분류: `Case`

#### 기본 LLM 확정

- 결정: OpenAI 호환 API의 `openai/gpt-4.1-mini`를 Workmate 기본 LLM으로 사용한다.
- 적용: 운영 구현은 단일 Provider Client만 두고 `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL`로 설정한다.
- 평가기: 기존 실행 결과와 구분하기 위해 `openai2` 그룹과 `OPENAI_BASE_URL2`, `OPENAI_API_KEY2`, `OPENAI_MODEL2`를 유지한다.
- 보류: 기존 OpenAI, 로컬 Qwen, NVIDIA Llama와 NVIDIA Gemma 후보는 당장 운영 구현에 포함하지 않는다.
- 재검토 조건: 현재 API 할당량이 소진되거나 계약이 종료되면 같은 Case와 Schema로 보류 후보를 다시 평가한 뒤 대체 모델을 수동으로 선정한다.
- 근거: Sample 4/4, 수정된 Full Case 1 최종 20/20과 독립 Full Case 2 최종 20/20을 통과했다. 다만 Full Case 2의 최초 응답은 15/20이므로 운영에서도 Schema·의미 검증과 제한된 수정 요청을 유지한다.
- 분류: `모델`, `기술 결정`

#### 현재 평가기 검증 상태

- 단위 테스트 21개 통과
- `full_cases.jsonl` 20개 JSON Schema·입력 규칙 dry-run 통과
- `full_cases2.jsonl` 20개 JSON Schema·입력 규칙 dry-run 통과
- 분류: `평가기`, `Case`

### 다음 기록 방법

재평가할 때마다 다음 항목을 위 날짜 아래에 추가한다.

1. 실행 결과 파일, 모델명과 Repeat 횟수
2. 최초 응답 통과율과 수정 후 최종 통과율
3. 기능별 통과 수와 Schema·의미 수정 요청 횟수
4. 평균·p50·p95 지연, 총 호출 수와 Case당 평균 호출 수
5. 입력·출력 Token과 확인 가능한 비용
6. 실패가 모델·Prompt·Case·평가기·Provider 중 어디에 해당하는지
7. 변경 이유, 변경 파일과 같은 Case 재평가 결과
8. Prompt·Schema Version 또는 Hash와 고정된 생성 설정
