from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.response import success
from app.repository.publication_repository import list_publications
from app.schemas.publication import PublicationSchema, PublicationListResponse

router = APIRouter()

@router.get("/publication")
def get_publications(db: Session = Depends(get_db)):
    total, rows = list_publications(db)
    items = [PublicationSchema.model_validate(row, from_attributes=True) for row in rows]
    result = PublicationListResponse(total=total, items=items)

    return success(result.model_dump(mode="json"))