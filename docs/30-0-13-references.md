# W0-13 — 참조 자료

> [30-0-w0-baseline.md](30-0-w0-baseline.md) §13의 상세 문서.

"무엇을 참조하는가"가 아니라 **"어디를 왜 읽는가"** 를 기록한다.

## 1. 설계 근거 문서

### 30-langgraph-migration-plan.md

| 절 | 읽는 이유 |
| --- | --- |
| §0 전제와 결정 기록 | **D1~D6이 확정됐는지**(W0-E1) |
| §5 W0 | 단계 정의 |
| §7.1 | 스위치오버와 롤백 — 기준 Commit의 역할 |
| §7.2 | 동결 구역 — 미커밋 변경이 여기 해당하는지 |
| §9 | 완료 기준 — W0가 그 판정의 기준선을 만든다 |

### AGENTS.md

**W0에서 가장 많이 참조한 문서다.** 측정 단계의 판단 기준이 여기 있다.

| 규칙 | W0에서의 적용 |
| --- | --- |
| **작업 시작 순서** | `docs/README.md` → `HANDOFF.md` → 마일스톤 문서 → 증빙 → Schema·테스트 → 테스트 실행 |
| **"외부 인증이나 Provider Secret이 필요한 테스트는 설정 여부를 먼저 확인하고, 실행하지 못한 경우 원인과 재현 조건을 기록한다"** | W0-R4, SKIP 12건 처리 |
| **"자동 재시도는 명령의 작업 디렉터리·환경 변수 전달·일시적인 실행 환경처럼 결과 계약을 바꾸지 않는 수정에 한정한다"** | venv 복구의 근거 |
| **"실패한 테스트를 삭제하거나 우회하지 않는다"** | 중단 기준 |
| **"하나의 커밋에는 하나의 논리적 변경만 넣는다"** | 커밋 2건 분리 |
| **"백로그 완료 시에는 (…) 로컬 커밋으로만 남기고 원격 Push하지 않는다"** | Push 안 함 |
| **"실행 증빙과 `HANDOFF.md`에는 `자동 재작업 착수: 예/아니오`를 기록"** | 증빙 §2 |
| "구현 결과가 생기기 전에는 빈 `result.md`를 만들지 않는다" | 결과가 나온 뒤 작성 |
| "API Key, Token, Presigned URL (…) 커밋·Push하지 않는다" | W0-R5 |

---

## 2. 코드·설정 참조

### 2.1 환경 정의

| 위치 | 읽는 이유 |
| --- | --- |
| [`pyproject.toml`](../workmate-agent/pyproject.toml) | **`requires-python = ">=3.12,<3.13"`** — 환경 복구 시 버전 제약 |
| 동 `dependencies` | 고정 버전 목록(`a2a-sdk==1.1.2`, `fastapi==0.116.1` 등) |
| `uv.lock` | 실제 설치 버전. **복구 시 그대로 사용** |
| `.venv/pyvenv.cfg` | **깨진 원인 확인** — `home = C:\Python312` |

### 2.2 테스트 DB 요구사항 (W0-F3)

