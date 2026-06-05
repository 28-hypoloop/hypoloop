import time

from fastapi.testclient import TestClient

from api.server import create_app
from backend.mock import MockBackend

INPUT = {
    "csv_path": "sample_data/sample.csv", "loop_count": 2,
    "data_card": {"target_column": "Survived", "task_type": "classification",
                  "description": "t"},
    "llm_instruction": "가설",
}


def _client():
    return TestClient(create_app(backend_factory=lambda: MockBackend(step_delay=0.0)))


def test_health():
    assert _client().get("/health").json()["status"] == "ok"


def test_job_lifecycle():
    c = _client()
    r = c.post("/jobs", json=INPUT)
    assert r.status_code == 201
    jid = r.json()["job_id"]
    after, status = 0, "running"
    for _ in range(400):
        e = c.get(f"/jobs/{jid}/events", params={"after": after}).json()
        after, status = e["next"], e["status"]
        if status in ("done", "failed"):
            break
        time.sleep(0.01)
    assert status == "done"
    res = c.get(f"/jobs/{jid}/result")
    assert res.status_code == 200
    assert res.json()["report_md"].startswith("#")


def test_validate_endpoint_reports_missing_target():
    c = _client()
    bad = {**INPUT, "data_card": {**INPUT["data_card"], "target_column": "없는컬럼"}}
    errors = c.post("/validate", json=bad).json()["errors"]
    assert any("없는컬럼" in e for e in errors)


def test_create_job_validation_400():
    c = _client()
    r = c.post("/jobs", json={**INPUT, "loop_count": 0})
    assert r.status_code == 400
    assert any("루프" in e for e in r.json()["errors"])


def test_unknown_job_404():
    assert _client().get("/jobs/nope/events").status_code == 404


def test_unsafe_csv_path_rejected():
    c = _client()
    bad = {**INPUT, "csv_path": "/etc/passwd"}
    errors = c.post("/validate", json=bad).json()["errors"]
    assert any("작업 디렉터리" in e for e in errors)
    assert c.post("/jobs", json=bad).status_code == 400


def test_malformed_payload_400():
    # 필수 키 누락 → 500이 아닌 400
    assert _client().post("/jobs", json={"loop_count": 2}).status_code == 400
