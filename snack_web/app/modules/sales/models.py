from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base
import datetime


class Sale(Base):
    __tablename__ = "sales"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime)
    snack_id = Column(String, ForeignKey("snacks.barcode"))
    snack = relationship("Snack")
    quantity = Column(Integer)