| 위치 | 읽는 이유 |
| --- | --- |
| [`migrations/004_search_data.sql`](../workmate-agent/migrations/004_search_data.sql) | **`CREATE EXTENSION IF NOT EXISTS vector; pg_trgm;`** — pgvector 이미지가 필요한 이유 |
| [`runtime.py:402-414`](../workmate-agent/app/a2a/runtime.py#L402) | `DATABASE_URL` 유무에 따른 백엔드 선택 |
| `tests/test_*_postgres_integration.py` | `WORKMATE_TEST_DATABASE_URL` 환경변수 사용 |

### 2.3 조사 대상 (W0-F1, W0-F2)

| 위치 | 읽는 이유 |
| --- | --- |
| [`runtime.py:228-233`](../workmate-agent/app/a2a/runtime.py#L228) | **`save_checkpoint` 호출** — 유일한 사용처 |
| [`persistence.py:63-70`](../workmate-agent/app/a2a/persistence.py#L63) | `a2a_checkpoints` 스키마 |
| [`persistence.py:281-307`](../workmate-agent/app/a2a/persistence.py#L281) | `save_checkpoint()` 구현 |
| [`external_sync.py`](../workmate-agent/app/workflows/external_sync.py) | `ExternalSyncWorkflow` |
| [`dev_gmail_sync_api.py:3`](../workmate-agent/app/dev_gmail_sync_api.py#L3) | **"운영 자동 동기화 Job은 아직 없다"** — 호출자 부재의 근거 |

### 2.4 미커밋 변경 (W0-T4)

커밋하기 전에 **전부 읽었다.** 내용을 모르고 커밋하지 않는다.

| 위치 | 변경 내용 |
| --- | --- |
| [`assistant_router.py:429-439`](../workmate-agent/app/workflows/assistant_router.py#L429) | `proposal_id` 누락 수정 + 주석(99번 문서 32번 항목) |
| [`meetings.py:444-453`](../workmate-agent/app/workflows/meetings.py#L444) | warning 분류 |
| [`meeting_answer.py`](../workmate-agent/app/meeting_answer.py) | `_summarize_with_llm()` 추가 — **기능 변경** |
| `tests/test_assistant_router.py`, `tests/test_meeting_answer.py` | 위 변경의 테스트 |

**`meeting_answer.py`의 변경이 예상보다 컸다.** warning 분류만인 줄 알았는데 LLM 답변 생성이 들어
있었다. 커밋 메시지에 명시했다.

---

## 3. 증빙 형식 참조

기존 마일스톤 증빙의 형식을 따랐다.

| 위치 | 읽는 이유 |
| --- | --- |
| [`evidence/M0/M0.4/runs/20260813-161223/result.md`](evidence/M0/M0.4/runs/20260813-161223/result.md) | **result.md의 9개 절 구성** |
| `evidence/M0/M0.1/runs/` | run_id 형식(`YYYYMMDD-HHMMSS`) |
| [`HANDOFF.md`](../HANDOFF.md) | "최신 상태 보정" 섹션의 append 패턴 |

### 3.1 기존 증빙에서 가져온 구조

```
1. 기본 정보          작업·담당자·검수자·상태·실행일·실행 ID·코드 버전
2. 최신 실행과 승인    latest_run_id·status·approved_run_id·approved_at·reviewer
3. 목표와 완료 기준
4. 구현 경로
5. 테스트 파일 경로
6. 실행 명령과 결과
7. 검수 항목          항목별 PASS/FAIL + 근거
8. 문제와 수정 이력
9. 최종 판단          승인 여부·검수 의견·다음 조치
```

---

## 4. 후행 단계 문서

| 문서 | W0와의 관계 |
| --- | --- |
| [30-1-3](30-1-3-entry-criteria.md) §2.1 | **기준 Commit이 스냅샷 값을 바꾼다** |
| [30-1-11](30-1-11-rollback.md) §1.1 | 스냅샷 재작성 기한(W7까지) |
| [30-2-5](30-2-5-design.md) §4.4 | W0-F1이 Checkpointer 대체의 근거 |
| [30-7-2](30-7-2-scope.md) §4.1 | W0-F2가 `external_sync` 이동의 근거 |
| [30-7-5](30-7-5-design.md) §5 | W0-F1이 DROP의 근거 |
| [30-9-13](30-9-13-references.md) §3 | W9가 W0 증빙에서 가져갈 것 |

---

## 5. 도구 참조

| 도구 | 확인한 것 |
| --- | --- |
| `uv` | `python install`, `venv --clear`, `sync`의 동작 |
| `uv python list` | 설치된 인터프리터 목록 |
| Docker | 엔진 상태 확인, 컨테이너 실행 |
| `pgvector/pgvector:pg16` | `vector` 확장이 포함된 PostgreSQL 이미지 |
| `git` | `status --porcelain`, `diff --stat`, `log --oneline` |
| `unittest` | `discover -s tests -v`, SKIP 표시 |

### 5.1 `uv venv --clear`

첫 시도가 실패했다.

```
error: Failed to create virtual environment
  Caused by: A virtual environment already exists at: .venv
hint: Use the `--clear` flag or set `UV_VENV_CLEAR=1`
```

**에러 메시지가 해결책을 알려줬다.** 기존 venv가 동작하지 않는 상태였으므로 `--clear`가 안전했다.

---

## 6. 이 문서 묶음

| 문서 | 대응 절 |
| --- | --- |
| [30-0-1](30-0-1-document-info.md) | §1 문서 정보·용어·**발견 사항(W0-F)** |
| [30-0-2](30-0-2-scope.md) | §2 목적과 범위, 측정의 원칙 |
| [30-0-3](30-0-3-entry-criteria.md) | §3 선행 조건과 실제 결과 |
| [30-0-4](30-0-4-requirements.md) | §4 요구사항 W0-R1~R7과 충족 여부 |
| [30-0-5](30-0-5-design.md) | §5 설계 — 측정 대상, 환경 정의, 절차 |
| [30-0-6](30-0-6-wbs.md) | §6 작업 분해와 **실제 수행 결과** |
| [30-0-7](30-0-7-verification.md) | §7 검증 설계와 **실제 결과** |
| [30-0-8](30-0-8-traceability.md) | §8 추적성, **발견 사항 추적** |
| [30-0-9](30-0-9-exit-criteria.md) | §9 완료 정의와 달성 상태 |
| [30-0-10](30-0-10-results.md) | §10 **실행 결과** (W0 고유) |
| [30-0-11](30-0-11-risks.md) | §11 위험과 **실제 결과** |
| [30-0-12](30-0-12-rollback.md) | §12 롤백·중단 기준 |
| [30-0-13](30-0-13-references.md) | §13 참조 (이 문서) |
