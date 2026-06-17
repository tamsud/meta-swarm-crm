"""Opportunity model for sales pipeline management."""

import enum
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class OpportunityStage(str, enum.Enum):
    """Pipeline stages for opportunities."""

    prospecting = "prospecting"
    proposal = "proposal"
    negotiation = "negotiation"
    closed_won = "closed_won"
    closed_lost = "closed_lost"


class Opportunity(Base):
    """A qualified sales deal actively being pursued."""

    __tablename__ = "opportunities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    account_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("accounts.id", ondelete="RESTRICT"),
        nullable=False,
    )
    contact_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("contacts.id", ondelete="SET NULL"),
        nullable=True,
    )
    stage: Mapped[OpportunityStage] = mapped_column(
        Enum(OpportunityStage, name="opportunity_stage"),
        nullable=False,
        server_default="prospecting",
    )
    value: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=15, scale=2),
        nullable=True,
    )
    probability: Mapped[int | None] = mapped_column(Integer, nullable=True)
    expected_close_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    # Relationships
    account: Mapped["Account"] = relationship(  # noqa: F821
        "Account",
        lazy="selectin",
    )
    contact: Mapped["Contact | None"] = relationship(  # noqa: F821
        "Contact",
        lazy="selectin",
    )

    __table_args__ = (
        CheckConstraint("value > 0", name="ck_opportunities_value_positive"),
        CheckConstraint(
            "probability >= 0 AND probability <= 100",
            name="ck_opportunities_probability_range",
        ),
    )

    def __repr__(self) -> str:
        return f"<Opportunity {self.title}>"
