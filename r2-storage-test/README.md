# R2 Storage Smoke Test

Workmate의 Cloudflare R2 단일 Private 버킷 계약을 검증하는 별도 테스트 폴더다. 실제 오디오 대신 짧은 테스트 바이트를 사용하며, 테스트가 끝나면 생성한 객체를 삭제한다.

## 1. 준비

```powershell
cd C:\dev\workmate\r2-storage-test
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

`.env`에 R2 Endpoint, 제한형 Access Key, Secret, Bucket을 입력한다. 실제 `.env`는 Git에 커밋하지 않는다.

## 2. 설정만 확인

```powershell
.\venv\Scripts\python.exe smoke_test.py --dry-run
```

## 3. 실제 검증

```powershell
.\venv\Scripts\python.exe smoke_test.py
```

검증 항목:

1. Presigned PUT 업로드
2. `HeadObject` MIME·크기 조회
3. Presigned GET 다운로드와 checksum 비교
4. Lifecycle 설정 조회
5. 테스트 객체 삭제

Lifecycle 정책까지 필수로 요구하려면 다음을 사용한다.

```powershell
.\venv\Scripts\python.exe smoke_test.py --require-lifecycle
```

API Key·Secret·Presigned URL은 결과에 출력하지 않는다.
