from typing import Optional

from sqlalchemy import Date, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Publication(Base):
    __tablename__ = "publication"

    published_date: Mapped[object] = mapped_column(Date, primary_key=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[object] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )