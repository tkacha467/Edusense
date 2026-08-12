"""Base repository module."""
from typing import TypeVar, Generic, Type, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, func, asc, desc
from datetime import datetime, timezone
from app.database.base import BaseModel

ModelType = TypeVar('ModelType', bound=BaseModel)

class BaseRepository(Generic[ModelType]):
    """Generic base repository for all models."""
    
    def __init__(self, model: Type[ModelType]) -> None:
        """Initialize with model type."""
        self.model = model

    def create(self, db: Session, obj_in: Optional[dict[str, Any]] = None, **kwargs: Any) -> ModelType:
        """Create a new record."""
        data = dict(obj_in) if obj_in else {}
        data.update(kwargs)
        obj = self.model(**data)
        db.add(obj)
        db.flush()
        return obj

    def get_by_id(self, db: Session, entity_id: str) -> ModelType | None:
        """Get a record by ID."""
        stmt = select(self.model).where(self.model.id == entity_id)
        return db.execute(stmt).scalar_one_or_none()



    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> list[ModelType]:
        """Get all records with pagination."""
        stmt = select(self.model).offset(skip).limit(limit)
        return list(db.execute(stmt).scalars().all())

    def update(
        self,
        db: Session,
        entity_id: str = "",
        db_obj: Optional[ModelType] = None,
        obj_in: Optional[dict[str, Any]] = None,
        **kwargs: Any
    ) -> ModelType | None:
        """Update a record by ID or instance with non-None kwargs or dict."""
        obj = db_obj or (self.get_by_id(db, entity_id) if entity_id else None)
        if obj:
            data = dict(obj_in) if obj_in else {}
            data.update(kwargs)
            for key, value in data.items():
                if value is not None and hasattr(obj, key):
                    setattr(obj, key, value)
            db.flush()
        return obj

    def delete(self, db: Session, entity_id: str = "", id: str = "") -> bool:
        """Delete a record by ID."""
        target_id = entity_id or id
        obj = self.get_by_id(db, target_id)
        if obj:
            db.delete(obj)
            db.flush()
            return True
        return False

    def count(self, db: Session) -> int:
        """Get the total count of records."""
        stmt = select(func.count()).select_from(self.model)
        return db.execute(stmt).scalar_one()

    def exists(self, db: Session, entity_id: str) -> bool:
        """Check if a record exists."""
        stmt = select(func.count()).select_from(self.model).where(self.model.id == entity_id)
        count = db.execute(stmt).scalar_one()
        return count > 0

    def get_paginated(
        self,
        db: Session,
        page: int = 1,
        page_size: int = 20,
        order_by: str | None = None,
        order_dir: str = 'asc',
        filters: dict[str, Any] | None = None
    ) -> tuple[list[ModelType], int]:
        """Get paginated records with filtering and sorting."""
        stmt = select(self.model)
        count_stmt = select(func.count()).select_from(self.model)

        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    column = getattr(self.model, key)
                    stmt = stmt.where(column == value)
                    count_stmt = count_stmt.where(column == value)

        total_count = db.execute(count_stmt).scalar_one()

        if order_by and hasattr(self.model, order_by):
            column = getattr(self.model, order_by)
            if order_dir.lower() == 'desc':
                stmt = stmt.order_by(desc(column))
            else:
                stmt = stmt.order_by(asc(column))

        skip = (page - 1) * page_size
        stmt = stmt.offset(skip).limit(page_size)
        items = list(db.execute(stmt).scalars().all())
        
        return items, total_count

    def bulk_create(self, db: Session, items: list[dict[str, Any]]) -> list[ModelType]:
        """Bulk create records."""
        objs = [self.model(**item) for item in items]
        db.add_all(objs)
        db.flush()
        return objs

    def soft_delete(self, db: Session, entity_id: str) -> ModelType | None:
        """Soft delete a record by setting deleted_at."""
        obj = self.get_by_id(db, entity_id)
        if obj and hasattr(obj, 'deleted_at'):
            setattr(obj, 'deleted_at', datetime.now(timezone.utc))
            db.flush()
        return obj
