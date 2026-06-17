"""Lead schemas for request/response validation."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.lead import LeadStatus


class LeadCreate(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=128)
    last_name: str = Field(..., min_length=1, max_length=128)
    email: str = Field(..., min_length=1, max_length=256)
    phone: str | None = Field(default=None, max_length=64)
    company: str | None = Field(default=None, max_length=256)
    status: LeadStatus = LeadStatus.new
    source: str | None = Field(default=None, max_length=128)
    notes: str | None = None


class LeadUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    first_name: str | None = Field(default=None, min_length=1, max_length=128)
    last_name: str | None = Field(default=None, min_length=1, max_length=128)
    email: str | None = Field(default=None, min_length=1, max_length=256)
    phone: str | None = None
    company: str | None = None
    status: LeadStatus | None = None
    source: str | None = None
    notes: str | None = None


class LeadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    email: str
    phone: str | None
    company: str | None
    status: LeadStatus
    source: str | None
    notes: str | None
    created_by_user_id: int | None
    converted_opportunity_id: int | None
    converted_at: datetime | None
    created_at: datetime
    updated_at: datetime
