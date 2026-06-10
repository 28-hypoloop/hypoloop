import shutil
import uuid
from datetime import datetime
from typing import Generator, Optional

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.path_utils import (
    DATA_ROOT,
    ensure_dir,
    get_data_card_file_path,
    get_project_dir,
)
from app.db import crud
from app.db.session import get_db

router = APIRouter(prefix="/projects", tags=["data-cards"])


def _project_db(project_id: str) -> Generator[Session, None, None]:
    yield from get_db(project_id)


class DataCardResponse(BaseModel):
    card_id: str
    project_id: str
    name: str
    original_filename: str
    file_path: str
    role: Optional[str]
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
    role: Optional[str] = Form(None),
    db: Session = Depends(_project_db),
) -> DataCardResponse:
    """Upload a dataset file and register it as a data card.
    role: "train" | "test" | "description" — if set, replaces any existing card with that role.
    File is stored flat next to project.db as {project_id}_{card_id}{ext}.
    """
    if not get_project_dir(project_id).exists():
        raise HTTPException(status_code=404, detail="Project not found")

    # 같은 role의 기존 카드 파일 삭제 후 교체
    if role:
        existing = crud.get_data_card_by_role(db, project_id, role)
        if existing:
            old_path = get_data_card_file_path(
                project_id, existing.card_id, existing.original_filename
            )
            if old_path.exists():
                old_path.unlink()
            crud.delete_data_cards_by_role(db, project_id, role)

    card_id = str(uuid.uuid4())
    dest_path = get_data_card_file_path(project_id, card_id, file.filename)
    ensure_dir(dest_path.parent)

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
        role=role,
    )
    return _to_response(row)


@router.get("/{project_id}/data-cards", response_model=list[DataCardResponse])
def list_data_cards(
    project_id: str,
    db: Session = Depends(_project_db),
) -> list[DataCardResponse]:
    """List all data cards registered for a project."""
    if not get_project_dir(project_id).exists():
        raise HTTPException(status_code=404, detail="Project not found")
    return [_to_response(r) for r in crud.list_data_cards(db, project_id)]


@router.delete("/{project_id}/data-cards/{card_id}", status_code=204)
def delete_data_card(
    project_id: str,
    card_id: str,
    db: Session = Depends(_project_db),
) -> None:
    """Delete a data card record and its file."""
    row = crud.get_data_card(db, card_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Data card not found")
    dest_path = get_data_card_file_path(project_id, card_id, row.original_filename)
    if dest_path.exists():
        dest_path.unlink()
    crud.delete_data_card(db, card_id)


def _to_response(row) -> DataCardResponse:
    return DataCardResponse(
        card_id=row.card_id,
        project_id=row.project_id,
        name=row.name,
        original_filename=row.original_filename,
        file_path=row.file_path,
        role=row.role,
        created_at=row.created_at,
    )
