from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError

from app.core.models.order_item import OrderItem
from app.dependencies import SessionDepend
from app.schemas.order_items import (
    OrderItemCreateSchema,
    OrderItemResponseSchema,
    OrderItemPartialUpdateSchema
)

router = APIRouter(prefix="/order_items", tags=["Order Items"])

# --- GET (Список) ---
@router.get(
    path="/",
    response_model=List[OrderItemResponseSchema],
    status_code=status.HTTP_200_OK,
)
async def get_order_items(session: SessionDepend):
    """Отримати список всіх позицій замовлень, включаючи Order та Product."""
    query = select(OrderItem).options(selectinload(OrderItem.order), selectinload(OrderItem.product))
    result = await session.execute(query)
    return result.scalars().all()

# --- GET (Один об'єкт) ---
@router.get(
    path="/{item_id}",
    response_model=OrderItemResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_order_item(item_id: int, session: SessionDepend):
    """Отримати одну позицію замовлення за ID."""
    query = select(OrderItem).filter(OrderItem.id == item_id).options(selectinload(OrderItem.order), selectinload(OrderItem.product))
    result = await session.execute(query)
    existing_item = result.scalars().first()

    if not existing_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order item with id={item_id} not found."
        )
    return existing_item

# --- CREATE (POST) ---
@router.post(
    path="/",
    response_model=OrderItemResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_order_item(item: OrderItemCreateSchema, session: SessionDepend):
    """Створити нову позицію замовлення."""
    # ПРИМІТКА: unit_price має бути встановлений на основі поточного Product.price
    # Для спрощення ми припускаємо, що unit_price буде встановлено пізніше або в моделі
    new_item = OrderItem(**item.model_dump())
    session.add(new_item)
    try:
        await session.commit()
        await session.refresh(new_item)
        return new_item
    except SQLAlchemyError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating order item: {e}"
        )

# --- UPDATE (PATCH) ---
@router.patch(
    path="/{item_id}",
    response_model=OrderItemResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def partial_update_order_item(
    item_id: int,
    item: OrderItemPartialUpdateSchema,
    session: SessionDepend
):
    """Частково оновити дані позиції замовлення (тільки quantity)."""
    existing_item = await session.get(OrderItem, item_id)
    if not existing_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order item with id={item_id} not found."
        )

    update_data = item.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(existing_item, field, value)

    await session.commit()
    await session.refresh(existing_item)
    return existing_item

# --- DELETE ---
@router.delete(
    path="/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_order_item(item_id: int, session: SessionDepend):
    """Видалити позицію замовлення за ID."""
    existing_item = await session.get(OrderItem, item_id)
    if not existing_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order item with id={item_id} not found."
        )

    await session.delete(existing_item)
    await session.commit()
    return None