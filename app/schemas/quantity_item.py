from datetime import date
from typing import Optional

from pydantic import BaseModel


class PriceSchema(BaseModel):
    material_cost: Optional[float]
    labor_cost: Optional[float]
    expense_cost: Optional[float]
    published_date: Optional[date]


class QuantityItemSchema(BaseModel):
    item_code: str
    item_name: str
    work_type_code: str
    work_type_name: str
    level1_name: Optional[str]
    level2_name: Optional[str]
    level3_name: Optional[str]
    level4_name: Optional[str]
    level5_name: Optional[str]
    spec: Optional[str]
    unit: Optional[str]
    has_price: bool
    price: Optional[PriceSchema]


class QuantityItemListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: list[QuantityItemSchema]
