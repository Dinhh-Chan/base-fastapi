# app/crud/base.py
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union, Callable
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete, asc, desc, or_, and_, func
from sqlalchemy.sql.expression import ColumnElement

from app.db.base_class import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        
        **Parameters**
        
        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """
        Get a single record by ID.
        """
        return db.execute(select(self.model).filter(self.model.id == id)).scalars().first()
        
    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """
        Get multiple records with pagination.
        """
        return db.execute(
            select(self.model).offset(skip).limit(limit)
        ).scalars().all()
        
    def get_all(self, db: Session) -> List[ModelType]:
        """
        Get all records without pagination.
        """
        return db.execute(select(self.model)).scalars().all()
        
    def get_multi_paginated(
        self, 
        db: Session, 
        *, 
        page: int = 1, 
        page_size: int = 20,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ) -> Dict[str, Any]:
        """
        Get multiple records with advanced pagination and sorting.
        
        Args:
            db: Database session
            page: Page number (1-indexed)
            page_size: Items per page
            sort_by: Column name to sort by
            sort_order: Sort direction ('asc' or 'desc')
            
        Returns:
            Dict with items, pagination metadata and sorting info
        """
        # Ensure positive values
        page = max(1, page)
        page_size = max(1, min(100, page_size))  # Limit page size to 100
        
        # Calculate offset
        skip = (page - 1) * page_size
        
        # Create base query
        query = select(self.model)
        
        # Apply sorting if specified
        if sort_by and hasattr(self.model, sort_by):
            sort_column = getattr(self.model, sort_by)
            if sort_order.lower() == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))
        
        # Get total count - Fix for SQLAlchemy 2.0
        count_query = select(func.count()).select_from(self.model)
        total_count = db.execute(count_query).scalar() or 0
        
        # Apply pagination
        query = query.offset(skip).limit(page_size)
        
        # Execute query
        items = db.execute(query).scalars().all()
        
        # Convert SQLAlchemy objects to dictionaries for JSON serialization
        serialized_items = [jsonable_encoder(item) for item in items]
        
        # Calculate pagination metadata
        total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 0
        has_next = page < total_pages
        has_prev = page > 1
        
        # Return items and metadata
        return {
            "items": serialized_items,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_items": total_count,
                "total_pages": total_pages,
                "has_next": has_next,
                "has_prev": has_prev,
                "next_page": page + 1 if has_next else None,
                "prev_page": page - 1 if has_prev else None
            },
            "sorting": {
                "sort_by": sort_by,
                "sort_order": sort_order
            }
        }
        
    def filter_by(
        self, 
        db: Session, 
        *, 
        filters: Dict[str, Any],
        page: int = 1, 
        page_size: int = 20,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ) -> Dict[str, Any]:
        """
        Get records that match given filter criteria with pagination.
        
        Args:
            db: Database session
            filters: Dict of {column_name: value} to filter by
            page: Page number (1-indexed)
            page_size: Items per page
            sort_by: Column name to sort by
            sort_order: Sort direction ('asc' or 'desc')
            
        Returns:
            Dict with filtered items, pagination metadata and sorting info
        """
        # Ensure positive values
        page = max(1, page)
        page_size = max(1, min(100, page_size))
        
        # Calculate offset
        skip = (page - 1) * page_size
        
        # Build filter conditions
        filter_conditions = []
        for column_name, value in filters.items():
            if hasattr(self.model, column_name):
                column = getattr(self.model, column_name)
                if isinstance(value, str) and '%' in value:
                    # For string with wildcards, use LIKE
                    filter_conditions.append(column.like(value))
                elif isinstance(value, list):
                    # For list, use IN
                    filter_conditions.append(column.in_(value))
                else:
                    # For exact match
                    filter_conditions.append(column == value)
        
        # Create queries with filters
        base_query = select(self.model)
        
        if filter_conditions:
            base_query = base_query.filter(and_(*filter_conditions))
        
        # Get total count of filtered items - Fix for SQLAlchemy 2.0
        if filter_conditions:
            count_query = select(func.count()).select_from(self.model).filter(and_(*filter_conditions))
        else:
            count_query = select(func.count()).select_from(self.model)
        
        total_count = db.execute(count_query).scalar() or 0
        
        # Apply sorting if specified
        if sort_by and hasattr(self.model, sort_by):
            sort_column = getattr(self.model, sort_by)
            if sort_order.lower() == "desc":
                base_query = base_query.order_by(desc(sort_column))
            else:
                base_query = base_query.order_by(asc(sort_column))
        
        # Apply pagination
        base_query = base_query.offset(skip).limit(page_size)
        
        # Execute query
        items = db.execute(base_query).scalars().all()
        
        # Convert SQLAlchemy objects to dictionaries for JSON serialization
        serialized_items = [jsonable_encoder(item) for item in items]
        
        # Calculate pagination metadata
        total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 0
        has_next = page < total_pages
        has_prev = page > 1
        
        # Return items and metadata
        return {
            "items": serialized_items,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_items": total_count,
                "total_pages": total_pages,
                "has_next": has_next,
                "has_prev": has_prev,
                "next_page": page + 1 if has_next else None,
                "prev_page": page - 1 if has_prev else None
            },
            "filters": filters,
            "sorting": {
                "sort_by": sort_by,
                "sort_order": sort_order
            }
        }
        
    def search(
        self, 
        db: Session, 
        *, 
        search_term: str,
        search_columns: List[str],
        page: int = 1, 
        page_size: int = 20,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ) -> Dict[str, Any]:
        """
        Search for records matching a search term across specified columns.
        
        Args:
            db: Database session
            search_term: Term to search for
            search_columns: List of column names to search in
            page: Page number (1-indexed)
            page_size: Items per page
            sort_by: Column name to sort by
            sort_order: Sort direction ('asc' or 'desc')
            
        Returns:
            Dict with search results, pagination metadata and sorting info
        """
        # Ensure positive values
        page = max(1, page)
        page_size = max(1, min(100, page_size))
        
        # Calculate offset
        skip = (page - 1) * page_size
        
        # Build search conditions
        search_conditions = []
        for column_name in search_columns:
            if hasattr(self.model, column_name):
                column = getattr(self.model, column_name)
                # For text columns, use ILIKE for case-insensitive search
                search_conditions.append(column.ilike(f"%{search_term}%"))
        
        # Create queries with search conditions
        base_query = select(self.model)
        
        if search_conditions:
            base_query = base_query.filter(or_(*search_conditions))
        
        # Get total count of search results - Fix for SQLAlchemy 2.0
        if search_conditions:
            count_query = select(func.count()).select_from(self.model).filter(or_(*search_conditions))
        else:
            count_query = select(func.count()).select_from(self.model)
        
        total_count = db.execute(count_query).scalar() or 0
        
        # Apply sorting if specified
        if sort_by and hasattr(self.model, sort_by):
            sort_column = getattr(self.model, sort_by)
            if sort_order.lower() == "desc":
                base_query = base_query.order_by(desc(sort_column))
            else:
                base_query = base_query.order_by(asc(sort_column))
        
        # Apply pagination
        base_query = base_query.offset(skip).limit(page_size)
        
        # Execute query
        items = db.execute(base_query).scalars().all()
        
        # Convert SQLAlchemy objects to dictionaries for JSON serialization
        serialized_items = [jsonable_encoder(item) for item in items]
        
        # Calculate pagination metadata
        total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 0
        has_next = page < total_pages
        has_prev = page > 1
        
        # Return items and metadata
        return {
            "items": serialized_items,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_items": total_count,
                "total_pages": total_pages,
                "has_next": has_next,
                "has_prev": has_prev,
                "next_page": page + 1 if has_next else None,
                "prev_page": page - 1 if has_prev else None
            },
            "search": {
                "term": search_term,
                "columns": search_columns
            },
            "sorting": {
                "sort_by": sort_by,
                "sort_order": sort_order
            }
        }

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Create a new record.
        """
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        Update a record.
        """
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> ModelType:
        """
        Remove a record.
        """
        obj = db.execute(select(self.model).filter(self.model.id == id)).scalars().first()
        db.delete(obj)
        db.commit()
        return obj
        
    def exists(self, db: Session, *, id: int) -> bool:
        """
        Check if a record exists.
        """
        result = db.execute(
            select(func.count()).select_from(self.model).filter(self.model.id == id)
        ).scalar()
        return bool(result and result > 0)
        
    def count(self, db: Session) -> int:
        """
        Count all records.
        """
        return db.execute(select(func.count()).select_from(self.model)).scalar() or 0

    def bulk_create(self, db: Session, *, objs_in: List[CreateSchemaType]) -> List[ModelType]:
        """
        Create multiple records at once.
        """
        db_objs = []
        for obj_in in objs_in:
            obj_in_data = jsonable_encoder(obj_in)
            db_obj = self.model(**obj_in_data)  # type: ignore
            db_objs.append(db_obj)
        
        db.add_all(db_objs)
        db.commit()
        for db_obj in db_objs:
            db.refresh(db_obj)
        return db_objs
        
    def bulk_update(
        self, 
        db: Session, 
        *, 
        ids: List[int], 
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> int:
        """
        Update multiple records at once by their IDs.
        
        Returns:
            int: Number of rows updated
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        stmt = (
            update(self.model)
            .where(self.model.id.in_(ids))
            .values(**update_data)
        )
        
        result = db.execute(stmt)
        db.commit()
        return result.rowcount
        
    def bulk_delete(self, db: Session, *, ids: List[int]) -> int:
        """
        Delete multiple records at once by their IDs.
        
        Returns:
            int: Number of rows deleted
        """
        stmt = delete(self.model).where(self.model.id.in_(ids))
        result = db.execute(stmt)
        db.commit()
        return result.rowcount