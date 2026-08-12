# Workmate STT 평가

OpenAI `gpt-4o-transcribe`의 한국어 회의 음성 인식 품질을 평가한다. 실제 음성은 저장소에 커밋하지 않는다.

## 준비

```powershell
Copy-Item .env.example .env
pip install -r requirements.txt
```

`.env`에 `OPENAI_STT_API_KEY`를 입력한다. 키는 문서·결과에 기록하지 않는다.

## Case 형식

```json
{"case_id":"meeting-001","audio":"audio/pilot/meeting-001.wav","language":"ko","must_include":["QA 빌드"],"forbidden":["스토어 출시 완료"],"expected_speaker_count":null}
```

## 실행

```powershell
python run_eval.py --cases cases/pilot_cases.jsonl --dry-run
python run_eval.py --cases cases/pilot_cases.jsonl
```

결과는 `results/`에 JSONL·CSV·지표 JSON으로 저장한다. `--dry-run`은 외부 API를 호출하지 않는다.

## Streaming Pilot

16kHz mono WAV를 24kHz PCM16으로 변환해 200ms Chunk로 Realtime Transcription에 전송한다.

```powershell
python run_streaming_eval.py --cases cases/pilot_cases.jsonl --chunk-ms 200
```

Realtime 결과는 `results/streaming-metrics-*.json`에 저장한다.
