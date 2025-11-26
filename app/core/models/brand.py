from sqlalchemy.orm import Mapped, relationship, mapped_column
from sqlalchemy import String

from .base import BaseModel, int_pk


class Brand(BaseModel):
    """Модель Бренду (Виробника) кросівок."""
    __tablename__ = "brands"

    id: Mapped[int_pk]
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    description: Mapped[str | None]

    products: Mapped[list["Product"]] = relationship(back_populates="brand")