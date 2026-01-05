from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class StockBase(BaseModel):
    snack_id: str
    quantity: int
    quantity_now: int


class StockCreate(StockBase):
    pass


class BarcodeStockRequest(BaseModel):
    barcode: str
    quantity: int


class StockUpdate(BaseModel):
    snack_id: Optional[str] = None
    quantity: Optional[int] = None
    quantity_now: Optional[int] = None


class StockResponse(StockBase):
    id: str
    create_at: datetime

    class Config:
        from_attributes = True


class PurchaseItem(BaseModel):
    snack_id: str
    quantity: int

    class Config:
        from_attributes = True
