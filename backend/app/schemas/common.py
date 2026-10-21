from typing import Generic, TypeVar, Optional, Any, List
from pydantic import BaseModel, ConfigDict
from datetime import datetime

T = TypeVar("T")


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[Any] = None


class ErrorResponse(BaseModel):
    error: ErrorDetail


class ResponseMetadata(BaseModel):
    source: str
    source_type: str  # user_api, shared_api, free_api, scraped, cache
    fetched_at: datetime
    age_minutes: float
    stale: bool
    fallback_reason: Optional[str] = None


class DataEnvelope(BaseModel, Generic[T]):
    data: T
    meta: Optional[ResponseMetadata] = None


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    pages: int
