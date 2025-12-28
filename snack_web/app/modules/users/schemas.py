from pydantic import BaseModel
from typing import Optional


class MemberBase(BaseModel):
    name: str
    member_class: str


class MemberCreate(MemberBase):
    pass


class MemberUpdate(BaseModel):
    name: Optional[str] = None
    member_class: Optional[str] = None


class MemberResponse(MemberBase):
    id: str

    class Config:
        from_attributes = True
