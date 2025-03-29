"""
Type definitions for SQLAlchemy to help with type checking.
This module provides type stubs and helpers for SQLAlchemy operations.
"""
from typing import TypeVar, Generic, Any, Type, List, Optional, Union, Dict, ClassVar
from sqlalchemy.orm import Session, Query
from sqlalchemy.ext.declarative import DeclarativeMeta

# Type variable for SQLAlchemy models
T = TypeVar('T')

class SQLAlchemySession(Session):
    """Type stub for SQLAlchemy session with explicit method definitions."""
    
    def add(self, instance: Any) -> None:
        """Add a model instance to the session."""
        ...
    
    def commit(self) -> None:
        """Commit the current transaction."""
        ...
    
    def rollback(self) -> None:
        """Rollback the current transaction."""
        ...
    
    def delete(self, instance: Any) -> None:
        """Mark an instance for deletion."""
        ...
    
    def query(self, *entities: Any, **kwargs: Any) -> Query:
        """Return a new Query object."""
        ...
    
    def flush(self, objects: Optional[List[Any]] = None) -> None:
        """Flush all changes to the database."""
        ...

# Type alias for model classes
ModelType = TypeVar('ModelType')
    
class SQLAlchemyModel(Generic[ModelType]):
    """Base type for SQLAlchemy models."""
    
    query: ClassVar[Query[ModelType]]
    id: int
    
    @classmethod
    def get_or_404(cls, id: int) -> ModelType:
        """Get model by ID or return 404 error."""
        ...

# Import these types where needed for type hinting
__all__ = ['SQLAlchemySession', 'SQLAlchemyModel', 'T', 'ModelType'] 