from pydantic import BaseModel
from typing import Optional


class MemberBase(BaseModel):
    name: str
    member_class: str


class MemberCreate(MemberBase):
    ean13_code: str


class MemberUpdate(BaseModel):
    name: Optional[str] = None
    member_class: Optional[str] = None


class MemberResponse(MemberBase):
    ean13_code: str

    class Config:
        from_attributes = True
