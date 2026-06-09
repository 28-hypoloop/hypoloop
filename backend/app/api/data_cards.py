import shutil
import uuid
from datetime import datetime
from typing import Generator

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.path_utils import (
    DATA_ROOT,
    ensure_dir,
    get_dataset_dir,
    get_project_dir,
)
from app.db import crud
from app.db.session import get_db

router = APIRouter(prefix="/projects", tags=["data-cards"])


def _project_db(project_id: str) -> Generator[Session, None, None]:
    """Resolve a DB session from the project_id path parameter."""
    yield from get_db(project_id)


class DataCardResponse(BaseModel):
    card_id: str
    project_id: str
    name: str
    original_filename: str
    file_path: str
    created_at: datetime


@router.post(
    "/{project_id}/data-cards",
    response_model=DataCardResponse,
    status_code=201,
)
async def upload_data_card(
    project_id: str,
    file: UploadFile,
    name: str = Form(...),
    db: Session = Depends(_project_db),
) -> DataCardResponse:
    """Upload a dataset file and register it as a data card for the project."""
    if not get_project_dir(project_id).exists():
        raise HTTPException(status_code=404, detail="Project not found")

    card_id = str(uuid.uuid4())
    dest_dir = ensure_dir(get_dataset_dir(project_id, card_id))
    dest_path = dest_dir / file.filename

    with dest_path.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    relative_path = str(dest_path.relative_to(DATA_ROOT))

    row = crud.create_data_card(
        db,
        card_id=card_id,
        project_id=project_id,
        name=name,
        original_filename=file.filename,
        file_path=relative_path,
    )
    return DataCardResponse(
        card_id=row.card_id,
        project_id=row.project_id,
        name=row.name,
        original_filename=row.original_filename,
        file_path=row.file_path,
        created_at=row.created_at,
    )


@router.get("/{project_id}/data-cards", response_model=list[DataCardResponse])
def list_data_cards(
    project_id: str,
    db: Session = Depends(_project_db),
) -> list[DataCardResponse]:
    """List all data cards registered for a project."""
    if not get_project_dir(project_id).exists():
        raise HTTPException(status_code=404, detail="Project not found")

    rows = crud.list_data_cards(db, project_id)
    return [
        DataCardResponse(
            card_id=r.card_id,
            project_id=r.project_id,
            name=r.name,
            original_filename=r.original_filename,
            file_path=r.file_path,
            created_at=r.created_at,
        )
        for r in rows
    ]


@router.delete("/{project_id}/data-cards/{card_id}", status_code=204)
def delete_data_card(
    project_id: str,
    card_id: str,
    db: Session = Depends(_project_db),
) -> None:
    """Delete a data card record and its uploaded file directory."""
    row = crud.get_data_card(db, card_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Data card not found")

    dataset_dir = get_dataset_dir(project_id, card_id)
    if dataset_dir.exists():
        shutil.rmtree(dataset_dir)

    crud.delete_data_card(db, card_id)
