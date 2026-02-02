from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


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
    snack_name: Optional[str] = None
    create_at: datetime

    class Config:
        from_attributes = True


class PurchaseItem(BaseModel):
    snack_id: str
    quantity: int

    class Config:
        from_attributes = True


class ExcelRowData(BaseModel):
    """Schema for parsed Excel row data"""
    Name: str
    Quantity: Optional[float] = None
    Price: Optional[float] = None
    Unit: Optional[float] = None
    TotalUnit: Optional[float] = None
    PricePerUnit: Optional[float] = None
    SalePrice: Optional[float] = None
    Sheet: str
    Category: str

    class Config:
        from_attributes = True


class ExcelUploadResponse(BaseModel):
    """Response schema for Excel upload"""
    message: str
    total_rows: int
    data: List[ExcelRowData]

    class Config:
        from_attributes = True
