from typing import Optional

from sqlalchemy.orm import Session

from app.db import crud


def get_best_score(db: Session, hypothesis_id: str) -> Optional[float]:
    """Return the highest score across all experiments, or None if no scores yet."""
    exps = crud.list_experiments(db, hypothesis_id)
    scores = [e.score for e in exps if e.score is not None]
    return max(scores) if scores else None


def get_score_history(db: Session, hypothesis_id: str) -> list[dict]:
    """
    Return per-experiment score data ordered by creation time, suitable for graphing.
    Experiments without a score are included with score=null.
    """
    exps = crud.list_experiments(db, hypothesis_id)
    return [
        {
            "exp_id": e.exp_id,
            "score": e.score,
            "status": e.status,
            "created_at": e.created_at.isoformat(),
        }
        for e in exps
    ]


def build_report(db: Session, hypothesis_id: str) -> dict:
    """
    Aggregate all report data for a hypothesis:
      - best_score: highest score across experiments
      - score_history: per-experiment list for graphing
      - analysis_texts: analysis text from each completed experiment
    """
    exps = crud.list_experiments(db, hypothesis_id)
    scores = [e.score for e in exps if e.score is not None]
    return {
        "hypothesis_id": hypothesis_id,
        "best_score": max(scores) if scores else None,
        "score_history": [
            {
                "exp_id": e.exp_id,
                "score": e.score,
                "status": e.status,
                "created_at": e.created_at.isoformat(),
            }
            for e in exps
        ],
        "analysis_texts": [
            {"exp_id": e.exp_id, "text": e.analysis_text}
            for e in exps
            if e.analysis_text is not None
        ],
    }
