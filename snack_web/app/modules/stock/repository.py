from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime
from . import models


class StockRepository:
    """Data access layer for Stock operations"""
    
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[models.Stock]:
        """Retrieve all stock records with pagination"""
        return db.query(models.Stock).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_id(db: Session, stock_id: str) -> Optional[models.Stock]:
        """Find stock by ID"""
        return db.query(models.Stock).filter(models.Stock.id == stock_id).first()

    @staticmethod
    def get_by_snack_id(db: Session, snack_id: str) -> List[models.Stock]:
        """Find all stock records for a specific snack"""
        return db.query(models.Stock).filter(models.Stock.snack_id == snack_id).all()

    @staticmethod
    def create(db: Session, stock_data: dict) -> models.Stock:
        """Create a new stock record"""
        db_stock = models.Stock(**stock_data)
        db.add(db_stock)
        db.commit()
        db.refresh(db_stock)
        return db_stock

    @staticmethod
    def update(db: Session, db_stock: models.Stock, update_data: dict) -> models.Stock:
        """Update an existing stock record"""
        for field, value in update_data.items():
            setattr(db_stock, field, value)
        db.commit()
        db.refresh(db_stock)
        return db_stock

    @staticmethod
    def delete(db: Session, db_stock: models.Stock) -> None:
        """Delete a stock record"""
        db.delete(db_stock)
        db.commit()
