"""Account model for company/organization records."""

from datetime import datetime

from sqlalchemy import DateTime, Index, Integer, String, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Account(Base):
    """A company or organization that is a current or potential customer."""

    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    industry: Mapped[str | None] = mapped_column(String(128), nullable=True)
    website: Mapped[str | None] = mapped_column(String(512), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    address: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False
    )

    __table_args__ = (
        # Functional index for case-insensitive name search
        Index("ix_accounts_lower_name", func.lower(name)),
        # Unique constraint on lowercase name for case-insensitive uniqueness
        Index("ix_accounts_name_unique", func.lower(name), unique=True),
    )

    def __repr__(self) -> str:
        return f"<Account {self.name}>"
