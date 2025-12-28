from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from . import models


class MemberRepository:
    """Data access layer for Member operations"""
    
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[models.Member]:
        """Retrieve all members with pagination"""
        return db.query(models.Member).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_id(db: Session, member_id: str) -> Optional[models.Member]:
        """Find member by ID"""
        return db.query(models.Member).filter(models.Member.id == member_id).first()

    @staticmethod
    def create(db: Session, member_data: dict) -> models.Member:
        """Create a new member"""
        db_member = models.Member(**member_data)
        db.add(db_member)
        db.commit()
        db.refresh(db_member)
        return db_member

    @staticmethod
    def update(db: Session, db_member: models.Member, update_data: dict) -> models.Member:
        """Update an existing member"""
        for field, value in update_data.items():
            setattr(db_member, field, value)
        db.commit()
        db.refresh(db_member)
        return db_member

    @staticmethod
    def delete(db: Session, db_member: models.Member) -> None:
        """Delete a member"""
        db.delete(db_member)
        db.commit()
