"""Contact model for individual person records."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Contact(Base):
    """An individual person who is associated with an account."""

    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(128), nullable=False)
    last_name: Mapped[str] = mapped_column(String(128), nullable=False)
    email: Mapped[str] = mapped_column(String(256), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    job_title: Mapped[str | None] = mapped_column(String(128), nullable=True)
    account_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False
    )

    # Relationship to Account
    account = relationship("Account", backref="contacts", lazy="selectin")

    __table_args__ = (
        # Functional index for case-insensitive email lookup
        Index("ix_contacts_email_lower", func.lower(email)),
        # Unique constraint on lowercase email for case-insensitive uniqueness
        Index("ix_contacts_email_unique", func.lower(email), unique=True),
        # Index on account_id for efficient filtering
        Index("ix_contacts_account_id", account_id),
    )

    def __repr__(self) -> str:
        return f"<Contact {self.first_name} {self.last_name}>"
