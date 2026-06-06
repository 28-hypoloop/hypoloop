import pytest
from fastapi.testclient import TestClient

from api.server import create_app
from backend.mock import MockBackend
from backend.api_backend import ApiBackend
from backend.interface import DataCard, PipelineInput, PIPELINE_STAGES


def _backend():
    app = create_app(backend_factory=lambda: MockBackend(step_delay=0.0))
    client = TestClient(app)
    return ApiBackend("http://testserver", client=client, poll_interval=0.0)


def _inp(loop_count=2, target="Survived"):
    return PipelineInput("sample_data/sample.csv", loop_count,
                         DataCard(target, "classification", "t"), "가설")


def test_run_yields_events_all_stages():
    events = list(_backend().run(_inp()))
    seen = {e.stage for e in events}
    for s in PIPELINE_STAGES:
        assert s in seen
    kinds = {e.kind for e in events}
    assert "metric" in kinds and "llm" in kinds


def test_get_result_after_run():
    b = _backend()
    list(b.run(_inp(loop_count=2)))
    res = b.get_result()
    assert res.report_md.startswith("#")
    assert len(res.metrics_history) == 3   # baseline + 2 loops


def test_validate_input_errors():
    errs = _backend().validate_input(_inp(loop_count=0))
    assert any("루프" in e for e in errs)


def test_get_result_before_run_raises():
    with pytest.raises(RuntimeError):
        _backend().get_result()


def test_run_raises_on_validation_error():
    with pytest.raises(RuntimeError):
        list(_backend().run(_inp(loop_count=0)))


def test_run_raises_on_failed_job():
    from backend.interface import ProgressEvent

    class _Failing:
        def validate_input(self, inp):
            return []

        def run(self, inp):
            yield ProgressEvent("계획수립", 0, "running", "start")
            raise RuntimeError("boom")

        def get_result(self):
            raise RuntimeError("no result")

    app = create_app(backend_factory=lambda: _Failing())
    b = ApiBackend("http://testserver", client=TestClient(app), poll_interval=0.0)
    with pytest.raises(RuntimeError):
        list(b.run(_inp()))
