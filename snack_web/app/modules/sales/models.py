from sqlalchemy import Column, Integer, String , text, DateTime,func, ForeignKey
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base
import datetime


class Sale(Base):
    __tablename__ = "sales"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()),server_default=text("gen_random_uuid()"), nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.datetime.now(
            datetime.timezone(datetime.timedelta(hours=7))
        ).replace(tzinfo=None), nullable=False,server_default=text("(now() at time zone 'utc' + interval '7 hours')"))
    snack_id = Column(String, ForeignKey("snacks.barcode"))
    snack = relationship("Snack")
    quantity = Column(Integer)
