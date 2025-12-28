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


@router.get("/{member_id}", response_model=schemas.MemberResponse)
def get_member(member_id: str, db: Session = Depends(get_db)):
    """Get a specific member by ID"""
    member_service = service.MemberService(db)
    member = member_service.get_member_by_id(member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    return member


@router.post("/", response_model=schemas.MemberResponse, status_code=201)
def create_member(member: schemas.MemberCreate, db: Session = Depends(get_db)):
    """Create a new member"""
    member_service = service.MemberService(db)
    return member_service.create_member(member)


@router.put("/{member_id}", response_model=schemas.MemberResponse)
def update_member(member_id: str, member: schemas.MemberUpdate, db: Session = Depends(get_db)):
    """Update a member"""
    member_service = service.MemberService(db)
    updated_member = member_service.update_member(member_id, member)
    if not updated_member:
        raise HTTPException(status_code=404, detail="Member not found")
    return updated_member


@router.delete("/{member_id}")
def delete_member(member_id: str, db: Session = Depends(get_db)):
    """Delete a member"""
    member_service = service.MemberService(db)
    if not member_service.delete_member(member_id):
        raise HTTPException(status_code=404, detail="Member not found")
    return {"message": "Member deleted successfully"}
