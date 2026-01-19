from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
from . import models, schemas, repository
from app.modules.stock.models import Stock


class SaleService:
    """Business logic layer for Sale operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = repository.SaleRepository()

    def get_all_sales(self, skip: int = 0, limit: int = 100) -> List[models.Sale]:
        """Get all sales with pagination and assemble response objects"""
        sales = self.repository.get_all(self.db, skip, limit)
        result = []
        for s in sales:
            # compute total and items
            total = 0.0
            items = []
            for ss in getattr(s, "sale_snacks", []):
                snack = None
                price = 0.0
                if getattr(ss, "stock", None) and getattr(ss.stock, "snack", None):
                    snack = ss.stock.snack
                    price = float(getattr(snack, "price", 0.0) or 0.0)
                qty = int(getattr(ss, "quantity", 0) or 0)
                total += price * qty
                items.append({
                    "id": ss.id,
                    "quantity": qty,
                    "snack_name": getattr(snack, "name", None) if snack else None,
                    "price": price,
                })

            operator = None
            if getattr(s, "member", None):
                member = s.member
                operator = f"{getattr(member, 'name', '')} {getattr(member, 'member_class', '')}".strip()

            result.append({
                "operator": operator,
                "id": s.id,
                "timestamp": s.timestamp,
                "total_price": total,
                "sale_snacks": items,
            })
        return result

    def get_sale_by_id(self, sale_id: str) -> Optional[models.Sale]:
        """Get a specific sale by ID and assemble response object"""
        s = self.repository.get_by_id(self.db, sale_id)
        if not s:
            return None

        total = 0.0
        items = []
        for ss in getattr(s, "sale_snacks", []):
            snack = None
            price = 0.0
            if getattr(ss, "stock", None) and getattr(ss.stock, "snack", None):
                snack = ss.stock.snack
                price = float(getattr(snack, "price", 0.0) or 0.0)
            qty = int(getattr(ss, "quantity", 0) or 0)
            total += price * qty
            items.append({
                "id": ss.id,
                "quantity": qty,
                "snack_name": getattr(snack, "name", None) if snack else None,
                "price": price,
            })

        operator = None
        if getattr(s, "member", None):
            member = s.member
            operator = f"{getattr(member, 'name', '')} {getattr(member, 'member_class', '')}".strip()

        return {
            "operator": operator,
            "id": s.id,
            "timestamp": s.timestamp,
            "total_price": total,
            "sale_snacks": items,
        }

    def create_sale(self, sale: schemas.SaleCreate) -> dict:
        """
        Create a new sale with sale_snacks
        Business logic: Generate UUID, set timestamp, validate stock availability
        Returns: Custom format with member_name, items, and total_price
        """
        # Validate sale_snacks
        if not sale.sale_snacks:
            raise ValueError("Sale must have at least one item")
        
        for ss in sale.sale_snacks:
            if ss.quantity <= 0:
                raise ValueError("Quantity must be greater than 0")
        
        # Prepare sale data
        sale_data = {
            "id": str(uuid.uuid4()),
            "timestamp": sale.timestamp or datetime.now(timezone(timedelta(hours=7))).replace(tzinfo=None),
            "operator": sale.operator,
        }
        
        # Validate stock and prepare sale_snacks data
        sale_snacks_data = []
        items = []
        total_price = 0.0
        
        for ss in sale.sale_snacks:
            # Find available stock for this snack
            stock = (
                self.db.query(Stock)
                .filter(
                    Stock.snack_id == ss.snack_id,
                    Stock.quantity_now >= ss.quantity
                )
                .order_by(Stock.create_at.asc())  # FIFO: oldest stock first
                .first()
            )
            
            if not stock:
                raise ValueError(
                    f"Insufficient stock for snack {ss.snack_id}. "
                    f"Required: {ss.quantity}, Available: 0 or not found"
                )
            
            # Deduct stock quantity
            stock.quantity_now -= ss.quantity
            
            # Calculate item total
            item_price = stock.snack.price if stock.snack else 0.0
            total_price += item_price * ss.quantity
            
            # Add to items list
            items.append({
                "snack_name": stock.snack.name if stock.snack else "Unknown",
                "price": item_price,
                "quantity": ss.quantity,
            })
            
            sale_snacks_data.append({
                "id": str(uuid.uuid4()),
                "stock_id": stock.id,
                "quantity": ss.quantity,
            })
        
        # Create the sale in database
        db_sale = self.repository.create(self.db, sale_data, sale_snacks_data)
        
        # Get member name if operator is provided
        member_name = None
        member_class = None
        if db_sale.member:
            member_name = db_sale.member.name
            member_class = db_sale.member.member_class
        
        # Return custom response
        return {
            "member_name": member_name+" "+member_class,
            "items": items,
            "total_price": total_price,
        }

    def update_sale(self, sale_id: str, sale: schemas.SaleUpdate) -> Optional[models.Sale]:
        """
        Update sale information (operator, timestamp)
        Business logic: Validate existence
        """
        db_sale = self.repository.get_by_id(self.db, sale_id)
        if not db_sale:
            return None
        
        update_data = sale.model_dump(exclude_unset=True)
        if not update_data:
            return db_sale
        
        return self.repository.update(self.db, db_sale, update_data)

    def delete_sale(self, sale_id: str) -> bool:
        """
        Delete a sale and its sale_snacks
        Business logic: Check if sale exists before deletion
        """
        db_sale = self.repository.get_by_id(self.db, sale_id)
        if not db_sale:
            return False
        
        self.repository.delete(self.db, db_sale)
        return True
