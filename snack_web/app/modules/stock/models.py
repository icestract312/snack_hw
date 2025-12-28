from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base
import datetime


class Stock(Base):
    __tablename__ = "stock"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    create_at = Column(DateTime, default=datetime.datetime.utcnow)
    snack_id = Column(String, ForeignKey("snacks.barcode"))
    snack = relationship("Snack")
    quantity = Column(Integer)
    quantity_now = Column(Integer)
