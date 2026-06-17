"""Contact schemas for request/response validation."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ContactCreate(BaseModel):
    """Schema for creating a new contact."""

    first_name: str = Field(..., min_length=1, max_length=128)
    last_name: str = Field(..., min_length=1, max_length=128)
    email: EmailStr = Field(..., max_length=256)
    phone: str | None = Field(default=None, max_length=32)
    job_title: str | None = Field(default=None, max_length=128)
    account_id: int | None = Field(default=None, gt=0)


class ContactUpdate(BaseModel):
    """Schema for updating an existing contact."""

    first_name: str | None = Field(default=None, min_length=1, max_length=128)
    last_name: str | None = Field(default=None, min_length=1, max_length=128)
    email: EmailStr | None = Field(default=None, max_length=256)
    phone: str | None = Field(default=None, max_length=32)
    job_title: str | None = Field(default=None, max_length=128)
    account_id: int | None = Field(default=None)


class AccountBrief(BaseModel):
    """Brief account info for contact response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class ContactResponse(BaseModel):
    """Schema for contact responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    email: str
    phone: str | None
    job_title: str | None
    account_id: int | None
    account: AccountBrief | None
    created_at: datetime
    updated_at: datetime
