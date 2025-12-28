from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from . import service, schemas

router = APIRouter(prefix="/stock", tags=["stock"])


@router.get("/", response_model=List[schemas.StockResponse])
def get_stock(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all stock records"""
    stock_service = service.StockService(db)
    return stock_service.get_all_stock(skip=skip, limit=limit)


@router.get("/{stock_id}", response_model=schemas.StockResponse)
def get_stock_by_id(stock_id: str, db: Session = Depends(get_db)):
    """Get a specific stock record by ID"""
    stock_service = service.StockService(db)
    stock = stock_service.get_stock_by_id(stock_id)
    if not stock:
        raise HTTPException(status_code=404, detail="Stock record not found")
    return stock


@router.get("/snack/{snack_id}", response_model=List[schemas.StockResponse])
def get_stock_by_snack(snack_id: str, db: Session = Depends(get_db)):
    """Get all stock records for a specific snack"""
    stock_service = service.StockService(db)
    return stock_service.get_stock_by_snack_id(snack_id)


@router.post("/", response_model=schemas.StockResponse, status_code=201)
def create_stock(stock: schemas.StockCreate, db: Session = Depends(get_db)):
    """Create a new stock record"""
    stock_service = service.StockService(db)
    try:
        return stock_service.create_stock(stock)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{stock_id}", response_model=schemas.StockResponse)
def update_stock(stock_id: str, stock: schemas.StockUpdate, db: Session = Depends(get_db)):
    """Update a stock record"""
    stock_service = service.StockService(db)
    try:
        updated_stock = stock_service.update_stock(stock_id, stock)
        if not updated_stock:
            raise HTTPException(status_code=404, detail="Stock record not found")
        return updated_stock
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{stock_id}")
def delete_stock(stock_id: str, db: Session = Depends(get_db)):
    """Delete a stock record"""
    stock_service = service.StockService(db)
    if not stock_service.delete_stock(stock_id):
        raise HTTPException(status_code=404, detail="Stock record not found")
    return {"message": "Stock record deleted successfully"}
