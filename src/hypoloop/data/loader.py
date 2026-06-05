from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

_PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _normalize_db_path(db_path: str | Path) -> Path:
    p = Path(db_path)
    data_dir = _PROJECT_ROOT / "storage" / "data"
    if not p.is_absolute() and "data" not in p.parts and "storage" not in p.parts:
        p = data_dir / p.name
    p = p.resolve()
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def load_csv(csv_path: str | Path, db_path: str | Path, table_name: str) -> int:
    """CSV를 읽어 SQLite 테이블에 replace 모드로 적재. 적재된 행 수를 반환한다."""
    df = pd.read_csv(csv_path)
    target = _normalize_db_path(db_path)
    with sqlite3.connect(target) as conn:
        df.to_sql(table_name, conn, if_exists="replace", index=False)
    return len(df)


def append_experiment_log(record: dict, db_path: str | Path) -> None:
    """실험 결과를 experiment_log 테이블에 append 모드로 적재한다.

    record 필수 키: loop_index, metric_name, baseline, value

    # TODO: experiment_log 컬럼명이 UI MetricRecord(loop_index/metric_name/baseline/value)와
    #       1:1로 맞는지 팀 합의 확인 필요
    """
    df = pd.DataFrame([record])
    target = _normalize_db_path(db_path)
    with sqlite3.connect(target) as conn:
        df.to_sql("experiment_log", conn, if_exists="append", index=False)


def query_metric_records(
    db_path: str | Path,
    loop_index: int | None = None,
) -> list[dict]:
    """experiment_log 테이블에서 MetricRecord 형식으로 행을 조회한다.

    반환 형식: [{"loop_index": int, "metric_name": str, "baseline": float, "value": float}, ...]
    PipelineResult.metrics_history 에 바로 사용할 수 있다.
    """
    target = _normalize_db_path(db_path)
    if not target.exists():
        return []

    with sqlite3.connect(target) as conn:
        if loop_index is None:
            query = "SELECT loop_index, metric_name, baseline, value FROM experiment_log"
            df = pd.read_sql_query(query, conn)
        else:
            query = (
                "SELECT loop_index, metric_name, baseline, value "
                "FROM experiment_log WHERE loop_index = ?"
            )
            df = pd.read_sql_query(query, conn, params=(loop_index,))

    df["loop_index"] = df["loop_index"].astype(int)
    df["baseline"] = df["baseline"].astype(float)
    df["value"] = df["value"].astype(float)
    return df.to_dict(orient="records")
