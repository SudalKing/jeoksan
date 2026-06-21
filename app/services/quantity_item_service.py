from typing import Optional

from sqlalchemy.orm import Session

from app.repository.quantity_item_repository import get_quantity_item, search_quantity_item
from app.schemas.quantity_item import PriceSchema, QuantityItemListResponse, QuantityItemSchema


def _to_schema(classification, material_cost, labor_cost, expense_cost, published_date) -> QuantityItemSchema:
    has_price = published_date is not None
    price = (
        PriceSchema(
            material_cost=material_cost,
            labor_cost=labor_cost,
            expense_cost=expense_cost,
            published_date=published_date,
        )
        if has_price
        else None
    )
    return QuantityItemSchema(
        item_code=classification.item_code,
        item_name=classification.item_name,
        work_type_code=classification.work_type_code,
        work_type_name=classification.work_type_name,
        level1_name=classification.level1_name,
        level2_name=classification.level2_name,
        level3_name=classification.level3_name,
        level4_name=classification.level4_name,
        level5_name=classification.level5_name,
        spec=classification.spec,
        unit=classification.canonical_unit,
        has_price=has_price,
        price=price,
    )


def search(
    db: Session,
    work_type_code: Optional[str],
    level_codes: list,
    keyword: Optional[str],
    has_price: Optional[bool],
    page: int,
    size: int,
    as_of=None
) -> QuantityItemListResponse:
    total, rows = search_quantity_item(db, work_type_code, level_codes, keyword, has_price, page, size, as_of)
    items = [_to_schema(*row) for row in rows]
    return QuantityItemListResponse(total=total, page=page, size=size, items=items)


def get_one(
        db: Session,
        item_code: str,
        as_of=None
) -> Optional[QuantityItemSchema]:
    row = get_quantity_item(db, item_code, as_of)
    if row is None:
        return None

    return _to_schema(*row)
