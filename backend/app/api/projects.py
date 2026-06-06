import uuid

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.path_utils import ensure_dir, get_project_dir, get_reports_dir
from app.db.session import init_db

router = APIRouter(prefix="/projects", tags=["projects"])


class ProjectCreate(BaseModel):
    project_id: str | None = None  # auto-generated if omitted
    name: str | None = None


class ProjectResponse(BaseModel):
    project_id: str


@router.post("", response_model=ProjectResponse, status_code=201)
def create_project(body: ProjectCreate) -> ProjectResponse:
    """Create a project directory, initialise its SQLite DB, and return the project_id."""
    project_id = body.project_id or str(uuid.uuid4())
    ensure_dir(get_project_dir(project_id))
    ensure_dir(get_reports_dir(project_id))
    init_db(project_id)
    return ProjectResponse(project_id=project_id)
