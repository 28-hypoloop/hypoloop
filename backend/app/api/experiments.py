import uuid
from typing import Generator, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import crud
from app.db.session import get_db

router = APIRouter(tags=["experiments"])


# --- shared DB dependency ---

def _project_db(project_id: str) -> Generator[Session, None, None]:
    """Resolve a DB session from the project_id query parameter."""
    yield from get_db(project_id)


# --- schemas ---

class ExperimentResponse(BaseModel):
    exp_id: str
    hypothesis_id: str
    score: Optional[float]
    status: str
    analysis_text: Optional[str]


class ExperimentUpdate(BaseModel):
    score: Optional[float] = None
    status: Optional[str] = None
    analysis_text: Optional[str] = None


# --- endpoints ---

@router.post(
    "/hypotheses/{hypothesis_id}/experiments",
    response_model=ExperimentResponse,
    status_code=201,
)
def create_experiment(
    hypothesis_id: str,
    project_id: str,
    db: Session = Depends(_project_db),
) -> ExperimentResponse:
    """
    Register a new experiment record in DB (DB only — exp_id.yml is written by the agent).
    project_id is a required query parameter.
    """
    row = crud.create_experiment(
        db, exp_id=str(uuid.uuid4()), hypothesis_id=hypothesis_id
    )
    return ExperimentResponse(
        exp_id=row.exp_id,
        hypothesis_id=row.hypothesis_id,
        score=row.score,
        status=row.status,
        analysis_text=row.analysis_text,
    )


@router.patch("/experiments/{exp_id}", response_model=ExperimentResponse)
def update_experiment(
    exp_id: str,
    body: ExperimentUpdate,
    project_id: str,
    db: Session = Depends(_project_db),
) -> ExperimentResponse:
    """Agent callback: update score, status, or analysis_text for a finished experiment."""
    row = crud.update_experiment(
        db,
        exp_id,
        score=body.score,
        status=body.status,
        analysis_text=body.analysis_text,
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return ExperimentResponse(
        exp_id=row.exp_id,
        hypothesis_id=row.hypothesis_id,
        score=row.score,
        status=row.status,
        analysis_text=row.analysis_text,
    )
