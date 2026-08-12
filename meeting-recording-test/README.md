# Meeting Recording Integration Test

Workmate 회의 녹음 흐름의 WebSocket·RecordingSession 계약을 검증하는 독립 테스트 어댑터입니다. 아래의 비버전 경로는 테스트 전용이며, 정식 운영 API는 `docs/02-a2a-interface.md`의 `/api/v1/...` 경로를 사용합니다.

## 1단계 범위

- `POST /meetings`: 회의와 RecordingSession 생성
- `WS /meetings/{meeting_id}/recording`: JSON 음성 Chunk 수신
- Chunk 순번·중복·재연결 경계 검증
- `POST /meetings/{meeting_id}/recording/complete`: 녹음 종료와 transcript Task 생성 Mock

이 폴더는 STT 모델 평가(`stt-evaluation`)와 분리되어 있으며, 실제 Workmate 서버가 준비되면 정식 운영 API에 대응하는 Client 어댑터를 사용합니다. 테스트 어댑터의 상태 전이·권한·멱등성 검증 규칙은 운영 계약과 동일하게 유지합니다.

## 실행

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn mock_workmate.app:app --host 127.0.0.1 --port 8010
```

별도 터미널:

```powershell
python client/test_recording.py --audio ..\stt-evaluation\audio\pilot\meeting-001.wav
```

## Docker Compose

```powershell
docker compose up --build -d
docker compose ps
# recording-mock가 (healthy)가 된 뒤 다음 명령 실행
curl.exe http://127.0.0.1:8010/health/live
python client/test_recording.py --base-url http://127.0.0.1:8010 --audio ..\stt-evaluation\audio\pilot\meeting-001.wav
docker compose down
```

컨테이너는 `recording-test-data` 볼륨에 테스트용 SQLite를 저장하므로 재시작 후에도 Meeting·Task·Artifact 조회를 확인할 수 있습니다.

오류 계약은 다음처럼 실행합니다.

```powershell
python client/test_errors.py --base-url http://127.0.0.1:8010 --audio ..\stt-evaluation\audio\pilot\meeting-001.wav
```

## 메시지 계약

클라이언트는 각 Chunk를 다음 JSON으로 전송합니다. 실제 음성 바이트는 테스트 단순화를 위해 Base64로 담습니다.

```json
{"chunk_no":0,"audio_base64":"...","sample_rate":16000,"format":"pcm16"}
```

실제 구현에서는 JSON 메타데이터와 Binary WebSocket Frame을 분리할 수 있습니다.
