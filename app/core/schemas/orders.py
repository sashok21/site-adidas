from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


# --- Вкладені схеми ---
# 1. Спрощена схема User (щоб уникнути циклу з users.py)
class UserOrderNestedSchema(BaseModel):
    id: int
    email: str
    first_name: Optional[str] = None

    class Config:
        from_attributes = True


# 2. Схема OrderItem (для відображення вмісту замовлення)
class OrderItemOrderNestedSchema(BaseModel):
    id: int
    product_id: int
    quantity: int = Field(gt=0)
    unit_price: float

    class Config:
        from_attributes = True


# --- Схеми Order ---

class OrderCreateSchema(BaseModel):
    """Схема для створення нового Замовлення."""
    user_id: int = Field(gt=0)
    status: str = Field(max_length=20)
    shipping_address: Optional[str] = None

    # total_amount та order_date не включаємо, вони генеруються БД/сервером

    class Config:
        from_attributes = True


class OrderResponseSchema(OrderCreateSchema):
    """Схема для повернення Замовлення з БД."""
    id: int = Field(gt=0)
    order_date: datetime  # Повертається після створення
    total_amount: float  # Повертається після створення/розрахунку

    # Замінюємо user_id на повний об'єкт User
    user: UserOrderNestedSchema
    user_id: int = Field(exclude=True)

    # Включаємо список позицій замовлення
    items: List[OrderItemOrderNestedSchema] = []

    class Config:
        from_attributes = True


class OrderPartialUpdateSchema(BaseModel):
    """Схема для часткового оновлення Замовлення (PATCH)."""
    status: Optional[str] = Field(default=None, max_length=20)
    shipping_address: Optional[str] = Field(default=None)

    # total_amount: Optional[float] = Field(default=None) # Можна оновлювати, якщо потрібно вручну

    class Config:
        from_attributes = True