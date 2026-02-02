from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime
import io
import pandas as pd
import numpy as np
import math
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
        stocks = self.repository.get_all(self.db, skip, limit)
        return [self._serialize_stock(s) for s in stocks]

    def get_stock_by_id(self, stock_id: str) -> Optional[models.Stock]:
        """Get a specific stock record by ID"""
        stock = self.repository.get_by_id(self.db, stock_id)
        return self._serialize_stock(stock) if stock else None

    def get_stock_by_snack_id(self, snack_id: str) -> List[models.Stock]:
        """Get all stock records for a specific snack"""
        stocks = self.repository.get_by_snack_id(self.db, snack_id)
        return [self._serialize_stock(s) for s in stocks]

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
        db_stock = self.repository.create(self.db, stock_data)
        return self._serialize_stock(db_stock)

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
        
        updated = self.repository.update(self.db, db_stock, update_data)
        return self._serialize_stock(updated)

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
        updated = self.repository.update(self.db, db_stock, update_data)
        return self._serialize_stock(updated)

    def _serialize_stock(self, stock: Optional[models.Stock]) -> Optional[dict]:
        """Return a serializable dict for a stock record including snack name"""
        if not stock:
            return None
        return {
            "snack_id": stock.snack_id,
            "snack_name": stock.snack.name if getattr(stock, "snack", None) else None,
            "quantity": stock.quantity,
            "quantity_now": stock.quantity_now,
            "id": stock.id,
            "create_at": stock.create_at,
        }

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

    def process_excel_file(self, file_content: bytes) -> dict:
        """
        Process Excel file with multiple sheets and tables
        Returns parsed data in structured format
        """
        try:
            # Load the Excel file from bytes
            xls = pd.read_excel(io.BytesIO(file_content), sheet_name=None, header=None)
        except Exception as e:
            raise ValueError(f"Could not read Excel file: {e}")

        all_data_frames = []
        standard_columns = ["Name", "Quantity", "Price", "Unit", "TotalUnit", "PricePerUnit", "SalePrice"]

        for sheet_name, df in xls.items():
            # 1. Find the header row (looking for "Name" and "Quantity")
            header_row_idx = None
            for i, row in df.iterrows():
                row_str = row.astype(str).tolist()
                if "Name" in row_str and "Quantity" in row_str:
                    header_row_idx = i
                    break
            
            if header_row_idx is None:
                continue  # Skip sheets without the expected structure

            header_row = df.iloc[header_row_idx]
            num_cols = df.shape[1]

            # 2. Scan columns to find side-by-side tables
            for c in range(num_cols):
                val = str(header_row[c]).strip()
                
                if val == "Name":
                    # Determine block size (approx 7 columns)
                    end_col = min(c + 7, num_cols)
                    
                    # Extract data block
                    sub_df = df.iloc[header_row_idx+1:, c:end_col].copy()
                    
                    # Standardize columns
                    if sub_df.shape[1] == 7:
                        sub_df.columns = standard_columns
                    else:
                        sub_df.columns = standard_columns[:sub_df.shape[1]]

                    # 3. Get Category (e.g., Makro, Pepsi) from the row above header
                    category = "Unknown"
                    if header_row_idx > 0:
                        cat_val = df.iloc[header_row_idx-1, c]
                        if pd.notna(cat_val):
                            category = str(cat_val).strip()

                    # Add metadata
                    sub_df["Sheet"] = sheet_name
                    sub_df["Category"] = category
                    
                    # Filter valid rows
                    sub_df = sub_df[sub_df["Name"].notna()]
                    
                    all_data_frames.append(sub_df)

        if not all_data_frames:
            raise ValueError("No valid data tables found in the provided file.")

        # Combine all data
        final_df = pd.concat(all_data_frames, ignore_index=True)

        # Convert numeric columns
        cols_to_numeric = ["Quantity", "Price", "Unit", "TotalUnit", "PricePerUnit", "SalePrice"]
        for col in cols_to_numeric:
            if col in final_df.columns:
                final_df[col] = pd.to_numeric(final_df[col], errors='coerce')

        # Replace infinite values with NaN
        final_df = final_df.replace([np.inf, -np.inf], np.nan)

        # Drop rows where all numeric columns are missing
        final_df = final_df.dropna(subset=cols_to_numeric, how='all')

        # Convert remaining NaN to None for JSON serialization
        final_df = final_df.where(pd.notnull(final_df), None)

        # Convert to list of dictionaries
        raw_list = final_df.to_dict('records')

        # Sanitize values: convert numpy types to native Python and replace non-finite floats
        def sanitize_value(v):
            if v is None:
                return None
            # numpy integer
            if isinstance(v, (np.integer,)):
                return int(v)
            # numpy floating or python float
            if isinstance(v, (np.floating, float)):
                try:
                    fv = float(v)
                except Exception:
                    return None
                if not math.isfinite(fv):
                    return None
                return fv
            # numpy boolean
            if isinstance(v, (np.bool_,)):
                return bool(v)
            return v

        data_list = []
        for rec in raw_list:
            sanitized = {k: sanitize_value(v) for k, v in rec.items()}
            data_list.append(sanitized)

        return {
            "message": "Excel file processed successfully",
            "total_rows": len(data_list),
            "data": data_list
        }

    def transform_excel_to_file(self, file_content: bytes) -> io.BytesIO:
        """
        Reads raw Excel bytes, processes all sheets/tables, and returns 
        a BytesIO object containing the formatted Excel file.
        """
        try:
            # Load the Excel file from bytes
            xls = pd.read_excel(io.BytesIO(file_content), sheet_name=None, header=None)
        except Exception as e:
            raise ValueError(f"Could not read Excel file: {e}")

        all_data_frames = []
        standard_columns = ["Name", "Quantity", "Price", "Unit", "TotalUnit", "PricePerUnit", "SalePrice"]

        for sheet_name, df in xls.items():
            # 1. Find the header row (looking for "Name" and "Quantity")
            header_row_idx = None
            for i, row in df.iterrows():
                row_str = row.astype(str).tolist()
                if "Name" in row_str and "Quantity" in row_str:
                    header_row_idx = i
                    break
            
            if header_row_idx is None:
                continue  # Skip sheets without the expected structure

            header_row = df.iloc[header_row_idx]
            num_cols = df.shape[1]

            # 2. Scan columns to find side-by-side tables
            for c in range(num_cols):
                val = str(header_row[c]).strip()
                
                if val == "Name":
                    # Determine block size (approx 7 columns)
                    end_col = min(c + 7, num_cols)
                    
                    # Extract data block
                    sub_df = df.iloc[header_row_idx+1:, c:end_col].copy()
                    
                    # Standardize columns
                    if sub_df.shape[1] == 7:
                        sub_df.columns = standard_columns
                    else:
                        sub_df.columns = standard_columns[:sub_df.shape[1]]

                    # 3. Get Category (e.g., Makro, Pepsi) from the row above header
                    category = "Unknown"
                    if header_row_idx > 0:
                        cat_val = df.iloc[header_row_idx-1, c]
                        if pd.notna(cat_val):
                            category = str(cat_val).strip()

                    # Add metadata
                    sub_df["Sheet"] = sheet_name
                    sub_df["Category"] = category
                    
                    # Filter valid rows
                    sub_df = sub_df[sub_df["Name"].notna()]
                    
                    all_data_frames.append(sub_df)

        if not all_data_frames:
            raise ValueError("No valid data tables found in the provided file.")

        # Combine all data
        final_df = pd.concat(all_data_frames, ignore_index=True)

        # Convert numeric columns
        cols_to_numeric = ["Quantity", "Price", "Unit", "TotalUnit", "PricePerUnit", "SalePrice"]
        for col in cols_to_numeric:
            if col in final_df.columns:
                final_df[col] = pd.to_numeric(final_df[col], errors='coerce')

        # Save to buffer
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            final_df.to_excel(writer, index=False, sheet_name="MergedData")
        
        output.seek(0)
        return output
