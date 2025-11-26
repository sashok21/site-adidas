from typing import Optional
from pydantic import BaseModel, Field
from decimal import Decimal

# --- Базова схема для Product (як вкладений об'єкт) ---
# Використовується в BrandResponseSchema для відображення списку товарів
class ProductBrandNestedSchema(BaseModel):
    id: int = Field(gt=0)
    name: str
    price: float # Модель Product використовує float

    class Config:
        from_attributes = True

# --- Схеми Brand ---

class BrandCreateSchema(BaseModel):
    """Схема для створення нового Бренду."""
    name: str = Field(max_length=50)
    description: Optional[str] = None # Опис може бути порожнім

    class Config:
        from_attributes = True

class BrandResponseSchema(BrandCreateSchema):
    """Схема для повернення Бренду з БД."""
    id: int = Field(gt=0)
    products: list[ProductBrandNestedSchema] = [] # Вкладений список товарів

    class Config:
        from_attributes = True

class BrandPartialUpdateSchema(BaseModel):
    """Схема для часткового оновлення Бренду (PATCH)."""
    name: Optional[str] = Field(default=None, max_length=50)
    description: Optional[str] = Field(default=None)

    class Config:
        from_attributes = True