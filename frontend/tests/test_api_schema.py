from backend.interface import (
    DataCard, PipelineInput, ProgressEvent, MetricRecord, PipelineResult,
)
from api import schema


def test_metric_roundtrip():
    m = MetricRecord(1, "accuracy", 0.7, 0.82)
    assert schema.metric_from_dict(schema.metric_to_dict(m)) == m


def test_metric_none():
    assert schema.metric_to_dict(None) is None
    assert schema.metric_from_dict(None) is None


def test_input_roundtrip():
    inp = PipelineInput("a.csv", 3, DataCard("y", "classification", "d"), "가설")
    assert schema.input_from_dict(schema.input_to_dict(inp)) == inp


def test_event_roundtrip_with_metric():
    m = MetricRecord(0, "accuracy", 0.7, 0.7)
    ev = ProgressEvent("베이스라인", 0, "running", "m", kind="metric", metric=m)
    assert schema.event_from_dict(schema.event_to_dict(ev)) == ev


def test_event_roundtrip_plain():
    ev = ProgressEvent("EDA", 0, "done", "done")
    out = schema.event_from_dict(schema.event_to_dict(ev))
    assert out == ev and out.kind == "stage" and out.metric is None


def test_result_roundtrip():
    r = PipelineResult("# r", "code", [MetricRecord(0, "accuracy", 0.7, 0.7)], "yaml")
    assert schema.result_from_dict(schema.result_to_dict(r)) == r
