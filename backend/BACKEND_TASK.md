# Hypo Loop — 백엔드 작업 지시서

> 이 문서는 백엔드 구현을 AI(Claude 등)에게 맡길 때 사용하는 지시서입니다.
> 작업 전 이 문서를 먼저 읽고, 불명확한 부분은 추측하지 말고 질문하세요.

---

## 0. 프로젝트 개요

**Hypo Loop**는 사용자가 등록한 "가설"을 ML 실험으로 자동 검증하는 Auto Research Agent 플랫폼이다.
백엔드는 **데이터 계층 관리 + YML 파일 생성 + 트리거**를 담당한다. 실제 ML 학습은 별도 에이전트(AI 팀)가 수행한다.

전체 데이터 계층:

```
u_id (사용자)
└── project_id (프로젝트)
    ├── 프로젝트 로컬 db (SQLite)
    └── 가설_id (가설)
        ├── u_id_가설_id.yml   ← 백엔드가 생성
        └── exp_id (실험)
            ├── exp_id.yml      ← 에이전트(AI팀)가 생성
            └── 에이전트가 생성한 학습용 기능코드  ← 에이전트 영역
```

---

## 1. 백엔드 책임 범위 (Scope)

### 담당 O
- `u_id / project_id / 가설_id / exp_id` 식별자 계층 관리
- 프로젝트별 로컬 SQLite DB 생성·연결·경로 정규화
- YML 파일 생성
  - `u_id_가설_id.yml` : 가설 메타데이터 (백엔드 전용 생성 대상)
- **트리거**: 가설 yml 생성이 끝나면 해당 yml에 `ready` 플래그를 세팅 → 에이전트가 이를 감지/호출
- DB 저장 항목
  - 가설 내용
  - 실험 횟수 (병렬 횟수, 최대 길이 제한)
  - 가설별 점수 (`가설_id` + `exp_id` 조합, 초기엔 비어있음)
- 보고서용 데이터 제공 API
  - 가설별 최고점
  - 가설별 실험 그래프용 데이터 (실험별 점수 추이)
  - 실험 결과 분석 텍스트(에이전트가 채운 값 전달)

### 담당 X (경계)
- 실제 ML 트레인 코드 작성 → **에이전트(AI 팀)**
- `exp_id.yml` (실험 설계 명세) 생성 → **에이전트(AI 팀)**
- 실험 설계 내용(피처/하이퍼파라미터/모델/수식) 산출 → 에이전트
- eda / 재실험 분기 로직 → 에이전트
- 프론트엔드 화면 → **프론트 담당**

> ⚠️ 경계가 모호한 작업(예: yml 스키마 필드 추가)은 임의 결정하지 말고 팀 질문으로 남길 것.

---

## 2. 기술 스택

- 언어: Python 3.11+
- 웹 프레임워크: FastAPI
- DB: SQLite (프로젝트별 분리, 파일 기반)
- ORM/드라이버: SQLAlchemy 또는 sqlite3 (팀 컨벤션 따름 — 미정 시 질문)
- 파일 포맷: YAML (PyYAML)

---

## 3. 디렉토리 구조 (백엔드)

```
backend/
├── app/
│   ├── main.py                 # FastAPI 엔트리포인트
│   ├── api/
│   │   ├── projects.py         # 프로젝트 CRUD
│   │   ├── hypotheses.py       # 가설 CRUD
│   │   └── experiments.py      # 실험(exp) CRUD
│   ├── services/
│   │   ├── yml_generator.py    # u_id_가설_id.yml 생성 (exp_id.yml은 에이전트 담당)
│   │   ├── trigger.py          # ready 플래그 세팅 → 에이전트 호출
│   │   └── report_builder.py   # 최고점 / 그래프 데이터 / 분석 텍스트 집계
│   ├── db/
│   │   ├── models.py           # 스키마 정의
│   │   ├── crud.py             # DB 입출력
│   │   └── session.py          # 프로젝트별 DB 연결 관리
│   └── core/
│       └── path_utils.py       # DB/파일 경로 정규화
└── requirements.txt
```

---

## 4. DB 스키마 (초안)

> 아래는 이미지 기반 초안. 확정 전 팀 리뷰 필요.

**hypotheses**
| 컬럼 | 타입 | 설명 |
|------|------|------|
| 가설_id | TEXT (PK) | 가설 식별자 |
| project_id | TEXT (FK) | 소속 프로젝트 |
| u_id | TEXT | 작성 사용자 |
| content | TEXT | 가설 내용 |
| max_experiments | INTEGER | 실험 최대 횟수(길이 제한) |
| parallel_count | INTEGER | 병렬 실험 횟수 |
| created_at | DATETIME | 생성 시각 |

