"""MockEmail model for simulated outbound email records."""

from datetime import datetime
import uuid

from sqlalchemy import CheckConstraint, DateTime, Index, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def generate_uuid() -> str:
    """Generate a new UUID string."""
    return str(uuid.uuid4())


class MockEmail(Base):
    """A simulated outbound email record for demo/testing purposes."""

    __tablename__ = "mock_emails"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid
    )
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    from_email: Mapped[str] = mapped_column(String(255), nullable=False)
    to_email: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="unread"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False
    )

    __table_args__ = (
        CheckConstraint("status IN ('unread', 'read')", name="ck_mock_emails_status"),
        Index("ix_mock_emails_subject", "subject"),
        Index("ix_mock_emails_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<MockEmail {self.subject} to={self.to_email}>"
