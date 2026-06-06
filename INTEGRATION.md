# 통합 실행 가이드 (frontend × data-layer)

이 브랜치는 **프론트엔드(UI)** 와 **백엔드 데이터 계층(`hypoloop`)** 을 합쳐
실제로 동작하는 버전입니다.

## 무엇이 연결됐나

프론트엔드는 `PipelineBackend` 계약에만 의존하고, 그 구현으로
`frontend/backend/data_layer_backend.py`(어댑터)가 **실제 `hypoloop` 데이터 계층**을
사용합니다.

| 단계 | 실제 백엔드 기능 사용 |
| --- | --- |
| 베이스라인 | `hypoloop.data.loader.load_csv` → CSV를 SQLite(`raw_data`)에 적재 |
| 루프마다 | `append_experiment_log` → 실험 지표를 SQLite(`experiment_log`)에 적재 |
| 리포트 | `query_metric_records` → 지표 조회 후 UI `MetricRecord`로 변환 |
| 리포트 | `write_experiment_yml` → 실험 yml 생성 후 `PipelineResult.experiment_yaml`로 |

> ⚠️ **모델 학습/평가(LangGraph 에이전트)는 아직 미구현**입니다. 그래서 지표 *값* 은
> 임시(placeholder)이고, 리포트에도 그 사실을 명시합니다. 데이터 적재·실험로그·yml
> 생성은 전부 실제 백엔드 기능입니다.

`hypoloop`을 import할 수 없으면 어댑터 대신 `MockBackend`로 자동 폴백하므로,
프론트엔드만 단독으로도 실행됩니다.

## 실행 방법

```bash
# 1) 백엔드(hypoloop) 설치 — 이걸 해야 실제 데이터 계층을 사용
pip install -e .

# 2) 프론트엔드 의존성 설치
pip install -r frontend/requirements.txt

# 3) 앱 실행
cd frontend
streamlit run app.py        # http://localhost:8501
```

1번을 건너뛰면 앱은 그대로 뜨지만 `MockBackend`로 동작합니다(가짜 데이터).

## 테스트

```bash
# 백엔드 데이터 계층
pip install -e ".[dev]"
pytest tests/                       # 17개

# 프론트엔드 (+ 통합 어댑터)
cd frontend && pytest               # 29개 (hypoloop 설치 시 어댑터 테스트 포함)
```

## 구조

```
src/hypoloop/data/        # 백엔드 데이터 계층 (load_csv, experiment_log, yml)
tests/                    # 백엔드 테스트
frontend/                 # Streamlit UI
  backend/interface.py    # UI↔백엔드 계약 (PipelineBackend)
  backend/data_layer_backend.py   # ★ hypoloop를 계약에 연결하는 어댑터
  backend/mock.py         # 폴백용 Mock
  app.py                  # get_backend(): hypoloop 있으면 어댑터, 없으면 Mock
data/                     # 런타임 산출물(SQLite 등, gitignore)
```

## 다음 단계

학습/평가 계층이 생기면, 어댑터의 임시 지표 계산 부분을 실제 학습 호출로 교체하면
됩니다. UI·데이터 계층 계약은 그대로 유지됩니다.
