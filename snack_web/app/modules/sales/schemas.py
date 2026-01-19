from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.modules.snacks.schemas import SnackResponse


class StockInfo(BaseModel):
    """Stock information for response"""
    id: str
    quantity_now: int
    snack: Optional[SnackResponse] = None

    class Config:
        from_attributes = True


class SaleSnackBase(BaseModel):
    snack_id: str  # API receives snack_id
    quantity: int


class SaleSnackCreate(SaleSnackBase):
    pass


class SaleSnackResponse(BaseModel):
    id: str
    sale_id: str
    quantity: int
    stock_id: str
    stock: Optional[StockInfo] = None

    class Config:
        from_attributes = True


class SaleItemDetail(BaseModel):
    """Snack item detail in sale response"""
    snack_name: str
    price: float
    quantity: int


class SaleCreateResponse(BaseModel):
    """Response for creating a sale"""
    member_name: Optional[str] = None
    items: List[SaleItemDetail] = []
    total_price: float


class SaleBase(BaseModel):
    operator: Optional[str] = None


class SaleCreate(SaleBase):
    timestamp: Optional[datetime] = None
    sale_snacks: List[SaleSnackCreate] = []


class SaleUpdate(BaseModel):
    operator: Optional[str] = None
    timestamp: Optional[datetime] = None


class SaleResponse(SaleBase):
    id: str
    timestamp: datetime
    sale_snacks: List[SaleSnackResponse] = []

    class Config:
        from_attributes = True
