from sqlalchemy import text
from sqlalchemy.orm import Session


def get_price_history(
        session: Session,
        item_code: str
):
    result = session.execute(text("""
        SELECT
            published_date,
            material_cost,
            labor_cost,
            expense_cost,
            LAG(material_cost) OVER (ORDER BY published_date) AS prev_material,
            LAG(labor_cost)    OVER (ORDER BY published_date) AS prev_labor,
            LAG(expense_cost)  OVER (ORDER BY published_date) AS prev_expense
        FROM std_market_price
        WHERE item_code = :item_code
        ORDER BY published_date
    """),{"item_code": item_code},
    )
    
    return result.fetchall()