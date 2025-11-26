from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError

from app.core.models.brand import Brand
from app.dependencies import SessionDepend
from app.schemas.brands import (
    BrandCreateSchema,
    BrandResponseSchema,
    BrandPartialUpdateSchema
)

router = APIRouter(prefix="/brands", tags=["Brands"])

# --- GET (Список) ---
@router.get(
    path="/",
    response_model=List[BrandResponseSchema],
    status_code=status.HTTP_200_OK,
)
async def get_brands(session: SessionDepend):
    """Отримати список всіх брендів, включаючи їхні товари."""
    query = select(Brand).options(selectinload(Brand.products))
    result = await session.execute(query)
    return result.scalars().all()

# --- GET (Один об'єкт) ---
@router.get(
    path="/{brand_id}",
    response_model=BrandResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_brand(brand_id: int, session: SessionDepend):
    """Отримати один бренд за ID."""
    query = select(Brand).filter(Brand.id == brand_id).options(selectinload(Brand.products))
    result = await session.execute(query)
    existing_brand = result.scalars().first()

    if not existing_brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Brand with id={brand_id} not found."
        )
    return existing_brand

# --- CREATE (POST) ---
@router.post(
    path="/",
    response_model=BrandResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_brand(brand: BrandCreateSchema, session: SessionDepend):
    """Створити новий бренд."""
    new_brand = Brand(**brand.model_dump())
    session.add(new_brand)
    try:
        await session.commit()
        await session.refresh(new_brand)
        return new_brand
    except SQLAlchemyError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating brand: {e}"
        )

# --- UPDATE (PATCH) ---
@router.patch(
    path="/{brand_id}",
    response_model=BrandResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def partial_update_brand(
    brand_id: int,
    brand: BrandPartialUpdateSchema,
    session: SessionDepend
):
    """Частково оновити дані бренду."""
    existing_brand = await session.get(Brand, brand_id)
    if not existing_brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Brand with id={brand_id} not found."
        )

    update_data = brand.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(existing_brand, field, value)

    await session.commit()
    await session.refresh(existing_brand)
    return existing_brand

# --- DELETE ---
@router.delete(
    path="/{brand_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_brand(brand_id: int, session: SessionDepend):
    """Видалити бренд за ID."""
    existing_brand = await session.get(Brand, brand_id)
    if not existing_brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Brand with id={brand_id} not found."
        )

    await session.delete(existing_brand)
    await session.commit()
    return None