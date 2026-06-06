"""FastAPI 참조 서버 — 잡 제출/폴링/결과 엔드포인트."""
from __future__ import annotations

import os
from typing import Callable, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from backend.interface import PipelineInput, PipelineBackend
from backend.mock import MockBackend
from api import schema
from api.job_store import JobStore


def _is_safe_csv_path(csv_path: str) -> bool:
    """csv_path가 작업 디렉터리 안쪽인지 확인(경로 탈출/임의 파일 읽기 방지)."""
    base = os.path.realpath(os.getcwd())
    target = os.path.realpath(csv_path)
    return target == base or target.startswith(base + os.sep)


def create_app(backend_factory: Optional[Callable[[], PipelineBackend]] = None) -> FastAPI:
    if backend_factory is None:
        backend_factory = MockBackend
    store = JobStore(backend_factory)
    app = FastAPI(title="hypoloop API")

    def _parse_input(payload: dict) -> PipelineInput:
        try:
            return schema.input_from_dict(payload)
        except (KeyError, TypeError) as exc:
            raise HTTPException(status_code=400, detail=f"잘못된 요청 형식: {exc}")

    def _validate(inp: PipelineInput):
        if not _is_safe_csv_path(inp.csv_path):
            return ["csv_path가 허용된 작업 디렉터리를 벗어났습니다."]
        return store.validate(inp)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.post("/validate")
    def validate(payload: dict):
        return {"errors": _validate(_parse_input(payload))}

    @app.post("/jobs", status_code=201)
    def create_job(payload: dict):
        inp = _parse_input(payload)
        errors = _validate(inp)
        if errors:
            return JSONResponse(status_code=400, content={"errors": errors})
        return {"job_id": store.submit(inp)}

    @app.get("/jobs/{job_id}/events")
    def get_events(job_id: str, after: int = 0):
        res = store.get_events(job_id, after)
        if res is None:
            raise HTTPException(status_code=404, detail="job not found")
        return res

    @app.get("/jobs/{job_id}/result")
    def get_result(job_id: str):
        status, payload = store.get_result(job_id)
        if status == "not_found":
            raise HTTPException(status_code=404, detail="job not found")
        if status == "not_ready":
            raise HTTPException(status_code=409, detail="job not done")
        if status == "failed":
            return JSONResponse(status_code=500, content={"error": payload})
        return payload

    return app


app = create_app()
