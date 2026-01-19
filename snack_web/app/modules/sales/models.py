from sqlalchemy import Column, Integer, String, text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base
import datetime


class Sale(Base):
    __tablename__ = "sales"
    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        server_default=text("gen_random_uuid()"),
        nullable=False,
    )
    timestamp = Column(
        DateTime,
        default=lambda: datetime.datetime.now(
            datetime.timezone(datetime.timedelta(hours=7))
        ).replace(tzinfo=None),
        nullable=False,
        server_default=text("(now() at time zone 'utc' + interval '7 hours')"),
    )
    operator = Column(String(13), ForeignKey("members.ean13_code"), nullable=True)
    member = relationship("Member")
    sale_snacks = relationship("SaleSnack", back_populates="sale")


class SaleSnack(Base):
    __tablename__ = "sales_snack"
    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        server_default=text("gen_random_uuid()"),
        nullable=False,
    )
    sale_id = Column(String(36), ForeignKey("sales.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    stock_id = Column(String(36), ForeignKey("stock.id"), nullable=False)
    sale = relationship("Sale", back_populates="sale_snacks")
    stock = relationship("Stock")
