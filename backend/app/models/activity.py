"""Activity model for CRM engagement tracking."""

import enum
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ActivityType(str, enum.Enum):
    call = "call"
    email = "email"
    meeting = "meeting"


class Activity(Base):
    __tablename__ = "activities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type: Mapped[ActivityType] = mapped_column(Enum(ActivityType, name="activity_type"), nullable=False)
    subject: Mapped[str] = mapped_column(String(512), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    activity_date: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    contact_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("contacts.id", ondelete="RESTRICT"),
        nullable=True,
    )
    opportunity_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("opportunities.id", ondelete="RESTRICT"),
        nullable=True,
    )
    created_by_user_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
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

    contact: Mapped["Contact | None"] = relationship("Contact", lazy="selectin")  # noqa: F821
    opportunity: Mapped["Opportunity | None"] = relationship("Opportunity", lazy="selectin")  # noqa: F821

    __table_args__ = (
        CheckConstraint(
            "contact_id IS NOT NULL OR opportunity_id IS NOT NULL",
            name="ck_activities_link_required",
        ),
    )

    def __repr__(self) -> str:
        return f"<Activity {self.type} {self.subject!r}>"
