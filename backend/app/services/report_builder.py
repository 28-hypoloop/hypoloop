from typing import Optional

import yaml

from app.core.path_utils import get_experiments_dir


def _read_all_statuses(project_id: str, hypothesis_id: str) -> list[dict]:
    """Collect all status.yml contents under a hypothesis's experiments directory."""
    experiments_dir = get_experiments_dir(project_id, hypothesis_id)
    if not experiments_dir.exists():
        return []
    results = []
    for exp_dir in sorted(experiments_dir.iterdir()):
        if exp_dir.is_dir():
            status_path = exp_dir / "status.yml"
            if status_path.exists():
                with open(status_path, "r", encoding="utf-8") as f:
                    results.append(yaml.safe_load(f))
    return results


def get_best_score(project_id: str, hypothesis_id: str) -> Optional[float]:
    """Return the highest score across all experiments, or None if no scores yet."""
    statuses = _read_all_statuses(project_id, hypothesis_id)
    scores = [s["score"] for s in statuses if s.get("score") is not None]
    return max(scores) if scores else None


def get_score_history(project_id: str, hypothesis_id: str) -> list[dict]:
    """Return per-experiment score data ordered by directory name, suitable for graphing."""
    return [
        {
            "exp_id": s["exp_id"],
            "score": s.get("score"),
            "status": s.get("status"),
            "updated_at": s.get("updated_at"),
        }
        for s in _read_all_statuses(project_id, hypothesis_id)
    ]


def build_report(project_id: str, hypothesis_id: str) -> dict:
    """
    Aggregate all report data for a hypothesis by reading status.yml files:
      - best_score: highest score across experiments
      - score_history: per-experiment list for graphing
      - analysis_texts: analysis text from each experiment that has one
    """
    statuses = _read_all_statuses(project_id, hypothesis_id)
    scores = [s["score"] for s in statuses if s.get("score") is not None]
    return {
        "hypothesis_id": hypothesis_id,
        "best_score": max(scores) if scores else None,
        "score_history": [
            {
                "exp_id": s["exp_id"],
                "score": s.get("score"),
                "status": s.get("status"),
                "updated_at": s.get("updated_at"),
            }
            for s in statuses
        ],
        "analysis_texts": [
            {"exp_id": s["exp_id"], "text": s["analysis_text"]}
            for s in statuses
            if s.get("analysis_text") is not None
        ],
    }
