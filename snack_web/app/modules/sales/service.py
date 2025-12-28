from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime
from . import models, schemas, repository


class SaleService:
    """Business logic layer for Sale operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = repository.SaleRepository()

    def get_all_sales(self, skip: int = 0, limit: int = 100) -> List[models.Sale]:
        """Get all sales with pagination"""
        return self.repository.get_all(self.db, skip, limit)

    def get_sale_by_id(self, sale_id: str) -> Optional[models.Sale]:
        """Get a specific sale by ID"""
        return self.repository.get_by_id(self.db, sale_id)

    def create_sale(self, sale: schemas.SaleCreate) -> models.Sale:
        """
        Create a new sale
        Business logic: Generate UUID, set timestamp, validate quantity
        """
        # Validate quantity
        if sale.quantity <= 0:
            raise ValueError("Quantity must be greater than 0")
        
        sale_data = {
            "id": str(uuid.uuid4()),
            "timestamp": sale.timestamp or datetime.utcnow(),
            "snack_id": sale.snack_id,
            "quantity": sale.quantity
        }
        return self.repository.create(self.db, sale_data)

    def update_sale(self, sale_id: str, sale: schemas.SaleUpdate) -> Optional[models.Sale]:
        """
        Update sale information
        Business logic: Validate existence, validate quantity if updated
        """
        db_sale = self.repository.get_by_id(self.db, sale_id)
        if not db_sale:
            return None
        
        update_data = sale.model_dump(exclude_unset=True)
        if not update_data:
            return db_sale
        
        # Validate quantity if being updated
        if "quantity" in update_data and update_data["quantity"] <= 0:
            raise ValueError("Quantity must be greater than 0")
        
        return self.repository.update(self.db, db_sale, update_data)

    def delete_sale(self, sale_id: str) -> bool:
        """
        Delete a sale
        Business logic: Check if sale exists before deletion
        """
        db_sale = self.repository.get_by_id(self.db, sale_id)
        if not db_sale:
            return False
        
        self.repository.delete(self.db, db_sale)
        return True
