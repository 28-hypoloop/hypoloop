from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import yaml


def build_experiment_dict(
    name: str,
    dataset: str,
    hypothesis: str,
    metric: str,
    params: dict | None = None,
) -> dict:
    """표준 실험 형식 딕셔너리를 생성한다.

    # TODO: name/dataset/hypothesis/metric 키 이름을 UI 팀(정의찬)과 합의 확인 필요
    """
    return {
        "name": name,
        "dataset": dataset,
        "hypothesis": hypothesis,
        "metric": metric,
        "params": params or {},
        "created_at": datetime.now(tz=timezone.utc).isoformat(),
    }


def write_experiment_yml(
    experiment: dict,
    output_path: str | Path,
) -> tuple[Path, str]:
    """실험 메타데이터를 YML 파일로 저장하고 (저장 경로, yml 문자열)을 반환한다.

    yml 문자열은 PipelineResult.experiment_yaml 에 바로 사용할 수 있다.
    sort_keys=False, allow_unicode=True 고정.
    """
    yml_str = yaml.dump(experiment, sort_keys=False, allow_unicode=True)
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yml_str, encoding="utf-8")
    return path, yml_str
