from datetime import date
from typing import Optional

from pydantic import BaseModel


class ChangeRate(BaseModel):
    material_cost: Optional[float]
    labor_cost: Optional[float]
    expense_cost: Optional[float]
    total_cost: Optional[float]

class PricePointSchema(BaseModel):
    published_date: date
    material_cost: Optional[float]
    labor_cost: Optional[float]
    expense_cost: Optional[float]
    total_cost: Optional[float]
    change_rate: ChangeRate

class PriceHistorySchema(BaseModel):
    item_code: str
    item_name: Optional[str]
    unit: Optional[str]
    history: list[PricePointSchema]