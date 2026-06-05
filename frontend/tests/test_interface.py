from backend.interface import (
    DataCard, PipelineInput, ProgressEvent, MetricRecord,
    PipelineResult, PIPELINE_STAGES,
)


def test_datacard_fields():
    card = DataCard(target_column="Survived", task_type="classification",
                    description="타이타닉")
    assert card.target_column == "Survived"
    assert card.task_type == "classification"


def test_pipeline_input_fields():
    card = DataCard(target_column="y", task_type="regression", description="d")
    inp = PipelineInput(csv_path="/tmp/a.csv", loop_count=3,
                        data_card=card, hypothesis="가설", metric="rmse")
    assert inp.loop_count == 3
    assert inp.hypothesis == "가설"
    assert inp.metric == "rmse"


def test_pipeline_input_metric_default():
    card = DataCard(target_column="y", task_type="regression", description="d")
    inp = PipelineInput(csv_path="/tmp/a.csv", loop_count=1,
                        data_card=card, hypothesis="가설")
    assert inp.metric == ""


def test_progress_event_fields():
    ev = ProgressEvent(stage="EDA", loop_index=0, status="running", message="시작")
    assert ev.stage == "EDA"
    assert ev.status == "running"


def test_metric_record_delta():
    m = MetricRecord(loop_index=1, metric_name="accuracy", baseline=0.7, value=0.82)
    assert round(m.value - m.baseline, 2) == 0.12


def test_pipeline_result_fields():
    res = PipelineResult(report_md="# r", final_code="print(1)",
                         metrics_history=[], experiment_yaml="a: 1")
    assert res.report_md == "# r"
    assert res.metrics_history == []


def test_pipeline_stages_order():
    assert PIPELINE_STAGES[0] == "계획수립"
    assert "베이스라인" in PIPELINE_STAGES
    assert PIPELINE_STAGES[-1] == "리포트"


def test_progress_event_new_fields_default():
    ev = ProgressEvent(stage="EDA", loop_index=0, status="running", message="m")
    assert ev.kind == "stage"
    assert ev.detail == ""
    assert ev.metric is None


def test_progress_event_metric_kind():
    from backend.interface import MetricRecord
    m = MetricRecord(loop_index=1, metric_name="accuracy", baseline=0.7, value=0.8)
    ev = ProgressEvent(stage="튜닝", loop_index=1, status="running",
                       message="지표", kind="metric", metric=m)
    assert ev.kind == "metric"
    assert ev.metric.value == 0.8
