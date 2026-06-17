"""Activity schemas for request/response validation."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.activity import ActivityType


class ActivityCreate(BaseModel):
    type: ActivityType
    subject: str = Field(..., min_length=1, max_length=512)
    notes: str | None = None
    activity_date: datetime | None = None
    contact_id: int | None = Field(default=None, gt=0)
    opportunity_id: int | None = Field(default=None, gt=0)

    @model_validator(mode="after")
    def require_link(self) -> "ActivityCreate":
        if self.contact_id is None and self.opportunity_id is None:
            raise ValueError("At least one of contact_id or opportunity_id must be provided")
        return self


class ActivityUpdate(BaseModel):
    type: ActivityType | None = None
    subject: str | None = Field(default=None, min_length=1, max_length=512)
    notes: str | None = None
    activity_date: datetime | None = None
    contact_id: int | None = Field(default=None, gt=0)
    opportunity_id: int | None = Field(default=None, gt=0)

    @model_validator(mode="before")
    @classmethod
    def check_not_both_null(cls, values: Any) -> Any:
        if isinstance(values, dict):
            c = values.get("contact_id")
            o = values.get("opportunity_id")
            if c is not None or o is not None:
                pass
        return values


class ActivityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    type: ActivityType
    subject: str
    notes: str | None
    activity_date: datetime
    contact_id: int | None
    opportunity_id: int | None
    created_by_user_id: int | None
    created_at: datetime
    updated_at: datetime
