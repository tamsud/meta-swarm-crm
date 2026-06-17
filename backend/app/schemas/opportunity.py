"""Opportunity schemas for request/response validation."""

from datetime import date, datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.opportunity import OpportunityStage


class OpportunityCreate(BaseModel):
    """Schema for creating a new opportunity."""

    title: str = Field(..., min_length=1, max_length=256)
    account_id: int = Field(..., gt=0, description="Required FK to account")
    contact_id: int | None = Field(default=None, gt=0, description="Optional FK to contact")
    stage: OpportunityStage | None = Field(
        default=None,
        description="Pipeline stage (defaults to prospecting if not provided)",
    )
    value: Annotated[Decimal | None, Field(default=None, description="Deal value in USD")] = None
    probability: int | None = Field(
        default=None,
        description="Win probability 0-100",
    )
    expected_close_date: date | None = Field(
        default=None,
        description="Expected close date",
    )

    @field_validator("value")
    @classmethod
    def validate_value_positive(cls, v: Decimal | None) -> Decimal | None:
        """Ensure value is strictly greater than zero when provided."""
        if v is not None and v <= 0:
            raise ValueError("Value must be greater than 0")
        return v

    @field_validator("probability")
    @classmethod
    def validate_probability_range(cls, v: int | None) -> int | None:
        """Ensure probability is between 0 and 100 when provided."""
        if v is not None and (v < 0 or v > 100):
            raise ValueError("Probability must be between 0 and 100")
        return v


class OpportunityUpdate(BaseModel):
    """Schema for updating an existing opportunity."""

    title: str | None = Field(default=None, min_length=1, max_length=256)
    account_id: int | None = Field(default=None, gt=0)
    contact_id: int | None = Field(default=None, gt=0)
    stage: OpportunityStage | None = Field(default=None)
    value: Annotated[Decimal | None, Field(default=None)] = None
    probability: int | None = Field(default=None)
    expected_close_date: date | None = Field(default=None)

    @field_validator("value")
    @classmethod
    def validate_value_positive(cls, v: Decimal | None) -> Decimal | None:
        """Ensure value is strictly greater than zero when provided."""
        if v is not None and v <= 0:
            raise ValueError("Value must be greater than 0")
        return v

    @field_validator("probability")
    @classmethod
    def validate_probability_range(cls, v: int | None) -> int | None:
        """Ensure probability is between 0 and 100 when provided."""
        if v is not None and (v < 0 or v > 100):
            raise ValueError("Probability must be between 0 and 100")
        return v


class OpportunityResponse(BaseModel):
    """Schema for opportunity responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    account_id: int
    contact_id: int | None
    stage: OpportunityStage
    value: Decimal | None
    probability: int | None
    expected_close_date: date | None
    created_at: datetime
    updated_at: datetime
