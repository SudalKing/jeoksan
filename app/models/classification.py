from typing import Optional

from sqlalchemy import Index, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime

from app.core.db import Base


class Classification(Base):
    __tablename__ = "classification"

    item_code: Mapped[str] = mapped_column(String, primary_key=True)
    work_type_code: Mapped[str] = mapped_column(String, nullable=False)
    work_type_name: Mapped[str] = mapped_column(String, nullable=False)

    level1_code: Mapped[Optional[str]] = mapped_column(String)
    level1_name: Mapped[Optional[str]] = mapped_column(String)
    level1_description: Mapped[Optional[str]] = mapped_column(String)
    level2_code: Mapped[Optional[str]] = mapped_column(String)
    level2_name: Mapped[Optional[str]] = mapped_column(String)
    level2_description: Mapped[Optional[str]] = mapped_column(String)
    level3_code: Mapped[Optional[str]] = mapped_column(String)
    level3_name: Mapped[Optional[str]] = mapped_column(String)
    level3_description: Mapped[Optional[str]] = mapped_column(String)
    level4_code: Mapped[Optional[str]] = mapped_column(String)
    level4_name: Mapped[Optional[str]] = mapped_column(String)
    level4_description: Mapped[Optional[str]] = mapped_column(String)
    level5_code: Mapped[Optional[str]] = mapped_column(String)
    level5_name: Mapped[Optional[str]] = mapped_column(String)
    level5_description: Mapped[Optional[str]] = mapped_column(String)

    item_name: Mapped[str] = mapped_column(String, nullable=False)
    spec: Mapped[Optional[str]] = mapped_column(String)
    raw_unit: Mapped[Optional[str]] = mapped_column(String)
    canonical_unit: Mapped[Optional[str]] = mapped_column(String)

    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[object] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index(
            "ix_classification_level_filter",
            "work_type_code",
            "level1_code",
            "level2_code",
            "level3_code",
            "level4_code",
            "level5_code",
        ),
        Index("ix_classification_item_name", "item_name"),
    )
