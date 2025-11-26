from typing import List
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload

from core.models.product import Product
from dependencies import SessionDepend
from schemas.products import (
    ProductCreateSchema,
    ProductResponseSchema,
    ProductPartialUpdateSchema
)


router = APIRouter(prefix="/products", tags=["Products"])


@router.get(
    path="/",
    response_model=List[ProductResponseSchema],
    status_code=status.HTTP_200_OK,
)
async def get_products(session: SessionDepend):
    """Отримати список всіх товарів."""
    query = select(Product).options(
        selectinload(Product.category),
        selectinload(Product.brand)
    )
    result = await session.execute(query)
    return result.scalars().all()


@router.get(
    path="/{product_id}",
    response_model=ProductResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_product(product_id: int, session: SessionDepend):
    """Отримати один товар за ID."""
    query = select(Product).filter(Product.id == product_id).options(
        selectinload(Product.category),
        selectinload(Product.brand)
    )
    result = await session.execute(query)
    existing_product = result.scalars().first()

    if not existing_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id={product_id} not found."
        )
    return existing_product


@router.post(
    path="/",
    response_model=ProductResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_product(
        product: ProductCreateSchema,
        session: SessionDepend
):
    """Створити новий товар."""
    product_data = product.model_dump()

    new_product = Product(**product_data)

    session.add(new_product)

    try:
        await session.commit()
        await session.refresh(new_product)
        return new_product
    except SQLAlchemyError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating product: {e}"
        )


@router.put(
    path="/{product_id}",
    response_model=ProductResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def update_product(
        product_id: int,
        product: ProductCreateSchema,
        session: SessionDepend
):
    """Повністю оновити товар за ID."""

    existing_product = await session.get(Product, product_id)

    if not existing_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id={product_id} not found."
        )

    update_data = product.model_dump()

    for field, value in update_data.items():
        setattr(existing_product, field, value)

    try:
        await session.commit()
        await session.refresh(existing_product)
        return existing_product
    except SQLAlchemyError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating product: {e}"
        )


@router.patch(
    path="/{product_id}",
    response_model=ProductResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def partial_update_product(
        product_id: int,
        product: ProductPartialUpdateSchema,
        session: SessionDepend
):
    """Частково оновити товар за ID (оновити лише передані поля)."""

    existing_product = await session.get(Product, product_id)

    if not existing_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id={product_id} not found."
        )

    update_data = product.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(existing_product, field, value)

    try:
        await session.commit()
        await session.refresh(existing_product)
        return existing_product
    except SQLAlchemyError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating product: {e}"
        )


@router.delete(
    path="/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_product(product_id: int, session: SessionDepend):
    """Видалити товар за ID."""

    existing_product = await session.get(Product, product_id)

    if not existing_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id={product_id} not found."
        )

    await session.delete(existing_product)
    await session.commit()

    return None