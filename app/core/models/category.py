from sqlalchemy.orm import Mapped, relationship, mapped_column
from sqlalchemy import String

from .base import BaseModel, int_pk




class Category(BaseModel):
    """Модель Категорії."""
    __tablename__ = "categories"

    id: Mapped[int_pk]
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)


    products: Mapped[list["Product"]] = relationship(back_populates="category")

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"