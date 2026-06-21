from datetime import date
from typing import Optional

from pydantic import BaseModel


class PublicationSchema(BaseModel):
    published_date: date
    description: Optional[str]

class PublicationListResponse(BaseModel):
    total: int
    items: list[PublicationSchema]