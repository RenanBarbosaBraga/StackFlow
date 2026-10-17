from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.connection import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    token_hash: Mapped[str] = mapped_column(String(64), unique=False, nullable=True)

    expired_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
