from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.connection import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(
        Integer,
        index=True,
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    price: Mapped[int] = mapped_column(
        Float,
        nullable=False,
    )
    quantity: Mapped[int] = mapped_column(
        Float,
        nullable=False,
    )
