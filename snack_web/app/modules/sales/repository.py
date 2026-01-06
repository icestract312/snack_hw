from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
import uuid
from datetime import datetime
from . import models


class SaleRepository:
    """Data access layer for Sale operations"""
    
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[models.Sale]:
        """Retrieve all sales with pagination"""
        return db.query(models.Sale).options(joinedload(models.Sale.snack)).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_id(db: Session, sale_id: str) -> Optional[models.Sale]:
        """Find sale by ID"""
        return db.query(models.Sale).options(joinedload(models.Sale.snack)).filter(models.Sale.id == sale_id).first()

    @staticmethod
    def create(db: Session, sale_data: dict) -> models.Sale:
        """Create a new sale"""
        db_sale = models.Sale(**sale_data)
        db.add(db_sale)
        db.commit()
        db.refresh(db_sale)
        # Load the snack relationship
        db.refresh(db_sale, ["snack"])
        return db_sale

    @staticmethod
    def update(db: Session, db_sale: models.Sale, update_data: dict) -> models.Sale:
        """Update an existing sale"""
        for field, value in update_data.items():
            setattr(db_sale, field, value)
        db.commit()
        db.refresh(db_sale)
        # Load the snack relationship
        db.refresh(db_sale, ["snack"])
        return db_sale

    @staticmethod
    def delete(db: Session, db_sale: models.Sale) -> None:
        """Delete a sale"""
        db.delete(db_sale)
        db.commit()
