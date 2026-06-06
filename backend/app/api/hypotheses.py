import uuid
from typing import Generator

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db import crud
from app.db.session import get_db
from app.services import trigger, yml_generator
from app.services.report_builder import build_report

router = APIRouter(tags=["hypotheses"])


# --- shared DB dependency ---

def _project_db(project_id: str) -> Generator[Session, None, None]:
    """Resolve a DB session from the project_id path/query parameter."""
    yield from get_db(project_id)


# --- schemas ---

class HypothesisCreate(BaseModel):
    u_id: str
    content: str
    max_experiments: int = Field(gt=0)
    parallel_count: int = Field(gt=0)


class HypothesisResponse(BaseModel):
    hypothesis_id: str
    project_id: str
    u_id: str
    content: str
    max_experiments: int
    parallel_count: int
    yml_path: str


# --- endpoints ---

@router.post(
    "/projects/{project_id}/hypotheses",
    response_model=HypothesisResponse,
    status_code=201,
)
def create_hypothesis(
    project_id: str,
    body: HypothesisCreate,
    db: Session = Depends(_project_db),
) -> HypothesisResponse:
    """Register a hypothesis in DB and generate its u_id_hypothesis_id.yml."""
    hypothesis_id = str(uuid.uuid4())

    crud.create_hypothesis(
        db,
        hypothesis_id=hypothesis_id,
        project_id=project_id,
        u_id=body.u_id,
        content=body.content,
        max_experiments=body.max_experiments,
        parallel_count=body.parallel_count,
    )

    yml_path = yml_generator.generate_hypothesis_yml(
        u_id=body.u_id,
        project_id=project_id,
        hypothesis_id=hypothesis_id,
        content=body.content,
        max_experiments=body.max_experiments,
        parallel_count=body.parallel_count,
    )

    return HypothesisResponse(
        hypothesis_id=hypothesis_id,
        project_id=project_id,
        u_id=body.u_id,
        content=body.content,
        max_experiments=body.max_experiments,
        parallel_count=body.parallel_count,
        yml_path=str(yml_path),
    )


@router.post("/hypotheses/{hypothesis_id}/ready", status_code=200)
def trigger_ready(
    hypothesis_id: str,
    project_id: str,
    u_id: str,
) -> dict:
    """
    Set ready=true in the hypothesis YML and notify the agent.
    project_id and u_id are required query parameters to locate the YML file.
    """
    try:
        yml_path = trigger.set_ready(
            project_id=project_id,
            u_id=u_id,
            hypothesis_id=hypothesis_id,
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Hypothesis YML not found")

    return {"hypothesis_id": hypothesis_id, "ready": True, "yml_path": str(yml_path)}


@router.get("/hypotheses/{hypothesis_id}/report")
def get_report(
    hypothesis_id: str,
    project_id: str,
    db: Session = Depends(_project_db),
) -> dict:
    """Return best_score, score_history, and analysis_texts for a hypothesis."""
    if crud.get_hypothesis(db, hypothesis_id) is None:
        raise HTTPException(status_code=404, detail="Hypothesis not found")
    return build_report(db, hypothesis_id)