**experiments**
| 컬럼 | 타입 | 설명 |
|------|------|------|
| exp_id | TEXT (PK) | 실험 식별자 |
| 가설_id | TEXT (FK) | 소속 가설 |
| score | REAL (nullable) | 가설별 점수 (초기 NULL) |
| status | TEXT | ready / running / done / failed |
| analysis_text | TEXT (nullable) | 실험 결과 분석 텍스트(에이전트 작성) |
| created_at | DATETIME | 생성 시각 |

---

## 5. YML 파일 스펙

### `u_id_가설_id.yml` (가설 메타 — **백엔드가 생성**)
```yaml
u_id: <string>
project_id: <string>
hypothesis_id: <string>
content: <가설 내용>
max_experiments: <int>      # 최대 길이 제한
parallel_count: <int>       # 병렬 횟수
ready: false                # 트리거가 true로 변경
```

### `exp_id.yml` (실험 설계 — **에이전트(AI팀)가 생성**, 참고용)
> 백엔드는 이 파일을 **만들지 않는다.** 아래는 에이전트가 만들 산출물 형태를
> 백엔드가 이해하기 위한 참고 스펙일 뿐이다. 백엔드는 이 파일을 읽기만 할 수 있다.
```yaml
hypothesis_id: <string>
exp_id: <string>
design:
  features: []              # 피처
  hyperparameters: {}       # 하이퍼파라미터
  model: <string>           # 모델
  formula: <string>         # 산식/수식
```

---

## 6. 주요 API 엔드포인트 (초안)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | `/projects` | 프로젝트 생성 + 로컬 DB 초기화 |
| POST | `/projects/{project_id}/hypotheses` | 가설 등록 → `u_id_가설_id.yml` 생성 |
| POST | `/hypotheses/{가설_id}/ready` | 트리거: ready 세팅 → 에이전트 호출 |
| POST | `/hypotheses/{가설_id}/experiments` | exp 레코드 생성 (DB 등록만, yml은 에이전트가 작성) |
| PATCH | `/experiments/{exp_id}` | 점수/분석 텍스트 업데이트(에이전트 콜백) |
| GET | `/hypotheses/{가설_id}/report` | 최고점 + 그래프 데이터 + 분석 텍스트 |

---

## 7. 작업 규칙 (AI에게 주는 지시)

1. **이 문서의 Scope를 벗어나는 작업은 하지 말 것.** 특히 ML 학습/실험 설계 로직은 건드리지 않는다.
2. 스키마·API 경로·필드명은 위 초안을 따르되, **추가·변경이 필요하면 코드로 밀어붙이지 말고 질문**한다.
3. 모든 함수에 타입 힌트와 docstring을 단다.
4. DB 경로는 반드시 `path_utils.py`를 통해 정규화한다(직접 문자열 결합 금지).
5. YML 생성/수정은 `yml_generator.py`에 모은다. 다른 모듈에서 직접 yaml.dump 하지 않는다. **단, `exp_id.yml`은 에이전트 산출물이므로 백엔드는 읽기만 하고 절대 생성·수정하지 않는다.**
6. 커밋은 작은 단위로, 기능별로 나눈다. (`feat:`, `fix:`, `chore:` 컨벤션)
7. main 직접 push 대신 feature 브랜치 + PR로 올린다.

---

## 8. 우선순위 (구현 순서 제안)

1. `db/session.py` + `core/path_utils.py` — DB 연결·경로 기반 다지기
2. `db/models.py` + `db/crud.py` — 스키마와 입출력
3. `services/yml_generator.py` — YML 생성
4. `api/projects.py`, `api/hypotheses.py` — 등록 플로우
5. `services/trigger.py` — ready 트리거
6. `api/experiments.py` + 콜백(PATCH) — 점수/분석 수신
7. `services/report_builder.py` + `/report` — 보고서 데이터

---

## 9. 열린 질문 (팀 확정 필요)

- [ ] ORM은 SQLAlchemy vs sqlite3 직접 사용 중 무엇으로?
- [ ] 트리거 방식: yml `ready` 폴링 vs 직접 API 호출 vs 메시지 큐?
- [ ] `parallel_count` 병렬 실행 주체가 백엔드인지 에이전트인지?
- [ ] 에이전트가 점수/분석을 돌려주는 방식: 콜백 API vs yml 파일 갱신?
- [ ] 프로젝트별 DB 파일 저장 경로 루트는 어디로 고정?
