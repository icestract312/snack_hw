from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
import uuid
from datetime import datetime
from . import models
from app.modules.stock import models as stock_models


class SaleRepository:
    """Data access layer for Sale operations"""
    
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[models.Sale]:
        """Retrieve all sales with pagination"""
        return (
            db.query(models.Sale)
            .options(
                joinedload(models.Sale.member),
                joinedload(models.Sale.sale_snacks)
                .joinedload(models.SaleSnack.stock)
                .joinedload(stock_models.Stock.snack),
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_by_id(db: Session, sale_id: str) -> Optional[models.Sale]:
        """Find sale by ID"""
        return (
            db.query(models.Sale)
            .options(
                joinedload(models.Sale.member),
                joinedload(models.Sale.sale_snacks)
                .joinedload(models.SaleSnack.stock)
                .joinedload(stock_models.Stock.snack),
            )
            .filter(models.Sale.id == sale_id)
            .first()
        )

    @staticmethod
    def create(db: Session, sale_data: dict, sale_snacks_data: List[dict]) -> models.Sale:
        """Create a new sale with sale_snacks"""
        db_sale = models.Sale(**sale_data)
        db.add(db_sale)
        db.flush()  # Get the sale ID
        
        # Create sale_snacks
        for ss_data in sale_snacks_data:
            db_sale_snack = models.SaleSnack(sale_id=db_sale.id, **ss_data)
            db.add(db_sale_snack)
        
        db.commit()
        db.refresh(db_sale)
        # Load relationships
        db.refresh(db_sale, ["member", "sale_snacks"])
        return db_sale

    @staticmethod
    def update(db: Session, db_sale: models.Sale, update_data: dict) -> models.Sale:
        """Update an existing sale"""
        for field, value in update_data.items():
            setattr(db_sale, field, value)
        db.commit()
        db.refresh(db_sale)
        # Load relationships
        db.refresh(db_sale, ["member", "sale_snacks"])
        return db_sale

    @staticmethod
    def delete(db: Session, db_sale: models.Sale) -> None:
        """Delete a sale and its sale_snacks"""
        # Delete related sale_snacks first
        db.query(models.SaleSnack).filter(models.SaleSnack.sale_id == db_sale.id).delete()
        db.delete(db_sale)
        db.commit()
