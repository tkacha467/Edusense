from datetime import datetime
from typing import Generic, TypeVar
from pydantic import BaseModel as PydanticBase, ConfigDict

T = TypeVar('T')

class BaseResponse(PydanticBase):
    """Base schema for response models containing standard fields."""
    id: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class PaginatedResponse(PydanticBase, Generic[T]):
    """Generic schema for paginated responses."""
    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int

class MessageResponse(PydanticBase):
    """Standard message response schema."""
    message: str
    success: bool = True
