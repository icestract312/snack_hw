from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from . import service, schemas

router = APIRouter(prefix="/snacks", tags=["snacks"])


@router.get("/", response_model=List[schemas.SnackResponse])
def get_snacks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all snacks"""
    snack_service = service.SnackService(db)
    return snack_service.get_all_snacks(skip=skip, limit=limit)


@router.get("/{barcode}", response_model=schemas.SnackResponse)
def get_snack(barcode: str, db: Session = Depends(get_db)):
    """Get a specific snack by barcode"""
    snack_service = service.SnackService(db)
    snack = snack_service.get_snack_by_barcode(barcode)
    if not snack:
        raise HTTPException(status_code=404, detail="Snack not found")
    return snack


@router.post("/", response_model=schemas.SnackResponse, status_code=201)
def create_snack(snack: schemas.SnackCreate, db: Session = Depends(get_db)):
    """Create a new snack"""
    snack_service = service.SnackService(db)
    try:
        return snack_service.create_snack(snack)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{barcode}", response_model=schemas.SnackResponse)
def update_snack(barcode: str, snack: schemas.SnackUpdate, db: Session = Depends(get_db)):
    """Update a snack"""
    snack_service = service.SnackService(db)
    try:
        updated_snack = snack_service.update_snack(barcode, snack)
        if not updated_snack:
            raise HTTPException(status_code=404, detail="Snack not found")
        return updated_snack
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{barcode}")
def delete_snack(barcode: str, db: Session = Depends(get_db)):
    """Delete a snack"""
    snack_service = service.SnackService(db)
    if not snack_service.delete_snack(barcode):
        raise HTTPException(status_code=404, detail="Snack not found")
    return {"message": "Snack deleted successfully"}
