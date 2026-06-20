from typing import Optional

from sqlalchemy import BigInteger, Date, Index, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime

from app.core.db import Base


class StdMarketPrice(Base):
    __tablename__ = "std_market_price"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    item_code: Mapped[Optional[str]] = mapped_column(String)
    work_type_code: Mapped[Optional[str]] = mapped_column(String)
    work_type_name: Mapped[Optional[str]] = mapped_column(String)
    product_name: Mapped[Optional[str]] = mapped_column(String)
    spec: Mapped[Optional[str]] = mapped_column(String)
    raw_unit: Mapped[Optional[str]] = mapped_column(String)
    canonical_unit: Mapped[Optional[str]] = mapped_column(String)

    material_cost: Mapped[Optional[float]] = mapped_column(Numeric)
    labor_cost: Mapped[Optional[float]] = mapped_column(Numeric)
    expense_cost: Mapped[Optional[float]] = mapped_column(Numeric)

    published_date: Mapped[Optional[object]] = mapped_column(Date)
    price_condition_note: Mapped[Optional[str]] = mapped_column(Text)

    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("item_code", "published_date", name="uq_price_item_published_date"),
        Index("ix_price_item_code", "item_code"),
    )
