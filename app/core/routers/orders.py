from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError

from app.core.models.order import Order
from app.dependencies import SessionDepend
from app.schemas.orders import (
    OrderCreateSchema,
    OrderResponseSchema,
    OrderPartialUpdateSchema
)

router = APIRouter(prefix="/orders", tags=["Orders"])

# --- GET (Список) ---
@router.get(
    path="/",
    response_model=List[OrderResponseSchema],
    status_code=status.HTTP_200_OK,
)
async def get_orders(session: SessionDepend):
    """Отримати список всіх замовлень, включаючи користувача та позиції."""
    query = select(Order).options(selectinload(Order.user), selectinload(Order.items))
    result = await session.execute(query)
    return result.scalars().all()

# --- GET (Один об'єкт) ---
@router.get(
    path="/{order_id}",
    response_model=OrderResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_order(order_id: int, session: SessionDepend):
    """Отримати одне замовлення за ID."""
    query = select(Order).filter(Order.id == order_id).options(selectinload(Order.user), selectinload(Order.items))
    result = await session.execute(query)
    existing_order = result.scalars().first()

    if not existing_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id={order_id} not found."
        )
    return existing_order

# --- CREATE (POST) ---
@router.post(
    path="/",
    response_model=OrderResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_order(order: OrderCreateSchema, session: SessionDepend):
    """Створити нове замовлення."""
    # ПРИМІТКА: total_amount та order_date будуть заповнені ORM
    new_order = Order(**order.model_dump())
    session.add(new_order)
    try:
        await session.commit()
        await session.refresh(new_order)
        return new_order
    except SQLAlchemyError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating order: {e}"
        )

# --- UPDATE (PATCH) ---
@router.patch(
    path="/{order_id}",
    response_model=OrderResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def partial_update_order(
    order_id: int,
    order: OrderPartialUpdateSchema,
    session: SessionDepend
):
    """Частково оновити дані замовлення."""
    existing_order = await session.get(Order, order_id)
    if not existing_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id={order_id} not found."
        )

    update_data = order.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(existing_order, field, value)

    await session.commit()
    await session.refresh(existing_order)
    return existing_order

# --- DELETE ---
@router.delete(
    path="/{order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_order(order_id: int, session: SessionDepend):
    """Видалити замовлення за ID."""
    existing_order = await session.get(Order, order_id)
    if not existing_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id={order_id} not found."
        )

    await session.delete(existing_order)
    await session.commit()
    return None