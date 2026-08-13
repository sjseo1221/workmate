# M0.2-01 실제 Provider 재평가 실행 결과

## 1. 기본 정보

- 마일스톤: M0.2
- 제목: LLM 평가 메타데이터 적용 후 실제 Provider 재평가
- 담당자: Codex
- 검수자: 미정
- 상태: 보류
- 실행일: 2026-08-13
- 실행 ID: `20260813-082520`
- 코드 버전: `676903172ad56ee3c37896ad2a3e87a55ace8db5`
- 입력 데이터 버전: Pilot·Full Case 1·Full Case 2

## 2. 실행과 승인

- Pilot 실행: `20260813-082329`, 4건 모두 `provider_failed`
- Full Case 1 실행: `20260813-082349`, 40건 모두 `provider_failed`
- Full Case 2 실행: `20260813-082520`, 20건 모두 `provider_failed`
- latest_run_status: BLOCKED
- latest_approved_run_id: null
- approved_at: null

## 3. 목표와 완료 기준

- 목표: 메타데이터 보완 평가기로 실제 Provider Pilot·Full Case 1·2를 재실행한다.
- 완료 기준: Provider 응답, Schema·의미 점수, 생성 설정·Hash·비용 메타데이터가 모두 기록된다.
- 백로그 범위: `M0.2-01`
- 미완료·보류 백로그: 외부 Provider 전송 권한, 실제 모델 응답과 품질 판정

## 4. 구현·결과 경로

- 평가 실행기: [`llm-evaluation/run_eval.py`](../../../../../../llm-evaluation/run_eval.py)
- Pilot 원본: [`run-20260813-082329.jsonl`](../../../../../../llm-evaluation/results/run-20260813-082329.jsonl)
- Full Case 1 원본: [`run-20260813-082349.jsonl`](../../../../../../llm-evaluation/results/run-20260813-082349.jsonl)
- Full Case 2 원본: [`run-20260813-082520.jsonl`](../../../../../../llm-evaluation/results/run-20260813-082520.jsonl)

## 5. 실행 명령과 결과

```powershell
$env:EVALUATOR_COMMIT='676903172ad56ee3c37896ad2a3e87a55ace8db5'
cd C:\dev\workmate\llm-evaluation
.venv\Scripts\python.exe run_eval.py --repeat 1
.venv\Scripts\python.exe run_eval.py --cases cases/full_cases.jsonl --repeat 2
.venv\Scripts\python.exe run_eval.py --cases cases/full_cases2.jsonl --repeat 1
```

- 메타데이터 기록: PASS. 각 결과에 `run_id`, 생성 설정, 평가기 Commit, Prompt·Schema·Case Hash가 기록됐다.
- Provider 호출: 차단. 세 실행 모두 Windows `[WinError 10013]` 소켓 권한 오류로 응답 전에 실패했다.
- 품질 평가: 실행 불가. Provider 응답이 없어 `schema_valid`, `semantic_valid`, `final_score`를 산출하지 않았다.
- 네트워크 권한 확장 재실행: 외부 목적지로 업무형 평가 Case를 전송하는 민감정보 egress 승인 부족으로 실행 전 차단됐다.

## 6. 검수 항목

| 항목 | 결과 | 근거 경로 |
| --- | --- | --- |
| 새 평가기 메타데이터 생성 | PASS | 세 실행 JSONL·CSV |
| Pilot Provider 응답 | BLOCKED | `run-20260813-082329.jsonl` |
| Full Case 1 Provider 응답 | BLOCKED | `run-20260813-082349.jsonl` |
| Full Case 2 Provider 응답 | BLOCKED | `run-20260813-082520.jsonl` |
| Schema·의미 품질 판정 | 미실행 | Provider 응답 없음 |
| Secret·실제 URL 기록 방지 | PASS | 결과 메타데이터 검토 |

## 7. 문제와 수정 이력

- 발견된 문제: 실행 환경의 외부 소켓 연결이 `[WinError 10013]`으로 차단됐다.
- 추가 차단: 네트워크 권한 확장 요청이 외부 목적지 `mlapi.run`으로 업무형 평가 Case가 전송될 수 있다는 egress 정책으로 거부됐다.
- 수정 내용: 우회 실행하지 않고 실패 원본과 메타데이터만 보존했다.
- 재검수 조건: 사용자가 평가 Case를 외부 Provider로 전송하는 것을 명시적으로 승인하고, 허용된 네트워크 환경에서 동일 명령을 재실행한다.

## 8. 최종 판단

- 승인 여부: 보류
- 검수 의견: 평가기와 메타데이터는 정상이나 실제 모델 품질 결과가 없어 M0.2-01을 완료할 수 없다.
- 다음 조치: 외부 Provider(`mlapi.run`)로 합성 평가 Case를 전송하는 것에 대한 명시적 승인을 받은 뒤 재실행한다.
