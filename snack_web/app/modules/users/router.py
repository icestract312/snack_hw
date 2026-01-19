from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from . import service, schemas

router = APIRouter(prefix="/members", tags=["members"])


@router.get("/", response_model=List[schemas.MemberResponse])
def get_members(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all members"""
    member_service = service.MemberService(db)
    return member_service.get_all_members(skip=skip, limit=limit)


@router.get("/{ean13_code}", response_model=schemas.MemberResponse)
def get_member(ean13_code: str, db: Session = Depends(get_db)):
    """Get a specific member by EAN13 code"""
    member_service = service.MemberService(db)
    member = member_service.get_member_by_id(ean13_code)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    return member


@router.post("/", response_model=schemas.MemberResponse, status_code=201)
def create_member(member: schemas.MemberCreate, db: Session = Depends(get_db)):
    """Create a new member"""
    member_service = service.MemberService(db)
    try:
        return member_service.create_member(member)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{ean13_code}", response_model=schemas.MemberResponse)
def update_member(ean13_code: str, member: schemas.MemberUpdate, db: Session = Depends(get_db)):
    """Update a member"""
    member_service = service.MemberService(db)
    updated_member = member_service.update_member(ean13_code, member)
    if not updated_member:
        raise HTTPException(status_code=404, detail="Member not found")
    return updated_member


@router.delete("/{ean13_code}")
def delete_member(ean13_code: str, db: Session = Depends(get_db)):
    """Delete a member"""
    member_service = service.MemberService(db)
    if not member_service.delete_member(ean13_code):
        raise HTTPException(status_code=404, detail="Member not found")
    return {"message": "Member deleted successfully"}
