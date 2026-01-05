from sqlalchemy import Column, String, Float
from app.core.database import Base


class Snack(Base):
    __tablename__ = "snacks"
    barcode = Column(String, primary_key=True, index=True, nullable=False)
    name = Column(String)
    price = Column(Float)
