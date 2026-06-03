import pandas as pd

from ui.input_form import infer_task_type, build_pipeline_input
from backend.interface import PipelineInput


def test_infer_task_type_binary_is_classification():
    s = pd.Series([0, 1, 1, 0, 1])
    assert infer_task_type(s) == "classification"


def test_infer_task_type_continuous_is_regression():
    s = pd.Series([1.2, 3.4, 5.6, 7.8, 9.1, 2.2, 4.5, 6.7, 8.9, 0.1, 11.0])
    assert infer_task_type(s) == "regression"


def test_infer_task_type_string_is_classification():
    s = pd.Series(["a", "b", "a", "c"])
    assert infer_task_type(s) == "classification"


def test_build_pipeline_input_shape():
    inp = build_pipeline_input(
        csv_path="/tmp/x.csv", loop_count=3, target_column="y",
        task_type="regression", description="d", llm_instruction="가설",
    )
    assert isinstance(inp, PipelineInput)
    assert inp.loop_count == 3
    assert inp.data_card.task_type == "regression"
