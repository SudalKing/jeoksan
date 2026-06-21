from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.classification import Classification


def search_classification(
    db: Session,
    work_type_code: Optional[str],
    level_codes: list,
    page: int,
    size: int,
):
    stmt = select(Classification)
    if work_type_code:
        stmt = stmt.where(Classification.work_type_code == work_type_code)
    for idx, code in enumerate(level_codes, start=1):
        if code:
            stmt = stmt.where(getattr(Classification, f"level{idx}_code") == code)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.execute(count_stmt).scalar_one()

    stmt = stmt.order_by(Classification.item_code).offset((page - 1) * size).limit(size)
    rows = db.execute(stmt).scalars().all()

    return total, rows
