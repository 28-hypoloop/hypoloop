import time

from backend.mock import MockBackend
from backend.interface import DataCard, PipelineInput
from api.job_store import JobStore


def make_inp(loop_count=2):
    return PipelineInput("sample_data/sample.csv", loop_count,
                         DataCard("Survived", "classification", "t"), "가설")


def _wait_done(store, job_id, tries=300):
    for _ in range(tries):
        res = store.get_events(job_id, 0)
        if res["status"] in ("done", "failed"):
            return res
        time.sleep(0.01)
    return res


def test_job_completes_with_events_and_result():
    store = JobStore(lambda: MockBackend(step_delay=0.0))
    job_id = store.submit(make_inp())
    res = _wait_done(store, job_id)
    assert res["status"] == "done"
    assert len(res["events"]) > 0
    status, result = store.get_result(job_id)
    assert status == "ok"
    assert result["report_md"].startswith("#")


def test_get_events_incremental():
    store = JobStore(lambda: MockBackend(step_delay=0.0))
    job_id = store.submit(make_inp())
    _wait_done(store, job_id)
    first = store.get_events(job_id, 0)
    again = store.get_events(job_id, first["next"])
    assert again["events"] == []
    assert again["next"] == first["next"]


def test_unknown_job():
    store = JobStore(lambda: MockBackend())
    assert store.get_events("nope", 0) is None
    assert store.get_result("nope")[0] == "not_found"


def test_validate_delegates():
    store = JobStore(lambda: MockBackend())
    bad = PipelineInput("sample_data/sample.csv", 0,
                        DataCard("Survived", "classification", "t"), "가설")
    errors = store.validate(bad)
    assert any("루프" in e for e in errors)
