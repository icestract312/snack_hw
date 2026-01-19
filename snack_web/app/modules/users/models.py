import uuid
from sqlalchemy import Column, text, String
from app.core.database import Base


class Member(Base):
    __tablename__ = "members"
    ean13_code = Column(String(13), primary_key=True, nullable=False)
    name = Column(String)
    member_class = Column(String)
    
