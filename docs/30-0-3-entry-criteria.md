# W0-3 — 선행 조건

> [30-0-w0-baseline.md](30-0-w0-baseline.md) §3의 상세 문서.

## 1. 선행 조건 목록

| ID | 조건 | 확인 방법 | 실제 결과 |
| --- | --- | --- | --- |
| W0-E1 | 상위 계획 §4의 결정 D1~D6이 확정됨 | 계획서 §4 표 | **충족**(2026-09-23) |
| W0-E2 | 작업 대상 저장소에 접근 가능 | `git -C workmate-agent status` | 충족 |
| W0-E3 | 실행 환경이 동작 | `uv run python -V` | **미충족 → 복구** |

## 2. 각 조건의 근거

### 2.1 W0-E1 — 결정이 먼저인 이유

W0는 기준선을 만드는 단계이고, **무엇을 기준선에 포함할지가 결정에 달려 있다.**

| 결정 | W0에 미치는 영향 |
| --- | --- |
| D6=B(`a2a_checkpoints` DROP) | Postgres 경로를 기준선에 포함할지 |
| D2=A(스냅샷 선추출) | W1이 W0 직후에 온다 |
| 빅뱅 전환 | 기준선 하나를 끝까지 쓴다 |

실제로 사용자가 "지금 구성해서 기준선에 포함"을 선택한 것이 D6=B와 연결된다 — DROP Migration을
검증하려면 Postgres가 필요하다.

### 2.2 W0-E3 — 실제로 미충족이었다

착수 시점에 `uv run`이 실패했다.

```
error: Querying Python at `C:\dev\workmate\workmate-agent\.venv\Scripts\python.exe`
failed with exit status exit code: 103
[stderr] No Python at '"C:\Python312\python.exe'
```

**원인** `.venv/pyvenv.cfg`의 `home = C:\Python312`(CPython 3.12.4)가 가리키는 인터프리터가 이 PC에서
사라졌다.

```
home = C:\Python312
implementation = CPython
uv = 0.11.28
version_info = 3.12.4
include-system-site-packages = false
prompt = workmate-agent
```

**제약** 프로젝트가 `requires-python = ">=3.12,<3.13"`인데 로컬에 설치된 Python은 3.13뿐이었다.

```
cpython-3.13.14-windows-x86_64-none   C:\Users\...\WindowsApps\python3.13.exe
cpython-3.12.13-windows-x86_64-none   <download available>
```

**해소** [30-0-10](30-0-10-results.md) §3.1 참조.

## 3. 착수 전 확인 명령

W0가 실제로 수행한 순서다.

```bash
cd workmate-agent

# W0-E2
git rev-parse --short HEAD          # 6a87c80
git status --porcelain              # 5개 파일 변경 (미커밋)
git branch --show-current           # feat/M0.1-01-sdk-runtime

# W0-E3
uv --version                        # 0.11.28
uv run python -V                    # 실패 → 복구 필요
```

### 3.1 여기서 두 가지가 드러났다

| 발견 | 조치 |
| --- | --- |
| 미커밋 변경 5개 파일 | 사용자에게 질문 |
| venv 깨짐 | 자동 재작업으로 복구 |

**둘의 처리가 달랐다.** 환경 복구는 자동, 코드 커밋은 질문.

### 3.2 왜 다르게 처리했나

| 항목 | 성격 | `AGENTS.md` |
| --- | --- | --- |
| venv 복구 | 실행 환경 보정. 결과 계약 불변 | **자동 재시도 허용** |
| 미커밋 변경 커밋 | 다른 작업자의 구현을 이력에 남김 | 판단 필요 |

`AGENTS.md`: "자동 재시도는 명령의 작업 디렉터리·환경 변수 전달·일시적인 실행 환경처럼 **결과
계약을 바꾸지 않는 수정**에 한정한다."

커밋은 결과 계약(기준선)을 확정하는 행위다. 게다가 **제가 쓴 변경이 아니었다.**

## 4. 환경 전제

| 항목 | 요구 | 실제 |
| --- | --- | --- |
| Python | `>=3.12,<3.13` | 3.12.13(설치함) |
| uv | — | 0.11.28 |
| 네트워크 | Python 다운로드 | 가능 |
| Docker | PostgreSQL 테스트 DB | Desktop 설치됨, 엔진 정지 |
| 로컬 PostgreSQL | — | **없음** |

### 4.1 Docker가 필요했다

W0-T5(테스트 DB 구성) 시점에 확인했다.

```
Docker version 29.4.3, build 055a478
failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine
```

CLI는 있지만 엔진이 꺼져 있었다. Docker Desktop을 기동해 해소했다.

## 5. 미충족 시 처리 (실제 적용)

| 조건 | 상황 | 처리 |
| --- | --- | --- |
| W0-E3 | venv 깨짐 | **자동 재작업** — Python 3.12 설치 후 venv 재생성 |
| (추가) | 미커밋 변경 | **사용자 질문** → "로컬 커밋으로 고정" |
| (추가) | SKIP 12건 | **사용자 질문** → "지금 구성해서 기준선에 포함" |
| (추가) | Docker 엔진 정지 | 기동 |

## 6. 후행 단계의 선행 조건에 미치는 영향

| W0 결과 | W1 선행 조건 | 관계 |
| --- | --- | --- |
| 기준 Commit `8043c1e` | [W1-E1](30-1-3-entry-criteria.md) | 스냅샷의 대상 |
| 440 passed / 0 skipped | W1-E2 | 깨진 상태의 출력을 기록하면 안 된다 |
| 테스트 DB 구성 | W1-E3 | `search_meetings`·`analyze_meeting` 케이스 |

### 6.1 기준 Commit이 스냅샷 값을 바꾼다

W0에서 커밋한 2건이 W1 스냅샷에 직접 영향을 준다.

| Commit | 영향 |
| --- | --- |
| `274c204` | `_default_proposals_context()`에 `proposal_id` 추가 → `assistant_ask` 컨텍스트 값 |
| `8043c1e` | 검색 warning이 `grounded`에 따라 갈림 → `search_meetings` 케이스 값 |

**이 커밋 이전 상태로 스냅샷을 뜨면 W3에서 전부 불일치가 난다.**

## 7. 참조

- [30-0-10](30-0-10-results.md) — 실제 결과와 조치
- [30-1-3](30-1-3-entry-criteria.md) §2.1 — W1이 기준 Commit에 거는 조건
- [`AGENTS.md`](../AGENTS.md) — 자동 재시도 범위
