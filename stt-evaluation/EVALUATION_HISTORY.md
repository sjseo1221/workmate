# Workmate STT 평가 이력

실제 음성 원본과 API Key는 저장하지 않는다. 평가 결과와 수정 이유를 날짜순으로 누적한다.

## 2026-08-11

### 평가기 초기 구성

- 대상: OpenAI `gpt-4o-transcribe`
- 입력: 한국어 회의 음성 파일 JSONL Case
- 검증: 파일 존재·필수 필드, 필수 문구 포함, 금지 문구 검출, 처리 지연
- 상태: Pilot 실행기 구성 완료; 실제 음성 API 평가는 별도 승인 후 수행

### gTTS 합성 음성 20 Case 평가

- 모델: `gpt-4o-transcribe`
- 입력: gTTS로 생성한 한국어 MP3 20개, 게임 개발 업무 문장
- 결과: [metrics-20260811-025641.json](results/metrics-20260811-025641.json), [summary-20260811-025641.csv](results/summary-20260811-025641.csv), [run-20260811-025641.jsonl](results/run-20260811-025641.jsonl)
- Provider 오류: 0/20
- 핵심어 포함 판정: 19/20 (95%)
- 실패: `synthetic-014`의 `튜토리얼`이 `포토리얼`로 인식됨
- 평균 처리 시간: 약 1초 내외(Case별 API 응답 편차 있음)
- 판단: API 연결·파일 처리·결과 저장 파이프라인은 통과했다. `튜토리얼` 실패는 gTTS 발음과 합성 음성의 한계이므로 실제 회의 품질 결론으로 사용하지 않는다.
- 분류: `합성 음성`, `Pipeline`, `한국어 고유명사`, `재현성`

### MVP STT 모델 확정

- 확정 모델: `gpt-4o-transcribe`
- 확정 범위: 파일 기반 STT Pipeline 및 MVP 시연
- 근거: 합성 음성 20 Case, Provider 오류 0건, 핵심어 인식 19/20(95%)
- 제한: gTTS 합성 음성이므로 실제 회의의 잡음·다중 화자·겹침 발화·자연 발음은 검증하지 않음

### Realtime Streaming STT Pilot

- 모델: `gpt-4o-transcribe`
- 입력: 16kHz WAV를 24kHz PCM16으로 변환해 200ms Chunk로 전송
- 결과: [streaming-metrics-20260811-032816.json](results/streaming-metrics-20260811-032816.json)
- Case: 2개, Provider 오류 0건, 핵심어 인식 2/2
- Partial 이벤트: Case별 88·90건
- 첫 Partial: 약 31.8~32.2초, Final: 약 39.7~40.1초
- 판단: Realtime 연결·Chunk 전송·Partial/Final 누적·결과 저장은 통과했다. 녹음 파일을 실시간 속도로 재생한 측정값이므로 실제 브라우저 마이크 지연 기준으로 해석하지 않는다.

### MVP STT 사양 최종 확정

- 모델: `gpt-4o-transcribe`
- 파일 기반 근거: 합성 음성 20 Case, 핵심어 19/20(95%), Provider 오류 0건
- Realtime 근거: 합성 WAV 2 Case, Partial·Final 이벤트 수신 성공, Provider 오류 0건
- 입력 계약: mono PCM16 24kHz, 200ms Chunk, 한국어 `ko`
- API 계약: WebSocket `wss://api.openai.com/v1/realtime?intent=transcription`, `session.type=transcription`
- 확정 범위: Workmate MVP 파일 분석과 실시간 임시 자막
- 제외 범위: 화자 분리, 실제 회의 WER/CER, 운영 동시성·비용 최적화

### 녹음 처리 E2E 하네스 Pilot

- 입력: 합성 WAV 2개, 200ms Chunk, Case별 146·147 Chunk
- 검증: Chunk 재연결 경계 복구, 최종 파일 STT, Task 입력용 transcript 생성 가능 여부
- 결과: [e2e-metrics-20260811-034055.json](results/e2e-metrics-20260811-034055.json)
- Chunk 재연결: 통과
- 최종 STT 핵심어: 2/2 통과
- Provider 오류: 0건
- Task 입력 준비: 2/2
- 판단: 로컬 Chunk 상태와 최종 STT 연결은 통과했다. 실제 Workmate WebSocket·RecordingSession API가 없으므로 브라우저-서버 종단 간 검증은 아직 아님.
