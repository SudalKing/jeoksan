from datetime import date
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.classification import Classification
from app.models.price import StdMarketPrice


def _latest_price_subquery(as_of: Optional[date] = None):
    stmt = (
        select(
            StdMarketPrice.item_code.label("item_code"),
            func.max(StdMarketPrice.published_date).label("max_published_date"),
        )
        .where(StdMarketPrice.item_code.is_not(None))
    )

    if as_of:
        stmt = stmt.where(StdMarketPrice.published_date <= as_of)

    return stmt.group_by(StdMarketPrice.item_code).subquery()


def _base_query(
        work_type_code,
        level_codes,
        keyword,
        has_price,
        as_of=None
):
    latest = _latest_price_subquery(as_of)
    latest_price = (
        select(
            StdMarketPrice.id,
            StdMarketPrice.item_code,
            StdMarketPrice.material_cost,
            StdMarketPrice.labor_cost,
            StdMarketPrice.expense_cost,
            StdMarketPrice.published_date,
        )
        .join(
            latest,
            (StdMarketPrice.item_code == latest.c.item_code)
            & (StdMarketPrice.published_date == latest.c.max_published_date),
        )
        .subquery()
    )

    stmt = select(
        Classification,
        latest_price.c.material_cost,
        latest_price.c.labor_cost,
        latest_price.c.expense_cost,
        latest_price.c.published_date,
    ).join(latest_price, Classification.item_code == latest_price.c.item_code, isouter=True)

    if work_type_code:
        stmt = stmt.where(Classification.work_type_code == work_type_code)
    for idx, code in enumerate(level_codes, start=1):
        if code:
            stmt = stmt.where(getattr(Classification, f"level{idx}_code") == code)
    if keyword:
        stmt = stmt.where(Classification.item_name.ilike(f"%{keyword}%"))
    if has_price is not None:
        price_exists = latest_price.c.id.is_not(None)
        stmt = stmt.where(price_exists if has_price else ~price_exists)

    return stmt, latest_price


def search_quantity_item(
    db: Session,
    work_type_code: Optional[str],
    level_codes: list,
    keyword: Optional[str],
    has_price: Optional[bool],
    page: int,
    size: int,
    as_of: Optional[date] = None,
):
    stmt, _ = _base_query(work_type_code, level_codes, keyword, has_price, as_of)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.execute(count_stmt).scalar_one()

    stmt = stmt.order_by(Classification.item_code).offset((page - 1) * size).limit(size)
    rows = db.execute(stmt).all()

    return total, rows


def get_quantity_item(
        db: Session,
        item_code: str,
        as_of: Optional[date] = None,
):
    stmt, _ = _base_query(None, [], None, None, as_of)
    stmt = stmt.where(Classification.item_code == item_code)

    return db.execute(stmt).first()
