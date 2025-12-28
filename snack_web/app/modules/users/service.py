from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from . import models, schemas, repository


class MemberService:
    """Business logic layer for Member operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = repository.MemberRepository()

    def get_all_members(self, skip: int = 0, limit: int = 100) -> List[models.Member]:
        """Get all members with pagination"""
        return self.repository.get_all(self.db, skip, limit)

    def get_member_by_id(self, member_id: str) -> Optional[models.Member]:
        """Get a specific member by ID"""
        return self.repository.get_by_id(self.db, member_id)

    def create_member(self, member: schemas.MemberCreate) -> models.Member:
        """
        Create a new member
        Business logic: Generate UUID, validate data
        """
        member_data = {
            "id": str(uuid.uuid4()),
            "name": member.name,
            "member_class": member.member_class
        }
        return self.repository.create(self.db, member_data)

    def update_member(self, member_id: str, member: schemas.MemberUpdate) -> Optional[models.Member]:
        """
        Update member information
        Business logic: Validate existence, apply partial updates
        """
        db_member = self.repository.get_by_id(self.db, member_id)
        if not db_member:
            return None
        
        update_data = member.model_dump(exclude_unset=True)
        if not update_data:
            return db_member
        
        return self.repository.update(self.db, db_member, update_data)

    def delete_member(self, member_id: str) -> bool:
        """
        Delete a member
        Business logic: Check if member exists before deletion
        """
        db_member = self.repository.get_by_id(self.db, member_id)
        if not db_member:
            return False
        
        self.repository.delete(self.db, db_member)
        return True
