from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError

from app.core.models.category import Category
from app.dependencies import SessionDepend
from app.schemas.categories import (
    CategoryCreateSchema,
    CategoryResponseSchema,
    CategoryPartialUpdateSchema
)

router = APIRouter(prefix="/categories", tags=["Categories"])

# --- GET (Список) ---
@router.get(
    path="/",
    response_model=List[CategoryResponseSchema],
    status_code=status.HTTP_200_OK,
)
async def get_categories(session: SessionDepend):
    """Отримати список всіх категорій, включаючи їхні товари."""
    query = select(Category).options(selectinload(Category.products))
    result = await session.execute(query)
    return result.scalars().all()

# --- GET (Один об'єкт) ---
@router.get(
    path="/{category_id}",
    response_model=CategoryResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_category(category_id: int, session: SessionDepend):
    """Отримати одну категорію за ID."""
    query = select(Category).filter(Category.id == category_id).options(selectinload(Category.products))
    result = await session.execute(query)
    existing_category = result.scalars().first()

    if not existing_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id={category_id} not found."
        )
    return existing_category

# --- CREATE (POST) ---
@router.post(
    path="/",
    response_model=CategoryResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_category(category: CategoryCreateSchema, session: SessionDepend):
    """Створити нову категорію."""
    new_category = Category(**category.model_dump())
    session.add(new_category)
    try:
        await session.commit()
        await session.refresh(new_category)
        return new_category
    except SQLAlchemyError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating category: {e}"
        )

# --- UPDATE (PATCH) ---
@router.patch(
    path="/{category_id}",
    response_model=CategoryResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def partial_update_category(
    category_id: int,
    category: CategoryPartialUpdateSchema,
    session: SessionDepend
):
    """Частково оновити дані категорії."""
    existing_category = await session.get(Category, category_id)
    if not existing_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id={category_id} not found."
        )

    update_data = category.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(existing_category, field, value)

    await session.commit()
    await session.refresh(existing_category)
    return existing_category

# --- DELETE ---
@router.delete(
    path="/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_category(category_id: int, session: SessionDepend):
    """Видалити категорію за ID."""
    existing_category = await session.get(Category, category_id)
    if not existing_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id={category_id} not found."
        )

    await session.delete(existing_category)
    await session.commit()
    return None