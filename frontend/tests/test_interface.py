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
                        data_card=card, llm_instruction="가설")
    assert inp.loop_count == 3
    assert inp.data_card.target_column == "y"


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
