from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, Null, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.connection import Base


class Invitation(Base):
    __tablename__ = "invitations"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, nullable=False
    )

    company_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("companies.id"), nullable=False
    )

    email: Mapped[str] = mapped_column(String(255), nullable=False)

    token_hash: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    expires_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    accepted_at: Mapped[datetime | Null] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    created_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
