from pydantic import BaseModel
from typing import Optional


class SnackBase(BaseModel):
    name: str
    price: float


class SnackCreate(SnackBase):
    barcode: str


class SnackUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None


class SnackResponse(SnackBase):
    barcode: str

    class Config:
        from_attributes = True
