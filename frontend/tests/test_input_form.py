import pandas as pd

from ui.input_form import (
    infer_task_type, build_pipeline_input, column_template, metric_options,
)
from backend.interface import PipelineInput


def test_metric_options_classification():
    opts = metric_options("classification")
    assert opts[0] == "accuracy"
    assert "f1" in opts and "roc_auc" in opts
    assert "rmse" not in opts


def test_metric_options_regression():
    opts = metric_options("regression")
    assert opts[0] == "rmse"
    assert "mae" in opts and "r2" in opts
    assert "accuracy" not in opts


def test_infer_task_type_binary_is_classification():
    s = pd.Series([0, 1, 1, 0, 1])
    assert infer_task_type(s) == "classification"


def test_infer_task_type_continuous_is_regression():
    s = pd.Series([1.2, 3.4, 5.6, 7.8, 9.1, 2.2, 4.5, 6.7, 8.9, 0.1, 11.0])
    assert infer_task_type(s) == "regression"


def test_infer_task_type_string_is_classification():
    s = pd.Series(["a", "b", "a", "c"])
    assert infer_task_type(s) == "classification"


def test_column_template_one_line_per_column():
    assert column_template(["Survived", "Pclass"]) == "Survived : \nPclass : \n"


def test_column_template_empty():
    assert column_template([]) == ""


def test_build_pipeline_input_shape():
    inp = build_pipeline_input(
        csv_path="/tmp/x.csv", loop_count=3, target_column="y",
        task_type="regression", description="Survived : 생존",
        hypothesis="가설", metric="rmse",
    )
    assert isinstance(inp, PipelineInput)
    assert inp.hypothesis == "가설"
    assert inp.metric == "rmse"
    assert inp.data_card.description == "Survived : 생존"


def test_build_pipeline_input_metric_optional():
    inp = build_pipeline_input(
        csv_path="/tmp/x.csv", loop_count=1, target_column="y",
        task_type="classification", description="d", hypothesis="가설",
    )
    assert inp.metric == ""
