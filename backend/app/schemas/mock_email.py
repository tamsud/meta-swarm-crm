"""MockEmail schemas for request/response validation."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class MockEmailCreate(BaseModel):
    """Schema for composing a new mock email."""

    to_email: EmailStr = Field(..., description="Recipient email address")
    subject: str = Field(..., min_length=1, max_length=255, description="Email subject line")
    body: str | None = Field(default=None, description="Email body text")


class MockEmailListItem(BaseModel):
    """Schema for mock email list item (with truncated preview)."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    subject: str
    from_email: str
    to_email: str
    preview: str = Field(..., description="Truncated body preview (max 80 chars)")
    status: str
    created_at: datetime


class MockEmailDetail(BaseModel):
    """Schema for full mock email detail."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    subject: str
    from_email: str
    to_email: str
    body: str | None
    status: str
    created_at: datetime


class MockEmailListResponse(BaseModel):
    """Schema for paginated mock email list response."""

    items: list[MockEmailListItem]
    meta: dict
