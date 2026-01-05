from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime
from . import models, schemas, repository
from ..snacks import repository as snacks_repository
from ..sales import repository as sales_repository
from ..sales import models as sales_models


class StockService:
    """Business logic layer for Stock operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = repository.StockRepository()
        self.snacks_repository = snacks_repository.SnackRepository()
        self.sales_repository = sales_repository.SaleRepository()

    def get_all_stock(self, skip: int = 0, limit: int = 100) -> List[models.Stock]:
        """Get all stock records with pagination"""
        return self.repository.get_all(self.db, skip, limit)

    def get_stock_by_id(self, stock_id: str) -> Optional[models.Stock]:
        """Get a specific stock record by ID"""
        return self.repository.get_by_id(self.db, stock_id)

    def get_stock_by_snack_id(self, snack_id: str) -> List[models.Stock]:
        """Get all stock records for a specific snack"""
        return self.repository.get_by_snack_id(self.db, snack_id)

    def create_stock(self, stock: schemas.StockCreate) -> models.Stock:
        """
        Create a new stock record
        Business logic: Generate UUID, set timestamp, validate quantities
        """
        # Validate quantities
        if stock.quantity < 0:
            raise ValueError("Quantity cannot be negative")
        if stock.quantity_now < 0:
            raise ValueError("Current quantity cannot be negative")
        if stock.quantity_now > stock.quantity:
            raise ValueError("Current quantity cannot exceed initial quantity")
        
        stock_data = {
            "id": str(uuid.uuid4()),
            "snack_id": stock.snack_id,
            "quantity": stock.quantity,
            "quantity_now": stock.quantity_now
        }
        return self.repository.create(self.db, stock_data)

    def update_stock(self, stock_id: str, stock: schemas.StockUpdate) -> Optional[models.Stock]:
        """
        Update stock information
        Business logic: Validate existence, validate quantities if updated
        """
        db_stock = self.repository.get_by_id(self.db, stock_id)
        if not db_stock:
            return None
        
        update_data = stock.model_dump(exclude_unset=True)
        if not update_data:
            return db_stock
        
        # Validate quantities if being updated
        if "quantity" in update_data and update_data["quantity"] < 0:
            raise ValueError("Quantity cannot be negative")
        if "quantity_now" in update_data and update_data["quantity_now"] < 0:
            raise ValueError("Current quantity cannot be negative")
        
        return self.repository.update(self.db, db_stock, update_data)

    def delete_stock(self, stock_id: str) -> bool:
        """
        Delete a stock record
        Business logic: Check if stock exists before deletion
        """
        db_stock = self.repository.get_by_id(self.db, stock_id)
        if not db_stock:
            return False
        
        self.repository.delete(self.db, db_stock)
        return True

    def adjust_stock_quantity(self, stock_id: str, quantity_change: int) -> Optional[models.Stock]:
        """
        Adjust stock quantity (e.g., for sales or restocking)
        Business logic: Ensure quantity doesn't go negative
        """
        db_stock = self.repository.get_by_id(self.db, stock_id)
        if not db_stock:
            return None
        
        new_quantity = db_stock.quantity_now + quantity_change
        if new_quantity < 0:
            raise ValueError("Insufficient stock quantity")
        
        update_data = {"quantity_now": new_quantity}
        return self.repository.update(self.db, db_stock, update_data)

    def process_sales(self, sale_requests: List[schemas.BarcodeStockRequest]) -> List[sales_models.Sale]:
        """
        Process multiple sales transactions
        Business logic:
        1. Check each barcode exists in snacks table
        2. Find latest stock with quantity_now > 0
        3. Check sufficient quantity available
        4. Decrease quantity_now in stock
        5. Create sale record with timestamp
        """
        created_sales = []
        transaction_timestamp = datetime.now()
        
        for request in sale_requests:
            # Check if snack exists
            snack = self.snacks_repository.get_by_barcode(self.db, request.barcode)
            if not snack:
                raise ValueError(f"Snack with barcode {request.barcode} not found")
            
            # Get latest stock with quantity_now > 0
            stock = self.repository.get_latest_stock_by_barcode(self.db, request.barcode)
            if not stock:
                raise ValueError(f"No available stock for snack {request.barcode}")
            
            # Check if sufficient quantity available
            if stock.quantity_now < request.quantity:
                raise ValueError(
                    f"Insufficient stock for {request.barcode}. "
                    f"Available: {stock.quantity_now}, Requested: {request.quantity}"
                )
            
            # Decrease quantity_now in stock
            new_quantity_now = stock.quantity_now - request.quantity
            update_data = {"quantity_now": new_quantity_now}
            self.repository.update(self.db, stock, update_data)
            
            # Create sale record
            sale_data = {
                "id": str(uuid.uuid4()),
                "timestamp": transaction_timestamp,
                "snack_id": request.barcode,
                "quantity": request.quantity
            }
            sale = self.sales_repository.create(self.db, sale_data)
            created_sales.append(sale)
        
        return created_sales
