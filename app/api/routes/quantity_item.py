from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.response import error, success
from app.services import quantity_item_service

router = APIRouter()


@router.get("/quantity-item")
def search_quantity_item(
    work_type_code: Optional[str] = None,
    level1_code: Optional[str] = None,
    level2_code: Optional[str] = None,
    level3_code: Optional[str] = None,
    level4_code: Optional[str] = None,
    level5_code: Optional[str] = None,
    keyword: Optional[str] = None,
    has_price: Optional[bool] = None,
    as_of: Optional[date] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    level_codes = [level1_code, level2_code, level3_code, level4_code, level5_code]
    result = quantity_item_service.search(db, work_type_code, level_codes, keyword, has_price, page, size, as_of)

    return success(result.model_dump(mode="json"))


@router.get("/quantity-item/{item_code}")
def get_quantity_item(
        item_code: str,
        as_of: Optional[date] = None,
        db: Session = Depends(get_db)
):
    result = quantity_item_service.get_one(db, item_code, as_of)
    if result is None:
        return error(f"item_code '{item_code}' not found")

    return success(result.model_dump(mode="json"))
