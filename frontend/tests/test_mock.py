import os
import tempfile

import pandas as pd
import pytest

from backend.interface import (
    DataCard, PipelineInput, PipelineBackend, PIPELINE_STAGES,
)
from backend.mock import MockBackend


@pytest.fixture
def csv_path():
    df = pd.DataFrame({"Pclass": [1, 3, 2], "Survived": [1, 0, 1]})
    fd, path = tempfile.mkstemp(suffix=".csv")
    os.close(fd)
    df.to_csv(path, index=False)
    yield path
    os.remove(path)


def make_input(csv_path, loop_count=2, target="Survived"):
    card = DataCard(target_column=target, task_type="classification",
                    description="테스트")
    return PipelineInput(csv_path=csv_path, loop_count=loop_count,
                         data_card=card, hypothesis="가설 검증")


def test_mock_satisfies_protocol():
    assert isinstance(MockBackend(), PipelineBackend)


def test_validate_ok(csv_path):
    errors = MockBackend().validate_input(make_input(csv_path))
    assert errors == []


def test_validate_missing_target(csv_path):
    errors = MockBackend().validate_input(make_input(csv_path, target="없는컬럼"))
    assert len(errors) == 1
    assert "없는컬럼" in errors[0]


def test_validate_bad_loop_count(csv_path):
    errors = MockBackend().validate_input(make_input(csv_path, loop_count=0))
    assert any("루프" in e for e in errors)


def test_run_streams_events_in_stage_order(csv_path):
    backend = MockBackend()
    events = list(backend.run(make_input(csv_path, loop_count=2)))
    assert len(events) > 0
    seen_stages = [e.stage for e in events]
    for stage in PIPELINE_STAGES:
        assert stage in seen_stages
    assert events[-1].status == "done"


def test_get_result_after_run(csv_path):
    backend = MockBackend()
    list(backend.run(make_input(csv_path, loop_count=3)))
    res = backend.get_result()
    assert res.report_md.startswith("#")
    assert "def " in res.final_code or "import" in res.final_code
    assert len(res.metrics_history) >= 1
    assert res.experiment_yaml != ""


def test_get_result_before_run_raises():
    with pytest.raises(RuntimeError):
        MockBackend().get_result()


def test_final_code_uses_classifier_for_classification(csv_path):
    backend = MockBackend()
    list(backend.run(make_input(csv_path)))  # task_type="classification"
    assert "RandomForestClassifier" in backend.get_result().final_code


def test_final_code_uses_regressor_for_regression(csv_path):
    card = DataCard(target_column="Survived", task_type="regression",
                    description="t")
    inp = PipelineInput(csv_path=csv_path, loop_count=2, data_card=card,
                        hypothesis="가설")
    backend = MockBackend()
    list(backend.run(inp))
    code = backend.get_result().final_code
    assert "RandomForestRegressor" in code
    assert "RandomForestClassifier" not in code
