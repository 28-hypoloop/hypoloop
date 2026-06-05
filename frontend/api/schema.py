"""dataclass ↔ dict(JSON) 직렬화 — HTTP 와이어 포맷의 단일 출처."""
from __future__ import annotations

from typing import Optional

from backend.interface import (
    DataCard, PipelineInput, ProgressEvent, MetricRecord, PipelineResult,
)


def metric_to_dict(m: Optional[MetricRecord]) -> Optional[dict]:
    if m is None:
        return None
    return {"loop_index": m.loop_index, "metric_name": m.metric_name,
            "baseline": m.baseline, "value": m.value}


def metric_from_dict(d: Optional[dict]) -> Optional[MetricRecord]:
    if d is None:
        return None
    return MetricRecord(loop_index=d["loop_index"], metric_name=d["metric_name"],
                        baseline=d["baseline"], value=d["value"])


def input_to_dict(inp: PipelineInput) -> dict:
    return {
        "csv_path": inp.csv_path,
        "loop_count": inp.loop_count,
        "data_card": {
            "target_column": inp.data_card.target_column,
            "task_type": inp.data_card.task_type,
            "description": inp.data_card.description,
        },
        "llm_instruction": inp.llm_instruction,
    }


def input_from_dict(d: dict) -> PipelineInput:
    dc = d["data_card"]
    return PipelineInput(
        csv_path=d["csv_path"],
        loop_count=d["loop_count"],
        data_card=DataCard(target_column=dc["target_column"],
                           task_type=dc["task_type"],
                           description=dc.get("description", "")),
        llm_instruction=d["llm_instruction"],
    )


def event_to_dict(ev: ProgressEvent) -> dict:
    return {"stage": ev.stage, "loop_index": ev.loop_index, "status": ev.status,
            "message": ev.message, "kind": ev.kind, "detail": ev.detail,
            "metric": metric_to_dict(ev.metric)}


def event_from_dict(d: dict) -> ProgressEvent:
    return ProgressEvent(stage=d["stage"], loop_index=d["loop_index"],
                         status=d["status"], message=d["message"],
                         kind=d.get("kind", "stage"), detail=d.get("detail", ""),
                         metric=metric_from_dict(d.get("metric")))


def result_to_dict(r: PipelineResult) -> dict:
    return {"report_md": r.report_md, "final_code": r.final_code,
            "metrics_history": [metric_to_dict(m) for m in r.metrics_history],
            "experiment_yaml": r.experiment_yaml}


def result_from_dict(d: dict) -> PipelineResult:
    return PipelineResult(
        report_md=d["report_md"], final_code=d["final_code"],
        metrics_history=[metric_from_dict(m) for m in d["metrics_history"]],
        experiment_yaml=d.get("experiment_yaml", ""))
