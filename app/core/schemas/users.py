from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime


# --- Вкладена схема для Order (щоб уникнути циклу з orders.py) ---
class OrderUserNestedSchema(BaseModel):
    id: int
    order_date: datetime
    status: str
    total_amount: float  # Модель Order використовує float/Numeric

    class Config:
        from_attributes = True


# --- Схеми User ---

class UserCreateSchema(BaseModel):
    """Схема для реєстрації нового користувача."""
    email: EmailStr = Field(max_length=100)
    password: str = Field(min_length=8, max_length=255)
    first_name: Optional[str] = Field(default=None, max_length=50)
    last_name: Optional[str] = Field(default=None, max_length=50)
    phone_number: Optional[str] = Field(default=None, max_length=20)

    class Config:
        from_attributes = True


class UserResponseSchema(BaseModel):
    """Схема для повернення користувача."""
    id: int
    email: EmailStr
    first_name: Optional[str]
    last_name: Optional[str]
    phone_number: Optional[str]

    password: str = Field(exclude=True)  # Виключаємо пароль з відповіді
    orders: List[OrderUserNestedSchema] = []  # Включаємо список замовлень

    class Config:
        from_attributes = True


class UserPartialUpdateSchema(BaseModel):
    """Схема для часткового оновлення користувача (PATCH)."""
    email: Optional[EmailStr] = Field(default=None, max_length=100)
    password: Optional[str] = Field(default=None, min_length=8, max_length=255)
    first_name: Optional[str] = Field(default=None, max_length=50)
    last_name: Optional[str] = Field(default=None, max_length=50)
    phone_number: Optional[str] = Field(default=None, max_length=20)

    class Config:
        from_attributes = True