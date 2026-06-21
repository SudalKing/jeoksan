from typing import Optional

from sqlalchemy.orm import Session

from app.models import Classification
from app.schemas.price_history import PriceHistorySchema, PricePointSchema, ChangeRate
from app.repository.price_history_repository import get_price_history as fetch_price_history


def _change_rate(
        current,
        previous
) -> Optional[float]:
    if current is None or previous is None or previous == 0:
        return None

    return round((float(current) - float(previous)) / float(previous), 4)


def _total(
        material,
        labor,
        expense
) -> Optional[float]:
    values = [v for v in (material, labor, expense) if v is not None]

    return float(sum(values)) if values else None


def get_price_history(
        db: Session,
        item_code: str
) -> Optional[PriceHistorySchema]:
    cls = db.get(Classification, item_code)
    rows = fetch_price_history(db, item_code)

    if cls is None and not rows:  # classification에도 없고 단가도 없으면 진짜 404
        return None

    history = []
    for row in rows:
        pub_date, mat, lab, exp, prev_mat, prev_lab, prev_exp = row
        total = _total(mat, lab, exp)
        prev_total = _total(prev_mat, prev_lab, prev_exp)

        history.append(PricePointSchema(
            published_date=pub_date,
            material_cost=float(mat) if mat is not None else None,
            labor_cost=float(lab) if lab is not None else None,
            expense_cost=float(exp) if exp is not None else None,
            total_cost=total,
            change_rate=ChangeRate(
                material_cost=_change_rate(mat, prev_mat),
                labor_cost=_change_rate(lab, prev_lab),
                expense_cost=_change_rate(exp, prev_exp),
                total_cost=_change_rate(total, prev_total),
            ),
        ))

    return PriceHistorySchema(
        item_code=item_code,
        item_name=cls.item_name if cls else None,
        unit=cls.canonical_unit if cls else None,
        history=history,
    )