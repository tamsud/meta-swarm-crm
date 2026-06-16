"""Standardized API response envelope schemas."""

from typing import Generic, Literal, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginatedMeta(BaseModel):
    """Pagination metadata for list responses."""

    count: int = Field(..., description="Number of items in current page")
    total: int = Field(..., description="Total number of items across all pages")
    offset: int = Field(..., description="Number of items skipped")
    limit: int = Field(..., description="Maximum items per page")


class ApiResponse(BaseModel, Generic[T]):
    """Standard success response envelope."""

    success: Literal[True] = Field(default=True, description="Always true for success responses")
    data: T = Field(..., description="Response payload")


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard success response envelope for paginated lists."""

    success: Literal[True] = Field(default=True, description="Always true for success responses")
    data: list[T] = Field(..., description="List of items")
    meta: PaginatedMeta = Field(..., description="Pagination metadata")


class ApiError(BaseModel):
    """Error details structure."""

    code: str = Field(..., description="Machine-readable error code in SCREAMING_SNAKE_CASE")
    message: str = Field(..., description="Human-readable error message")

    class Config:
        extra = "allow"


class ErrorResponse(BaseModel):
    """Standard error response envelope."""

    success: Literal[False] = Field(default=False, description="Always false for error responses")
    error: ApiError = Field(..., description="Error details")
