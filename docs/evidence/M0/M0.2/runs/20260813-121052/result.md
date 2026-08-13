# M0.2-03 검수 결과

## 1. 기본 정보

- 마일스톤: M0.2
- 제목: STT 평가 승인
- 담당자: Codex
- 검수자: 사용자 확인 필요
- 상태: 검수 중
- 실행일: 2026-08-13
- 실행 ID: 20260813-121052
- 코드 버전: `c9d7384`
- 입력 데이터 버전: 합성 한국어 음성 20 Case·Realtime 2 Case·Chunk 재연결 E2E 2 Case

## 2. 최신 실행과 승인

- latest_run_id: 20260813-121052
- latest_run_status: PASS_WITH_CAVEAT
- latest_approved_run_id: null
- approved_at: null

## 3. 목표와 완료 기준

- 목표: `gpt-4o-transcribe` 파일 기반·Realtime Streaming MVP의 품질과 입력 계약을 검토한다.
- 완료 기준: 합성 파일 평가 결과와 Streaming Partial/Final 이벤트·Provider 오류·Chunk 재연결 결과를 승인하고, 실제 회의 음성 미평가 위험을 M3.3에 연결한다.
- 백로그 범위: M0.2-03
- 미완료·보류 백로그: 사용자 승인, 실제 회의 음성 WER/CER·화자 분리·잡음·겹침 발화 평가

## 4. 구현 경로

- 구현 코드: [run_eval.py](../../../../../../stt-evaluation/run_eval.py), [run_streaming_eval.py](../../../../../../stt-evaluation/run_streaming_eval.py), [run_e2e_pipeline.py](../../../../../../stt-evaluation/run_e2e_pipeline.py)
- Schema 또는 Migration: [구현·검증 가이드](../../../../../../docs/12-implementation-verification-guide.md), [기술 상세 설계](../../../../../../docs/07-technical-specification.md)
- UI 코드: 해당 없음

## 5. 테스트 파일 경로

- 단위 테스트: [test_runner.py](../../../../../../stt-evaluation/tests/test_runner.py)
- 통합 테스트 결과: [metrics-20260811-025641.json](../../../../../../stt-evaluation/results/metrics-20260811-025641.json), [streaming-metrics-20260811-032816.json](../../../../../../stt-evaluation/results/streaming-metrics-20260811-032816.json), [e2e-metrics-20260811-034055.json](../../../../../../stt-evaluation/results/e2e-metrics-20260811-034055.json)
- UI 테스트: 해당 없음
- Fixture/입력: [synthetic_cases_20.jsonl](../../../../../../stt-evaluation/cases/synthetic_cases_20.jsonl), [pilot_cases.jsonl](../../../../../../stt-evaluation/cases/pilot_cases.jsonl)
- 기대 결과: Provider 오류 0건, 필수 문구 검증, Streaming Partial/Final 수신, Chunk 재연결 복구
- 모델 평가 Case: 합성 파일 20건, Realtime 2건, E2E 2건
- 모델 평가 결과: [EVALUATION_HISTORY.md](../../../../../../stt-evaluation/EVALUATION_HISTORY.md)

## 6. 실행 명령과 결과

```text
cd C:\dev\workmate\stt-evaluation
venv\Scripts\python.exe -m unittest discover -s tests -v
venv\Scripts\python.exe run_eval.py --cases cases\synthetic_cases_20.jsonl --dry-run
venv\Scripts\python.exe -m py_compile run_eval.py run_streaming_eval.py run_e2e_pipeline.py
git diff --check
```

- 실행 로그: 단위 테스트 2개 PASS, 20 Case dry-run PASS(외부 API 미호출), Python 구문 검사 PASS, `git diff --check` PASS
- API 응답 또는 Artifact: 기존 실제 Provider 평가 결과를 검토함. 합성 파일 19/20(95%), Realtime 2/2, E2E 2/2, Provider 오류 0건
- 화면 캡처: 해당 없음
- 함수 문서화: 평가기 파일 입력·Streaming·Chunk 재연결 경계를 확인함

## 7. 검수 항목

| 항목 | 결과 | 근거 경로 |
| --- | --- | --- |
| 모델 `gpt-4o-transcribe` 파일 평가 | PASS (19/20, 95%) | [metrics](../../../../../../stt-evaluation/results/metrics-20260811-025641.json) |
| 파일 평가 Provider 오류 | PASS (0/20) | [metrics](../../../../../../stt-evaluation/results/metrics-20260811-025641.json) |
| Realtime Streaming Partial/Final | PASS (2/2, 오류 0건) | [streaming metrics](../../../../../../stt-evaluation/results/streaming-metrics-20260811-032816.json) |
| Chunk 재연결·최종 STT·Task 입력 준비 | PASS (2/2) | [E2E metrics](../../../../../../stt-evaluation/results/e2e-metrics-20260811-034055.json) |
| 실제 회의 음성 WER/CER·화자 분리·잡음·겹침 발화 | 보류 | M3.3 완료 조건으로 연결 |
| STT MVP 사양 승인 | 사용자 승인 필요 | 이 결과와 `docs/06-delivery-plan.md` M0.2-03 |

## 8. 문제와 수정 이력

- 발견된 문제: 합성 Case `synthetic-014`에서 `튜토리얼`이 `포토리얼`로 인식됐다. 최초 루트 경로 `unittest discover`는 하이픈 폴더명 때문에 0개 테스트를 탐색했다.
- 원인: gTTS 합성 발음과 합성 음성의 한계로 실제 회의 품질을 대표하지 않으며, 테스트 탐색 명령이 평가 폴더 경계를 반영하지 않았다.
- 수정 내용: 합성 실패를 삭제하거나 우회하지 않고 이력에 보존했다. 테스트는 `stt-evaluation`을 작업 디렉터리로 지정해 2개 PASS를 재실행했다. 파일 기반 STT와 Realtime 임시 자막을 MVP 범위로 승인하되, 실제 회의 음성 품질은 M3.3에서 별도 평가한다.
- 재검수 실행 ID: 사용자 승인 후 20260813-121052에 승인 메타데이터를 추가한다.

## 9. 최종 판단

- 승인 여부: 미승인
- 검수 의견: 합성 파일·Realtime·Chunk 재연결 E2E 계약은 통과했다. 실제 회의 음성 품질과 화자 분리는 의도적으로 M0.2 완료 기준에서 제외하고 M3.3 위험으로 연결한다.
- 다음 조치: 사용자가 `gpt-4o-transcribe`, 한국어 `ko`, 파일 기반 STT·Realtime 임시 자막 MVP 범위와 실제 음성 평가의 M3.3 이관을 승인하면 M0.2-03을 완료로 전환한다.
