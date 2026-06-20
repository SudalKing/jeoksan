from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime

from app.core.db import Base


class UnitAlias(Base):
    __tablename__ = "unit_alias"

    raw_unit: Mapped[str] = mapped_column(String, primary_key=True)
    canonical_unit: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now())
