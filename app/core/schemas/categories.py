from typing import Optional
from pydantic import BaseModel, Field


# --- Базова схема для Product (як вкладений об'єкт) ---
# Використовується в CategoryResponseSchema для відображення списку товарів
class ProductCategoryNestedSchema(BaseModel):
    id: int = Field(gt=0)
    name: str
    price: float  # Модель Product використовує float

    class Config:
        from_attributes = True


# --- Схеми Category ---

class CategoryCreateSchema(BaseModel):
    """Схема для створення нової Категорії."""
    name: str = Field(max_length=50)

    class Config:
        from_attributes = True


class CategoryResponseSchema(CategoryCreateSchema):
    """Схема для повернення Категорії з БД."""
    id: int = Field(gt=0)
    products: list[ProductCategoryNestedSchema] = []  # Вкладений список товарів

    class Config:
        from_attributes = True


class CategoryPartialUpdateSchema(BaseModel):
    """Схема для часткового оновлення Категорії (PATCH)."""
    name: Optional[str] = Field(default=None, max_length=50)

    class Config:
        from_attributes = True