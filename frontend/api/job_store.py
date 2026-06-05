"""인메모리 잡 스토어 — 백그라운드 스레드로 파이프라인을 실행하고 이벤트를 적재."""
from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

from backend.interface import PipelineBackend, PipelineInput
from api import schema


@dataclass
class _Job:
    status: str = "running"               # "running" | "done" | "failed"
    events: List[dict] = field(default_factory=list)
    result: Optional[dict] = None
    error: str = ""
    lock: threading.Lock = field(default_factory=threading.Lock)


class JobStore:
    """backend_factory()로 잡마다 새 PipelineBackend를 만들어 실행(상태 격리)."""

    def __init__(self, backend_factory: Callable[[], PipelineBackend]) -> None:
        self._backend_factory = backend_factory
        self._jobs: Dict[str, _Job] = {}

    def validate(self, inp: PipelineInput) -> List[str]:
        return self._backend_factory().validate_input(inp)

    def submit(self, inp: PipelineInput) -> str:
        job_id = uuid.uuid4().hex
        job = _Job()
        self._jobs[job_id] = job
        threading.Thread(target=self._run, args=(job, inp), daemon=True).start()
        return job_id

    def _run(self, job: _Job, inp: PipelineInput) -> None:
        try:
            backend = self._backend_factory()
            for ev in backend.run(inp):
                with job.lock:
                    job.events.append(schema.event_to_dict(ev))
            result = backend.get_result()
            with job.lock:
                job.result = schema.result_to_dict(result)
                job.status = "done"
        except Exception as exc:  # noqa: BLE001 - 실패를 잡 상태로 전달
            with job.lock:
                job.status = "failed"
                job.error = str(exc)

    def get_events(self, job_id: str, after: int) -> Optional[dict]:
        job = self._jobs.get(job_id)
        if job is None:
            return None
        with job.lock:
            return {"status": job.status, "events": job.events[after:],
                    "next": len(job.events)}

    def get_result(self, job_id: str) -> Tuple[str, Optional[object]]:
        """('ok', result) | ('not_ready', None) | ('failed', error) | ('not_found', None)"""
        job = self._jobs.get(job_id)
        if job is None:
            return ("not_found", None)
        with job.lock:
            if job.status == "failed":
                return ("failed", job.error)
            if job.status != "done" or job.result is None:
                return ("not_ready", None)
            return ("ok", job.result)
