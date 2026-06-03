"""실제 백엔드 데이터 계층(hypoloop)을 UI 계약(PipelineBackend)에 연결하는 어댑터.

- 실제 사용: CSV→SQLite 적재(load_csv), 실험로그 적재/조회(append/query),
  실험 yml 생성(write_experiment_yml).
- 임시(placeholder): 모델 학습/평가 지표 값. 학습 계층(LangGraph 에이전트)이
  아직 없어서, 지표 숫자는 시뮬레이션이며 리포트에 그 사실을 명시한다.

hypoloop 패키지가 import 가능할 때만 동작한다(app.py가 실패 시 MockBackend로 폴백).
"""
from __future__ import annotations

import os
import tempfile
import time
from typing import Iterator, List, Optional

import pandas as pd

from backend.interface import (
    PipelineInput, ProgressEvent, MetricRecord, PipelineResult, TASK_TYPES,
)
from hypoloop.data.loader import (
    load_csv, append_experiment_log, query_metric_records, _normalize_db_path,
)
from hypoloop.data.writer import build_experiment_dict, write_experiment_yml

_DB_NAME = "hypoloop.db"
_TABLE = "raw_data"
_STEP_DELAY = 0.05


class DataLayerBackend:
    """hypoloop 데이터 계층을 사용하는 PipelineBackend 구현."""

    def __init__(self, step_delay: float = _STEP_DELAY) -> None:
        self._step_delay = step_delay
        self._result: Optional[PipelineResult] = None

    def validate_input(self, inp: PipelineInput) -> List[str]:
        errors: List[str] = []
        try:
            columns = list(pd.read_csv(inp.csv_path, nrows=1).columns)
        except Exception as exc:  # noqa: BLE001 - 사용자에게 그대로 안내
            return [f"CSV를 읽을 수 없습니다: {exc}"]
        if inp.data_card.target_column not in columns:
            errors.append(
                f"타깃 컬럼 '{inp.data_card.target_column}'이(가) CSV에 없습니다."
            )
        if inp.data_card.task_type not in TASK_TYPES:
            errors.append(f"태스크 종류가 올바르지 않습니다: {inp.data_card.task_type}")
        if inp.loop_count < 1:
            errors.append("루프 횟수는 1 이상이어야 합니다.")
        if not inp.llm_instruction.strip():
            errors.append("언어모델 입력(가설/목표)을 작성해주세요.")
        return errors

    def run(self, inp: PipelineInput) -> Iterator[ProgressEvent]:
        is_clf = inp.data_card.task_type == "classification"
        metric_name = "accuracy" if is_clf else "rmse"
        baseline = 0.70 if is_clf else 0.50

        # 매 실행마다 이전 실험로그 초기화(누적 방지)
        db_file = _normalize_db_path(_DB_NAME)
        if db_file.exists():
            db_file.unlink()

        # 계획수립 / EDA
        for stage in ("계획수립", "EDA"):
            yield ProgressEvent(stage=stage, loop_index=0, status="running",
                                message=f"{stage} 진행 중…")
            time.sleep(self._step_delay)
            yield ProgressEvent(stage=stage, loop_index=0, status="done",
                                message=f"{stage} 완료")

        # 베이스라인: CSV를 SQLite에 실제 적재 (백엔드 load_csv)
        yield ProgressEvent(stage="베이스라인", loop_index=0, status="running",
                            message="CSV를 SQLite에 적재하고 베이스라인 학습 중…")
        n_rows = load_csv(inp.csv_path, _DB_NAME, _TABLE)
        append_experiment_log(
            {"loop_index": 0, "metric_name": metric_name,
             "baseline": baseline, "value": baseline},
            _DB_NAME,
        )
        time.sleep(self._step_delay)
        yield ProgressEvent(stage="베이스라인", loop_index=0, status="done",
                            message=f"SQLite 적재 {n_rows}행, "
                                    f"베이스라인 {metric_name}={baseline}")

        # 개선 루프 (지표 값은 임시 — 학습 계층 미구현)
        for loop in range(1, inp.loop_count + 1):
            for stage in ("피처엔지니어링", "튜닝"):
                yield ProgressEvent(stage=stage, loop_index=loop, status="running",
                                    message=f"루프 {loop}: {stage} 진행 중…")
                time.sleep(self._step_delay)
                yield ProgressEvent(stage=stage, loop_index=loop, status="done",
                                    message=f"루프 {loop}: {stage} 완료")
            if is_clf:
                value = round(min(baseline + 0.04 * loop, 0.95), 4)
            else:
                value = round(max(baseline - 0.03 * loop, 0.10), 4)
            append_experiment_log(
                {"loop_index": loop, "metric_name": metric_name,
                 "baseline": baseline, "value": value},
                _DB_NAME,
            )

        # 리포트: 실험 yml 실제 생성 (백엔드 writer)
        yield ProgressEvent(stage="리포트", loop_index=inp.loop_count,
                            status="running", message="실험 yml 생성 및 리포트 작성 중…")
        self._result = self._build_result(inp, metric_name, n_rows)
        time.sleep(self._step_delay)
        yield ProgressEvent(stage="리포트", loop_index=inp.loop_count,
                            status="done", message="완료")

    def get_result(self) -> PipelineResult:
        if self._result is None:
            raise RuntimeError("run()을 먼저 실행해야 결과를 얻을 수 있습니다.")
        return self._result

    def _build_result(self, inp: PipelineInput, metric_name: str,
                      n_rows: int) -> PipelineResult:
        # 백엔드에서 지표 조회 → UI MetricRecord 로 변환 (형식 1:1)
        rows = query_metric_records(_DB_NAME)
        metrics = [MetricRecord(**r) for r in rows]
        metrics.sort(key=lambda m: m.loop_index)
        base = metrics[0].value if metrics else 0.0
        best = metrics[-1].value if metrics else 0.0
        delta = round(best - base, 4)

        # 백엔드 writer 로 실험 yml 생성
        exp = build_experiment_dict(
            name=f"{inp.data_card.target_column}-experiment",
            dataset=inp.csv_path,
            hypothesis=inp.llm_instruction,
            metric=metric_name,
            params={"loop_count": inp.loop_count,
                    "task_type": inp.data_card.task_type},
        )
        # 백엔드 writer는 파일 저장+문자열 반환. UI엔 문자열만 필요하므로
        # 임시 파일에 써서 문자열만 취하고 파일은 정리한다(작업 트리 오염 방지).
        fd, tmp_yml = tempfile.mkstemp(suffix=".yml")
        os.close(fd)
        try:
            _, yml_str = write_experiment_yml(exp, tmp_yml)
        finally:
            os.unlink(tmp_yml)

        report_md = (
            f"# 분석 리포트 (hypoloop 통합)\n\n"
            f"- 데이터: `{inp.csv_path}` → SQLite `{_TABLE}` ({n_rows}행)\n"
            f"- 타깃: **{inp.data_card.target_column}** "
            f"({inp.data_card.task_type})\n"
            f"- 루프 횟수: {inp.loop_count}\n\n"
            f"## 성능 요약\n\n"
            f"| 구분 | {metric_name} |\n|---|---|\n"
            f"| 베이스라인 | {base} |\n| 최종 | {best} |\n"
            f"| 향상폭(Δ) | {delta} |\n\n"
            f"## 사용자 가설\n\n> {inp.llm_instruction}\n\n"
            f"> ℹ️ 데이터 적재·실험로그·yml은 실제 백엔드(hypoloop) 기능을 사용했습니다. "
            f"지표 값은 학습 계층(에이전트) 미구현으로 임시값입니다.\n\n"
            f"> ⚠️ 제한된 데이터·환경에서 도출된 결과이므로, "
            f"프로덕션 적용 전 반드시 검토가 필요합니다.\n"
        )
        final_code = (
            "# hypoloop 데이터 계층 사용 예시\n"
            "from hypoloop.data.loader import load_csv, query_metric_records\n"
            "from hypoloop.data.writer import build_experiment_dict, "
            "write_experiment_yml\n\n"
            f"load_csv(r'{inp.csv_path}', '{_DB_NAME}', '{_TABLE}')\n"
            "# TODO: 학습/평가 계층에서 실험로그 append 후 리포트 생성\n"
        )
        return PipelineResult(report_md=report_md, final_code=final_code,
                              metrics_history=metrics, experiment_yaml=yml_str)
