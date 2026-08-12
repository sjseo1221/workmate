# R2 저장소 검증 이력

## 2026-08-11

### 테스트 하네스 생성 및 설정 Dry-run

- 대상: Cloudflare R2 단일 Private 버킷 `workmate`
- 검증기: `smoke_test.py`
- 검증 범위: Presigned PUT, `HeadObject`, Presigned GET checksum, Lifecycle 조회, 테스트 객체 삭제
- 결과: Python 구문 검사와 `--dry-run` 실행 성공
- 현재 상태: `R2_ENDPOINT`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`가 로컬 환경에 없어 실제 API 호출은 보류
- 보안: 실제 Secret·Presigned URL은 문서와 결과에 기록하지 않음

### 실제 R2 PUT·GET·DELETE 검증

- 실행: `smoke_test.py`
- 결과: Presigned PUT 성공, `HeadObject` 성공, Presigned GET 및 checksum 일치, 테스트 객체 삭제 성공
- 확인된 MIME·크기: `audio/wav`, 26 bytes
- Lifecycle 조회: `AccessDenied`로 확인 불가. 현재 제한형 Token에 Lifecycle 조회 권한이 없음
- 판단: R2 Endpoint·인증·객체 저장·조회·삭제 계약은 통과했다. Lifecycle은 Cloudflare Dashboard에서 확인하거나 해당 권한을 추가한 Token으로 별도 검증해야 한다.
