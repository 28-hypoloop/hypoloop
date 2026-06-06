import sqlite3

import pandas as pd
import pytest

from hypoloop.data.loader import (
    _normalize_db_path,
    append_experiment_log,
    load_csv,
    query_metric_records,
)


def test_load_csv_returns_row_count(sample_csv, db_path):
    count = load_csv(sample_csv, db_path, "raw_data")
    assert count == 3


def test_load_csv_replace_overwrites(sample_csv, db_path):
    load_csv(sample_csv, db_path, "raw_data")
    load_csv(sample_csv, db_path, "raw_data")
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute("SELECT COUNT(*) FROM raw_data").fetchone()[0]
    assert rows == 3


def test_load_csv_column_types_preserved(sample_csv, db_path):
    load_csv(sample_csv, db_path, "raw_data")
    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql_query("SELECT * FROM raw_data", conn)
    assert list(df.columns) == ["a", "b", "c"]
    assert df["a"].tolist() == [1, 4, 7]


def test_append_experiment_log_accumulates(db_path):
    record1 = {"loop_index": 0, "metric_name": "accuracy", "baseline": 0.7, "value": 0.75}
    record2 = {"loop_index": 1, "metric_name": "accuracy", "baseline": 0.7, "value": 0.80}
    append_experiment_log(record1, db_path)
    append_experiment_log(record2, db_path)
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute("SELECT COUNT(*) FROM experiment_log").fetchone()[0]
    assert rows == 2


def test_query_metric_records_returns_all(db_path):
    for i in range(3):
        append_experiment_log(
            {"loop_index": i, "metric_name": "f1", "baseline": 0.5, "value": 0.5 + i * 0.1},
            db_path,
        )
    records = query_metric_records(db_path)
    assert len(records) == 3
    assert all(set(r.keys()) == {"loop_index", "metric_name", "baseline", "value"} for r in records)


def test_query_metric_records_filter_by_loop(db_path):
    for i in range(3):
        append_experiment_log(
            {"loop_index": i, "metric_name": "accuracy", "baseline": 0.6, "value": 0.6 + i * 0.05},
            db_path,
        )
    records = query_metric_records(db_path, loop_index=1)
    assert len(records) == 1
    assert records[0]["loop_index"] == 1


def test_query_metric_records_empty_when_no_db(tmp_path):
    result = query_metric_records(tmp_path / "nonexistent.db")
    assert result == []


def test_normalize_db_path_stays_under_data(tmp_path, monkeypatch):
    import hypoloop.data.loader as loader_mod
    monkeypatch.setattr(loader_mod, "_PROJECT_ROOT", tmp_path)
    (tmp_path / "data").mkdir()
    result = _normalize_db_path("experiment.db")
    assert result.parent == (tmp_path / "data").resolve()
