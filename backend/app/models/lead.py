"""Lead model for prospect tracking and conversion."""

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class LeadStatus(str, enum.Enum):
    new = "new"
    contacted = "contacted"
    qualified = "qualified"
    lost = "lost"


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(128), nullable=False)
    last_name: Mapped[str] = mapped_column(String(128), nullable=False)
    email: Mapped[str] = mapped_column(String(256), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    company: Mapped[str | None] = mapped_column(String(256), nullable=True)
    status: Mapped[LeadStatus] = mapped_column(
        Enum(LeadStatus, name="lead_status"),
        nullable=False,
        server_default="new",
    )
    source: Mapped[str | None] = mapped_column(String(128), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by_user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    converted_opportunity_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("opportunities.id", ondelete="SET NULL"), nullable=True
    )
    converted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False
    )

    converted_opportunity: Mapped["Opportunity | None"] = relationship(  # noqa: F821
        "Opportunity", foreign_keys=[converted_opportunity_id], lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Lead {self.first_name} {self.last_name}>"
