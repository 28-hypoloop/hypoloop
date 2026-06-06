from typing import Optional

from sqlalchemy.orm import Session

from app.db.models import Experiment, Hypothesis


def create_hypothesis(
    db: Session,
    *,
    hypothesis_id: str,
    project_id: str,
    u_id: str,
    content: str,
    max_experiments: int,
    parallel_count: int,
) -> Hypothesis:
    """Insert a new hypothesis record and return it."""
    row = Hypothesis(
        hypothesis_id=hypothesis_id,
        project_id=project_id,
        u_id=u_id,
        content=content,
        max_experiments=max_experiments,
        parallel_count=parallel_count,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_hypothesis(db: Session, hypothesis_id: str) -> Optional[Hypothesis]:
    """Return a hypothesis by ID, or None if not found."""
    return db.get(Hypothesis, hypothesis_id)


def list_hypotheses(db: Session, project_id: str) -> list[Hypothesis]:
    """Return all hypotheses belonging to a project."""
    return db.query(Hypothesis).filter(Hypothesis.project_id == project_id).all()


def create_experiment(db: Session, *, exp_id: str, hypothesis_id: str) -> Experiment:
    """Insert a new experiment record with status='ready' and return it."""
    row = Experiment(exp_id=exp_id, hypothesis_id=hypothesis_id, status="ready")
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_experiment(db: Session, exp_id: str) -> Optional[Experiment]:
    """Return an experiment by ID, or None if not found."""
    return db.get(Experiment, exp_id)


def update_experiment(
    db: Session,
    exp_id: str,
    *,
    score: Optional[float] = None,
    status: Optional[str] = None,
    analysis_text: Optional[str] = None,
) -> Optional[Experiment]:
    """Partially update an experiment record. Returns the updated row, or None if not found."""
    row = db.get(Experiment, exp_id)
    if row is None:
        return None
    if score is not None:
        row.score = score
    if status is not None:
        row.status = status
    if analysis_text is not None:
        row.analysis_text = analysis_text
    db.commit()
    db.refresh(row)
    return row


def list_experiments(db: Session, hypothesis_id: str) -> list[Experiment]:
    """Return all experiments for a hypothesis ordered by creation time."""
    return (
        db.query(Experiment)
        .filter(Experiment.hypothesis_id == hypothesis_id)
        .order_by(Experiment.created_at)
        .all()
    )
