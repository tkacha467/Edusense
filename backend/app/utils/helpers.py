"""Helper functions."""
import uuid
from datetime import datetime, timezone
from typing import Tuple


def generate_uuid() -> str:
    """Generate a random UUID v4 string."""
    return str(uuid.uuid4())


def utc_now() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)


def paginate_query(query: Any, page: int, page_size: int) -> Tuple[Any, int, int]:
    """
    Calculate pagination offset and limit.
    Returns (query_with_limit_and_offset, offset, limit).
    """
    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 10
        
    offset = (page - 1) * page_size
    limit = page_size
    
    paginated_query = query.offset(offset).limit(limit)
    return paginated_query, offset, limit


def calculate_percentage(scored: float, total: float) -> float:
    """Calculate percentage score."""
    if total <= 0:
        return 0.0
    return (scored / total) * 100.0


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp a value between a minimum and maximum."""
    return max(min_val, min(value, max_val))
