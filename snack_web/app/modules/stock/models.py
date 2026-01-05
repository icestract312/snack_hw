from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, text, CheckConstraint
from sqlalchemy.orm import relationship, validates
from app.core.database import Base
import datetime
import uuid

class Stock(Base):
    __tablename__ = "stock"
    __table_args__ = (
        CheckConstraint('quantity_now <= quantity', name='check_quantity_limit'),
    )

    id = Column(
        String(36), 
        primary_key=True, 
        default=lambda: str(uuid.uuid4()),
        server_default=text("gen_random_uuid()"), 
        nullable=False
    )
    
    create_at = Column(
        DateTime, 
        default=lambda: datetime.datetime.now(
            datetime.timezone(datetime.timedelta(hours=7))
        ).replace(tzinfo=None), 
        nullable=False,
        server_default=text("(now() at time zone 'utc' + interval '7 hours')")
    )
    snack_id = Column(String, ForeignKey("snacks.barcode"))
    snack = relationship("Snack")
    quantity = Column(Integer)
    quantity_now = Column(Integer)
    @validates('quantity_now')
    def validate_quantity_now(self, key, value):
        if self.quantity is not None and value > self.quantity:
            raise ValueError(f"quantity_now ({value}) cannot be greater than quantity ({self.quantity})")
        return value