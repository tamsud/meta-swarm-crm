"""Account schemas for request/response validation."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AccountCreate(BaseModel):
    """Schema for creating a new account."""

    name: str = Field(..., min_length=1, max_length=256)
    industry: str | None = Field(default=None, max_length=128)
    website: str | None = Field(default=None, max_length=512)
    phone: str | None = Field(default=None, max_length=32)
    address: str | None = Field(default=None, max_length=512)


class AccountUpdate(BaseModel):
    """Schema for updating an existing account."""

    name: str | None = Field(default=None, min_length=1, max_length=256)
    industry: str | None = Field(default=None, max_length=128)
    website: str | None = Field(default=None, max_length=512)
    phone: str | None = Field(default=None, max_length=32)
    address: str | None = Field(default=None, max_length=512)


class AccountResponse(BaseModel):
    """Schema for account responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    industry: str | None
    website: str | None
    phone: str | None
    address: str | None
    created_at: datetime
    updated_at: datetime
