# app/services/base.py
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union, Tuple
from fastapi.encoders import jsonable_encoder
from fastapi import Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete, func, and_, or_, asc, desc, text
from sqlalchemy.sql.expression import Select

from app.db.base_class import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base class for CRUD operations.
    """

    def __init__(self, model: Type[ModelType]):
        """
        Initialize with SQLAlchemy model class.
        
        Args:
            model: The SQLAlchemy model class
        """
        self.model = model

    async def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """
        Get a record by ID.
        
        Args:
            db: Database session
            id: ID of the record to get
            
        Returns:
            The record if found, None otherwise
        """
        query = select(self.model).where(self.model.id == id)
        result = await db.execute(query)
        return result.scalars().first()

    async def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """
        Get multiple records with pagination.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of records
        """
        query = select(self.model).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_all(self, db: Session) -> List[ModelType]:
        """
        Get all records.
        
        Args:
            db: Database session
            
        Returns:
            List of all records
        """
        query = select(self.model)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_multi_paginated(
        self, 
        db: Session, 
        *, 
        page: int = 1, 
        page_size: int = 10,
        order_by: Optional[str] = None,
        order_direction: Optional[str] = "asc",
        search_fields: Optional[Dict[str, Any]] = None,
        exact_fields: Optional[Dict[str, Any]] = None,
        date_range: Optional[Dict[str, Tuple[str, str]]] = None,
        numeric_range: Optional[Dict[str, Tuple[float, float]]] = None,
        group_by: Optional[str] = None,
        include_total: bool = True
    ) -> Dict[str, Any]:
        """
        Get records with pagination, sorting, and filtering.
        
        Args:
            db: Database session
            page: Page number (1-based)
            page_size: Items per page
            order_by: Field to order by
            order_direction: Direction to order (asc/desc)
            search_fields: Dict of fields to search with LIKE (partial match)
            exact_fields: Dict of fields to match exactly 
            date_range: Dict of date fields with (from, to) tuples
            numeric_range: Dict of numeric fields with (min, max) tuples
            group_by: Field to group results by
            include_total: Whether to include total count (slight performance hit)
        
        Returns:
            Dict with items, total count (if requested), page info
        """
        # Calculate offset
        offset = (page - 1) * page_size
        
        # Start building query
        query = select(self.model)
        
        # Apply filters
        if search_fields:
            search_conditions = []
            for field, value in search_fields.items():
                if value and hasattr(self.model, field):
                    search_conditions.append(getattr(self.model, field).ilike(f"%{value}%"))
            if search_conditions:
                query = query.where(or_(*search_conditions))
        
        if exact_fields:
            exact_conditions = []
            for field, value in exact_fields.items():
                if value is not None and hasattr(self.model, field):
                    exact_conditions.append(getattr(self.model, field) == value)
            if exact_conditions:
                query = query.where(and_(*exact_conditions))
                
        if date_range:
            date_conditions = []
            for field, (start_date, end_date) in date_range.items():
                if hasattr(self.model, field):
                    field_attr = getattr(self.model, field)
                    if start_date:
                        date_conditions.append(field_attr >= start_date)
                    if end_date:
                        date_conditions.append(field_attr <= end_date)
            if date_conditions:
                query = query.where(and_(*date_conditions))
                
        if numeric_range:
            numeric_conditions = []
            for field, (min_val, max_val) in numeric_range.items():
                if hasattr(self.model, field):
                    field_attr = getattr(self.model, field)
                    if min_val is not None:
                        numeric_conditions.append(field_attr >= min_val)
                    if max_val is not None:
                        numeric_conditions.append(field_attr <= max_val)
            if numeric_conditions:
                query = query.where(and_(*numeric_conditions))
            
        # Apply grouping if specified
        if group_by and hasattr(self.model, group_by):
            query = query.group_by(getattr(self.model, group_by))
            
        # Get total count if requested
        total = None
        if include_total:
            count_query = select(func.count()).select_from(self.model)
            
            # Apply the same filters to count query
            if search_fields:
                search_conditions = []
                for field, value in search_fields.items():
                    if value and hasattr(self.model, field):
                        search_conditions.append(getattr(self.model, field).ilike(f"%{value}%"))
                if search_conditions:
                    count_query = count_query.where(or_(*search_conditions))
            
            if exact_fields:
                exact_conditions = []
                for field, value in exact_fields.items():
                    if value is not None and hasattr(self.model, field):
                        exact_conditions.append(getattr(self.model, field) == value)
                if exact_conditions:
                    count_query = count_query.where(and_(*exact_conditions))
                    
            if date_range:
                date_conditions = []
                for field, (start_date, end_date) in date_range.items():
                    if hasattr(self.model, field):
                        field_attr = getattr(self.model, field)
                        if start_date:
                            date_conditions.append(field_attr >= start_date)
                        if end_date:
                            date_conditions.append(field_attr <= end_date)
                if date_conditions:
                    count_query = count_query.where(and_(*date_conditions))
                    
            if numeric_range:
                numeric_conditions = []
                for field, (min_val, max_val) in numeric_range.items():
                    if hasattr(self.model, field):
                        field_attr = getattr(self.model, field)
                        if min_val is not None:
                            numeric_conditions.append(field_attr >= min_val)
                        if max_val is not None:
                            numeric_conditions.append(field_attr <= max_val)
                if numeric_conditions:
                    count_query = count_query.where(and_(*numeric_conditions))
                
            result = await db.execute(count_query)
            total = result.scalar()
        
        # Apply sorting
        if order_by and hasattr(self.model, order_by):
            if order_direction.lower() == "desc":
                query = query.order_by(desc(getattr(self.model, order_by)))
            else:
                query = query.order_by(asc(getattr(self.model, order_by)))
        else:
            # Default sort by id if exists
            if hasattr(self.model, "id"):
                query = query.order_by(asc(self.model.id))
        
        # Apply pagination
        query = query.offset(offset).limit(page_size)
        
        # Execute query
        result = await db.execute(query)
        items = result.scalars().all()
        
        # Calculate pagination info
        total_pages = (total // page_size) + (1 if total % page_size > 0 else 0) if total is not None else None
        has_next = page < total_pages if total_pages is not None else None
        has_prev = page > 1
        
        # Return response
        response = {
            "items": items,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "has_next": has_next,
                "has_prev": has_prev,
            }
        }
        
        if include_total:
            response["pagination"]["total"] = total
            response["pagination"]["total_pages"] = total_pages
            
        return response

    async def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Create a new record.
        
        Args:
            db: Database session
            obj_in: Schema with the data to create
            
        Returns:
            The created record
        """
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, db: Session, *, db_obj: ModelType, obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        Update a record.
        
        Args:
            db: Database session
            db_obj: The database object to update
            obj_in: Schema with the data to update
            
        Returns:
            The updated record
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
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: Session, *, id: Any) -> ModelType:
        """
        Remove a record.
        
        Args:
            db: Database session
            id: ID of the record to remove
            
        Returns:
            The removed record
        """
        obj = await self.get(db=db, id=id)
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj

    async def exists(self, db: Session, *, id: Any) -> bool:
        """
        Check if a record exists.
        
        Args:
            db: Database session
            id: ID of the record to check
            
        Returns:
            True if the record exists, False otherwise
        """
        query = select(self.model).where(self.model.id == id)
        result = await db.execute(query)
        return result.scalars().first() is not None

    async def count(self, db: Session) -> int:
        """
        Count total records.
        
        Args:
            db: Database session
            
        Returns:
            Total number of records
        """
        query = select(func.count()).select_from(self.model)
        result = await db.execute(query)
        return result.scalar()

    async def filter(
        self, 
        db: Session, 
        *, 
        conditions: Dict[str, Any],
        match_any: bool = False
    ) -> List[ModelType]:
        """
        Filter records by conditions.
        
        Args:
            db: Database session
            conditions: Dictionary of field:value to filter by
            match_any: If True, uses OR logic (match any condition), else AND logic (match all)
            
        Returns:
            List of records that match the conditions
        """
        query = select(self.model)
        
        filter_conditions = []
        for field, value in conditions.items():
            if hasattr(self.model, field):
                if isinstance(value, list):
                    filter_conditions.append(getattr(self.model, field).in_(value))
                else:
                    filter_conditions.append(getattr(self.model, field) == value)
        
        if filter_conditions:
            if match_any:
                query = query.where(or_(*filter_conditions))
            else:
                query = query.where(and_(*filter_conditions))
        
        result = await db.execute(query)
        return result.scalars().all()
        
    async def bulk_create(
        self, db: Session, *, objs_in: List[CreateSchemaType]
    ) -> List[ModelType]:
        """
        Create multiple records at once.
        
        Args:
            db: Database session
            objs_in: List of schemas with data to create
            
        Returns:
            List of created records
        """
        db_objs = []
        
        for obj_in in objs_in:
            obj_in_data = jsonable_encoder(obj_in)
            db_obj = self.model(**obj_in_data)
            db.add(db_obj)
            db_objs.append(db_obj)
            
        await db.commit()
        
        for db_obj in db_objs:
            await db.refresh(db_obj)
            
        return db_objs
    
    async def bulk_update(
        self, db: Session, *, ids: List[Any], obj_in: UpdateSchemaType
    ) -> int:
        """
        Update multiple records at once.
        
        Args:
            db: Database session
            ids: List of record IDs to update
            obj_in: Schema with the data to update
            
        Returns:
            Number of records updated
        """
        update_data = obj_in.dict(exclude_unset=True) if not isinstance(obj_in, dict) else obj_in
        
        stmt = (
            update(self.model)
            .where(self.model.id.in_(ids))
            .values(**update_data)
        )
        
        result = await db.execute(stmt)
        await db.commit()
        
        return result.rowcount
        
    async def bulk_delete(self, db: Session, *, ids: List[Any]) -> int:
        """
        Delete multiple records at once.
        
        Args:
            db: Database session
            ids: List of record IDs to delete
            
        Returns:
            Number of records deleted
        """
        stmt = delete(self.model).where(self.model.id.in_(ids))
        result = await db.execute(stmt)
        await db.commit()
        
        return result.rowcount
    
    async def upsert(
        self, db: Session, *, obj_in: Union[CreateSchemaType, UpdateSchemaType], key_field: str = "id"
    ) -> ModelType:
        """
        Update if exists, otherwise create.
        
        Args:
            db: Database session 
            obj_in: Schema with the data
            key_field: Field to check for existence
            
        Returns:
            Created or updated record
        """
        if not hasattr(obj_in, key_field):
            return await self.create(db, obj_in=obj_in)
        
        key_value = getattr(obj_in, key_field)
        if not key_value:
            return await self.create(db, obj_in=obj_in)
            
        # Check if record exists
        query = select(self.model).where(getattr(self.model, key_field) == key_value)
        result = await db.execute(query)
        db_obj = result.scalars().first()
        
        if db_obj:
            # Update existing record
            return await self.update(db, db_obj=db_obj, obj_in=obj_in)
        else:
            # Create new record
            return await self.create(db, obj_in=obj_in)
    async def filter_by_arrays(
    self, 
    db: Session, 
    *, 
    array_filters: Dict[str, List[Any]] = None,
    exact_filters: Dict[str, Any] = None,
    match_any: bool = False,
    skip: int = 0,
    limit: int = 100,
    order_by: Optional[str] = None,
    order_direction: str = "asc"
) -> List[ModelType]:

        """
        Filter records by array fields. "
        Args:
        db: Database session
        array_filters: Dictionary of field:list_of_values to filter by (IN operator)
        exact_filters: Dictionary of field:value for exact matching
        match_any: If True, uses OR logic (match any condition), else AND logic (match all)
        skip: Number of records to skip
        limit: Maximum number of records to return
        order_by: Field to order by
        order_direction: Direction to order (asc/desc)
        
    Returns:
        List of records that match the conditions
    """
        if array_filters:
            array_conditions = []
            for field, values in array_filters.items():
                if hasattr(self.model, field) and values and len(values) > 0:
                    array_conditions.append(getattr(self.model, field).in_(values))
            
            if array_conditions:
                if match_any:
                    query = query.where(or_(*array_conditions))
                else:
                    query = query.where(and_(*array_conditions))
        if exact_filters:
            exact_conditions = []
            for field, value in exact_filters.items():
                if hasattr(self.model, field) and value is not None:
                    exact_conditions.append(getattr(self.model, field) == value)
            
            if exact_conditions:
                if match_any and not array_filters:
                    query = query.where(or_(*exact_conditions))
                else:
                    query = query.where(and_(*exact_conditions))
        
        # Apply sorting
        if order_by and hasattr(self.model, order_by):
            if order_direction.lower() == "desc":
                query = query.order_by(desc(getattr(self.model, order_by)))
            else:
                query = query.order_by(asc(getattr(self.model, order_by)))
        else:
            if hasattr(self.model, "id"):
                query = query.order_by(asc(self.model.id))
        
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    async def filter_by_arrays_paginated(
    self, 
    db: Session, 
    *, 
    array_filters: Dict[str, List[Any]] = None,
    exact_filters: Dict[str, Any] = None,
    match_any: bool = False,
    page: int = 1,
    page_size: int = 10,
    order_by: Optional[str] = None,
    order_direction: str = "asc",
    include_total: bool = True
) -> Dict[str, Any]:
        """
        Filter records by array conditions with pagination.
        
        Args:
            db: Database session
            array_filters: Dictionary of field:list_of_values to filter by (IN operator)
            exact_filters: Dictionary of field:value for exact matching
            match_any: If True, uses OR logic (match any condition), else AND logic (match all)
            page: Page number (1-based)
            page_size: Items per page
            order_by: Field to order by
            order_direction: Direction to order (asc/desc)
            include_total: Whether to include total count
            
        Returns:
            Dict with items, total count (if requested), and page info
        """
        # Calculate offset
        offset = (page - 1) * page_size
        
        # Start building query
        query = select(self.model)
        
        # Build conditions list
        all_conditions = []
        
        # Process array filters (IN conditions)
        if array_filters:
            for field, values in array_filters.items():
                if hasattr(self.model, field) and values and len(values) > 0:
                    all_conditions.append(getattr(self.model, field).in_(values))
        
        # Process exact match filters
        if exact_filters:
            for field, value in exact_filters.items():
                if hasattr(self.model, field) and value is not None:
                    all_conditions.append(getattr(self.model, field) == value)
        
        # Apply conditions to query
        if all_conditions:
            if match_any:
                query = query.where(or_(*all_conditions))
            else:
                query = query.where(and_(*all_conditions))
        
        # Get total count if requested
        total = None
        if include_total:
            count_query = select(func.count()).select_from(self.model)
            
            if all_conditions:
                if match_any:
                    count_query = count_query.where(or_(*all_conditions))
                else:
                    count_query = count_query.where(and_(*all_conditions))
                    
            result = await db.execute(count_query)
            total = result.scalar()
        # Apply sorting
        if order_by and hasattr(self.model, order_by):
            if order_direction.lower() == "desc":
                query = query.order_by(desc(getattr(self.model, order_by)))
            else:
                query = query.order_by(asc(getattr(self.model, order_by)))
        else:
            # Default sort by id if exists
            if hasattr(self.model, "id"):
                query = query.order_by(asc(self.model.id))
        # Apply pagination
        query = query.offset(offset).limit(page_size)
        # Execute query
        result = await db.execute(query)
        items = result.scalars().all()
        # Calculate pagination info
        total_pages = (total // page_size) + (1 if total % page_size > 0 else 0) if total is not None else None
        has_next = page < total_pages if total_pages is not None else None
        has_prev = page > 1
        
        # Return response
        response = {
            "items": items,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "has_next": has_next,
                "has_prev": has_prev,
            }
        }
        
        if include_total:
            response["pagination"]["total"] = total
            response["pagination"]["total_pages"] = total_pages
            
        return response