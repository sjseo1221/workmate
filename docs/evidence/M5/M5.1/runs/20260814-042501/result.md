# M5.1 검수 결과

## 기본 정보

- 실행 ID: `20260814-042501`
- 상태: 재작업
- 목적: LLM/Embedding endpoint 최소 호출 검증

## 결과

| 요청 | 모델명 | 결과 |
| --- | --- | --- |
| `/v1/chat/completions` | `openai/gpt-4.1-mini` | FAIL, HTTP 400 |
| `/v1/embeddings` | `openai/text-embedding-3-small` | FAIL, HTTP 400 |
| `/v1/chat/completions` | `gpt-4.1-mini` | PASS |
| `/v1/embeddings` | `text-embedding-3-small` | PASS, 1536차원 |

## 판단

네트워크와 Token은 endpoint 최소 호출에서 동작했으며, 실패 원인은 Workmate Compose의 `openai/` 모델명 접두사와 OpenAI API 표준 모델명 불일치다. 현재 Workmate 문서·코드의 모델 계약을 임의 변경하지 않고 검수를 중단한다.

## 재개 조건

- OpenAI 직접 endpoint를 사용할 경우 모델명 매핑을 명시적으로 정한다.
- OpenAI 호환 Gateway를 사용할 경우 `openai/` 접두사를 지원하는 Base URL을 설정한다.
- 모델 계약 변경 시 관련 문서·평가·Embedding 재검증을 함께 수행한다.
