"""ApiBackend — HTTP API를 통해 PipelineBackend 계약을 구현하는 프론트 클라이언트."""
from __future__ import annotations

import time
from typing import Iterator, List, Optional

import httpx

from backend.interface import PipelineInput, ProgressEvent, PipelineResult
from api import schema

_POLL_INTERVAL = 0.3


class ApiBackend:
    """run()/get_result()/validate_input()을 HTTP 호출로 수행. 대시보드는 그대로 사용."""

    def __init__(self, base_url: str, client: Optional[httpx.Client] = None,
                 poll_interval: float = _POLL_INTERVAL) -> None:
        self._base = base_url.rstrip("/")
        self._client = client or httpx.Client(base_url=self._base, timeout=30.0)
        self._poll = poll_interval
        self._job_id: Optional[str] = None

    def validate_input(self, inp: PipelineInput) -> List[str]:
        r = self._client.post("/validate", json=schema.input_to_dict(inp))
        r.raise_for_status()
        return r.json()["errors"]

    def run(self, inp: PipelineInput) -> Iterator[ProgressEvent]:
        r = self._client.post("/jobs", json=schema.input_to_dict(inp))
        # 검증 실패(400)는 errors를 담은 RuntimeError로 먼저 처리하고,
        # 그 외 HTTP 에러만 raise_for_status로 표면화한다.
        if r.status_code == 400:
            raise RuntimeError("입력 검증 실패: " + "; ".join(r.json().get("errors", [])))
        r.raise_for_status()
        self._job_id = r.json()["job_id"]
        after = 0
        while True:
            er = self._client.get(f"/jobs/{self._job_id}/events",
                                  params={"after": after})
            er.raise_for_status()
            data = er.json()
            for ev in data["events"]:
                yield schema.event_from_dict(ev)
            after = data["next"]
            if data["status"] == "failed":
                raise RuntimeError("백엔드 작업이 실패했습니다.")
            if data["status"] == "done":
                break
            time.sleep(self._poll)

    def get_result(self) -> PipelineResult:
        if self._job_id is None:
            raise RuntimeError("run()을 먼저 실행해야 결과를 얻을 수 있습니다.")
        r = self._client.get(f"/jobs/{self._job_id}/result")
        if r.status_code != 200:
            # 실패(500)·미완료(409) 등은 httpx 예외 대신 RuntimeError로 일관 처리
            try:
                body = r.json()
            except Exception:  # noqa: BLE001
                body = {}
            msg = body.get("error") or body.get("detail") or ""
            raise RuntimeError(f"결과 조회 실패({r.status_code}): {msg}")
        return schema.result_from_dict(r.json())
