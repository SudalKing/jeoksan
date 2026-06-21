from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.response import success
from app.repository.classification_repository import search_classification
from app.schemas.classification import ClassificationListResponse, ClassificationSchema

router = APIRouter()


@router.get("/classification")
def list_classification(
    work_type_code: Optional[str] = None,
    level1_code: Optional[str] = None,
    level2_code: Optional[str] = None,
    level3_code: Optional[str] = None,
    level4_code: Optional[str] = None,
    level5_code: Optional[str] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    level_codes = [level1_code, level2_code, level3_code, level4_code, level5_code]
    total, rows = search_classification(db, work_type_code, level_codes, page, size)
    items = [ClassificationSchema.model_validate(row, from_attributes=True) for row in rows]
    result = ClassificationListResponse(total=total, page=page, size=size, items=items)

    return success(result.model_dump(mode="json"))
