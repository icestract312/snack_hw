from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class SaleBase(BaseModel):
    snack_id: str
    quantity: int


class SaleCreate(SaleBase):
    timestamp: Optional[datetime] = None


class SaleUpdate(BaseModel):
    snack_id: Optional[str] = None
    quantity: Optional[int] = None
    timestamp: Optional[datetime] = None


class SaleResponse(SaleBase):
    id: str
    timestamp: datetime

    class Config:
        from_attributes = True
