from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.price import StdMarketPrice


def get_price_history(session: Session, item_code: str):
    lag = lambda col: func.lag(col).over(order_by=StdMarketPrice.published_date)

    stmt = (
        select(
            StdMarketPrice.published_date,
            StdMarketPrice.material_cost,
            StdMarketPrice.labor_cost,
            StdMarketPrice.expense_cost,
            lag(StdMarketPrice.material_cost).label("prev_material"),
            lag(StdMarketPrice.labor_cost).label("prev_labor"),
            lag(StdMarketPrice.expense_cost).label("prev_expense"),
        )
        .where(StdMarketPrice.item_code == item_code)
        .order_by(StdMarketPrice.published_date)
    )

    return session.execute(stmt).fetchall()