"""DataLayerBackend(실제 백엔드 데이터 계층 연동) 테스트.

hypoloop 패키지가 import 가능할 때만 실행(미설치 시 자동 skip).
"""
import os
import tempfile

import pandas as pd
import pytest

pytest.importorskip("hypoloop")  # hypoloop 없으면 이 파일 전체 skip

from backend.interface import (  # noqa: E402
    DataCard, PipelineInput, PipelineBackend, MetricRecord, PIPELINE_STAGES,
)
from backend.data_layer_backend import DataLayerBackend  # noqa: E402


@pytest.fixture
def csv_path():
    df = pd.DataFrame({"Pclass": [1, 3, 2, 1], "Survived": [1, 0, 1, 1]})
    fd, path = tempfile.mkstemp(suffix=".csv")
    os.close(fd)
    df.to_csv(path, index=False)
    yield path
    os.remove(path)


def make_input(csv_path, loop_count=3, task="classification", target="Survived"):
    card = DataCard(target_column=target, task_type=task, description="t")
    return PipelineInput(csv_path=csv_path, loop_count=loop_count,
                         data_card=card, hypothesis="Pclass 영향 가설")


def test_satisfies_protocol():
    assert isinstance(DataLayerBackend(), PipelineBackend)


def test_validate_missing_target(csv_path):
    errors = DataLayerBackend().validate_input(make_input(csv_path, target="없음"))
    assert any("없음" in e for e in errors)


def test_run_streams_all_stages(csv_path):
    backend = DataLayerBackend()
    events = list(backend.run(make_input(csv_path, loop_count=2)))
    seen = {e.stage for e in events}
    for stage in PIPELINE_STAGES:
        assert stage in seen
    assert events[-1].status == "done"


def test_result_metrics_come_from_backend_db(csv_path):
    backend = DataLayerBackend()
    list(backend.run(make_input(csv_path, loop_count=3)))
    res = backend.get_result()
    # 베이스라인 + 3루프 = 4개의 MetricRecord 가 SQLite experiment_log 에서 조회됨
    assert len(res.metrics_history) == 4
    assert all(isinstance(m, MetricRecord) for m in res.metrics_history)
    assert [m.loop_index for m in res.metrics_history] == [0, 1, 2, 3]
    # 백엔드 writer 가 만든 yml 이 들어있음
    assert "metric:" in res.experiment_yaml
    assert "SQLite" in res.report_md


def test_run_resets_log_between_runs(csv_path):
    backend = DataLayerBackend()
    list(backend.run(make_input(csv_path, loop_count=2)))
    list(backend.run(make_input(csv_path, loop_count=2)))  # 두 번째 실행
    res = backend.get_result()
    # 누적되지 않고 2루프+베이스라인 = 3개만
    assert len(res.metrics_history) == 3


def test_get_result_before_run_raises():
    with pytest.raises(RuntimeError):
        DataLayerBackend().get_result()
