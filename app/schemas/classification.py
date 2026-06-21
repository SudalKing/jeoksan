from typing import Optional

from pydantic import BaseModel


class ClassificationSchema(BaseModel):
    item_code: str
    work_type_code: str
    work_type_name: str
    level1_code: Optional[str]
    level1_name: Optional[str]
    level2_code: Optional[str]
    level2_name: Optional[str]
    level3_code: Optional[str]
    level3_name: Optional[str]
    level4_code: Optional[str]
    level4_name: Optional[str]
    level5_code: Optional[str]
    level5_name: Optional[str]
    item_name: str


class ClassificationListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: list[ClassificationSchema]
