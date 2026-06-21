from typing import Optional

from pydantic import BaseModel
from sqlalchemy import BigInteger, String, Integer, DateTime, func, Text
from sqlalchemy.orm import Mapped, mapped_column

class DataQualityIssue(BaseModel):
    __tablename__ = "data_quality_issue"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    etl_run_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    issue_type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    target_code: Mapped[Optional[str]] = mapped_column(String)
    detail: Mapped[Optional[str]] = mapped_column(Text)
    detected_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now())