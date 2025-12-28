import uuid
from sqlalchemy import Column, String
from app.core.database import Base


class Member(Base):
    __tablename__ = "members"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String)
    member_class = Column(String)
