from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError

from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.user import User
from app.core.schemas.users import UserResponseSchema, UserCreateSchema, UserPartialUpdateSchema
from app.core.settings.db import db

SessionDepend = Annotated[AsyncSession, Depends(db.get_session)]

router = APIRouter(prefix="/users", tags=["Users"])


# --- GET (Список) ---
@router.get(
    path="/",
    response_model=List[UserResponseSchema],
    status_code=status.HTTP_200_OK,
)
async def get_users(session: SessionDepend):
    """Отримати список всіх користувачів."""
    # Завантажуємо зв'язок 'orders'
    query = select(User).options(selectinload(User.orders))
    result = await session.execute(query)
    return result.scalars().all()


# --- GET (Один об'єкт) ---
@router.get(
    path="/{user_id}",
    response_model=UserResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_user(user_id: int, session: SessionDepend):
    """Отримати одного користувача за ID."""
    query = select(User).filter(User.id == user_id).options(selectinload(User.orders))
    result = await session.execute(query)
    existing_user = result.scalars().first()

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id={user_id} not found."
        )
    return existing_user


# --- CREATE (POST) ---
@router.post(
    path="/",
    response_model=UserResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
        user: UserCreateSchema,
        session: SessionDepend
):
    """Створити нового користувача."""
    user_data = user.model_dump()

    # Тут можна додати хешування пароля перед створенням об'єкта User
    new_user = User(**user_data)

    session.add(new_user)

    try:
        await session.commit()
        await session.refresh(new_user)
        return new_user
    except SQLAlchemyError as e:
        await session.rollback()
        # Обробка помилки унікальності (наприклад, email вже існує)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating user: {e}"
        )


# --- UPDATE (PATCH) - Часткове оновлення ---
@router.patch(
    path="/{user_id}",
    response_model=UserResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def partial_update_user(
        user_id: int,
        user: UserPartialUpdateSchema,
        session: SessionDepend
):
    """Частково оновити дані користувача."""
    existing_user = await session.get(User, user_id)

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id={user_id} not found."
        )

    # Оновлюємо лише ті поля, які були передані в запиті
    update_data = user.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(existing_user, field, value)

    try:
        await session.commit()
        await session.refresh(existing_user)
        return existing_user
    except SQLAlchemyError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating user: {e}"
        )


# --- DELETE ---
@router.delete(
    path="/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(user_id: int, session: SessionDepend):
    """Видалити користувача за ID."""
    existing_user = await session.get(User, user_id)

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id={user_id} not found."
        )

    await session.delete(existing_user)
    await session.commit()

    return None