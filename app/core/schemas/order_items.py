from typing import Optional
from pydantic import BaseModel, Field
from decimal import Decimal


# --- Вкладені схеми ---
# 1. Спрощена схема Order
class OrderItemOrderNestedSchema(BaseModel):
    id: int
    status: str
    total_amount: float

    class Config:
        from_attributes = True


# 2. Спрощена схема Product
class OrderItemProductNestedSchema(BaseModel):
    id: int
    name: str
    price: float

    class Config:
        from_attributes = True


# --- Схеми OrderItem ---

class OrderItemCreateSchema(BaseModel):
    """Схема для створення нової Позиції Замовлення."""
    order_id: int = Field(gt=0)
    product_id: int = Field(gt=0)
    quantity: int = Field(default=1, gt=0)

    # unit_price не включаємо, оскільки має братися з моделі Product при створенні

    class Config:
        from_attributes = True


class OrderItemResponseSchema(OrderItemCreateSchema):
    """Схема для повернення Позиції Замовлення з БД."""
    id: int = Field(gt=0)
    unit_price: float  # Ціна одиниці на момент замовлення

    # Замінюємо ID на повні об'єкти
    order: OrderItemOrderNestedSchema
    product: OrderItemProductNestedSchema

    order_id: int = Field(exclude=True)
    product_id: int = Field(exclude=True)

    class Config:
        from_attributes = True


class OrderItemPartialUpdateSchema(BaseModel):
    """Схема для часткового оновлення Позиції Замовлення (PATCH)."""
    quantity: Optional[int] = Field(default=None, gt=0)

    # unit_price зазвичай не оновлюється вручну

    class Config:
        from_attributes = True