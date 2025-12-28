from sqlalchemy.orm import Session
from typing import List, Optional
from . import models


class SnackRepository:
    """Data access layer for Snack operations"""
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[models.Snack]:
        """Retrieve all snacks with pagination"""
        return db.query(models.Snack).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_barcode(db: Session, barcode: str) -> Optional[models.Snack]:
        """Find snack by barcode"""
        return db.query(models.Snack).filter(models.Snack.barcode == barcode).first()

    @staticmethod
    def create(db: Session, snack_data: dict) -> models.Snack:
        """Create a new snack"""
        db_snack = models.Snack(**snack_data)
        db.add(db_snack)
        db.commit()
        db.refresh(db_snack)
        return db_snack

    @staticmethod
    def update(db: Session, db_snack: models.Snack, update_data: dict) -> models.Snack:
        """Update an existing snack"""
        for field, value in update_data.items():
            setattr(db_snack, field, value)
        db.commit()
        db.refresh(db_snack)
        return db_snack

    @staticmethod
    def delete(db: Session, db_snack: models.Snack) -> None:
        """Delete a snack"""
        db.delete(db_snack)
        db.commit()
