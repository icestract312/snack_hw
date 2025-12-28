from sqlalchemy.orm import Session
from typing import List, Optional
from . import models, schemas, repository


class SnackService:
    """Business logic layer for Snack operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = repository.SnackRepository()

    def get_all_snacks(self, skip: int = 0, limit: int = 100) -> List[models.Snack]:
        """Get all snacks with pagination"""
        return self.repository.get_all(self.db, skip, limit)

    def get_snack_by_barcode(self, barcode: str) -> Optional[models.Snack]:
        """Get a specific snack by barcode"""
        return self.repository.get_by_barcode(self.db, barcode)

    def create_snack(self, snack: schemas.SnackCreate) -> models.Snack:
        """
        Create a new snack
        Business logic: Validate barcode uniqueness, check price > 0
        """
        # Check if snack already exists
        existing = self.repository.get_by_barcode(self.db, snack.barcode)
        if existing:
            raise ValueError(f"Snack with barcode {snack.barcode} already exists")
        
        # Validate price
        if snack.price <= 0:
            raise ValueError("Price must be greater than 0")
        
        snack_data = {
            "barcode": snack.barcode,
            "name": snack.name,
            "price": snack.price
        }
        return self.repository.create(self.db, snack_data)

    def update_snack(self, barcode: str, snack: schemas.SnackUpdate) -> Optional[models.Snack]:
        """
        Update snack information
        Business logic: Validate existence, validate price if updated
        """
        db_snack = self.repository.get_by_barcode(self.db, barcode)
        if not db_snack:
            return None
        
        update_data = snack.model_dump(exclude_unset=True)
        if not update_data:
            return db_snack
        
        # Validate price if being updated
        if "price" in update_data and update_data["price"] <= 0:
            raise ValueError("Price must be greater than 0")
        
        return self.repository.update(self.db, db_snack, update_data)

    def delete_snack(self, barcode: str) -> bool:
        """
        Delete a snack
        Business logic: Check if snack exists before deletion
        """
        db_snack = self.repository.get_by_barcode(self.db, barcode)
        if not db_snack:
            return False
        
        self.repository.delete(self.db, db_snack)
        return True
