from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from . import service, schemas

router = APIRouter(prefix="/sales", tags=["sales"])


@router.get("/", response_model=List[schemas.SaleResponse])
def get_sales(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all sales"""
    sale_service = service.SaleService(db)
    return sale_service.get_all_sales(skip=skip, limit=limit)


@router.get("/{sale_id}", response_model=schemas.SaleResponse)
def get_sale(sale_id: str, db: Session = Depends(get_db)):
    """Get a specific sale by ID"""
    sale_service = service.SaleService(db)
    sale = sale_service.get_sale_by_id(sale_id)
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    return sale


@router.post("/", response_model=schemas.SaleResponse, status_code=201)
def create_sale(sale: schemas.SaleCreate, db: Session = Depends(get_db)):
    """Create a new sale"""
    sale_service = service.SaleService(db)
    try:
        return sale_service.create_sale(sale)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{sale_id}", response_model=schemas.SaleResponse)
def update_sale(sale_id: str, sale: schemas.SaleUpdate, db: Session = Depends(get_db)):
    """Update a sale"""
    sale_service = service.SaleService(db)
    try:
        updated_sale = sale_service.update_sale(sale_id, sale)
        if not updated_sale:
            raise HTTPException(status_code=404, detail="Sale not found")
        return updated_sale
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{sale_id}")
def delete_sale(sale_id: str, db: Session = Depends(get_db)):
    """Delete a sale"""
    sale_service = service.SaleService(db)
    if not sale_service.delete_sale(sale_id):
        raise HTTPException(status_code=404, detail="Sale not found")
    return {"message": "Sale deleted successfully"}
