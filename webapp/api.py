from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import ORJSONResponse
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from webapp.models.sirius.book import Book
from webapp.postgres import get_session
from webapp.schema import *

book_router = APIRouter(prefix="/book")


@book_router.post(
    "/create",
    response_model=BookResponse,
)
async def create_book(
    body: CreateBook, session: AsyncSession = Depends(get_session)
) -> ORJSONResponse:
    try:
        body.validate_isbn()
        body.validate_published_year()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=e.message
        )

    async with session.begin_nested():
        async with session.begin_nested():
            data_dict = body.dict(exclude_unset=True)
            book = Book(**data_dict)
            session.add(book)
            await session.flush()
            await session.commit()

    return ORJSONResponse(
        {
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "published_year": book.published_year,
            "isbn": book.isbn,
            "created_at": book.created_at,
        }
    )


@book_router.get(
    "/read_all",
    response_model=BooksResponse,
)
async def read_books(
    session: AsyncSession = Depends(get_session),
) -> ORJSONResponse:
    books = (await session.scalars(select(Book))).all()

    return ORJSONResponse(
        [
            {
                "id": book.id,
                "title": book.title,
                "author": book.author,
                "published_year": book.published_year,
                "isbn": book.isbn,
                "created_at": book.created_at,
            }
            for book in books
        ]
    )


@book_router.get(
    "/read/{book_id}",
    response_model=BookResponse,
)
async def read_book(
    book_id: int,
    session: AsyncSession = Depends(get_session),
) -> ORJSONResponse:
    book = (await session.scalars(select(Book).where(Book.id == book_id))).one_or_none()

    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} does not exist",
        )

    return ORJSONResponse(
        {
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "published_year": book.published_year,
            "isbn": book.isbn,
            "created_at": book.created_at,
        }
    )


@book_router.post(
    "/update/{book_id}",
    response_model=BookResponse,
)
async def update_updated(
    book_id: int, body: UpdateBook, session: AsyncSession = Depends(get_session)
) -> ORJSONResponse:
    try:
        body.validate_isbn()
        body.validate_published_year()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=e.message
        )

    data = body.dict()
    await session.execute(update(Book).where(Book.id == book_id).values(**data))
    updated = (
        await session.scalars(select(Book).where(Book.id == book_id))
    ).one_or_none()
    await session.commit()

    if updated.id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Book "{body.title}" does not exist',
        )

    return ORJSONResponse(
        {
            "id": updated.id,
            "title": updated.title,
            "author": updated.author,
            "published_year": updated.published_year,
            "isbn": updated.isbn,
            "created_at": updated.created_at,
        }
    )


@book_router.post(
    "/delete/{book_id}",
    response_model=CreateBook,
)
async def delete_book(
    book_id: int, session: AsyncSession = Depends(get_session)
) -> ORJSONResponse:
    deleted_id = (
        await session.execute(delete(Book).where(Book.id == book_id).returning(Book.id))
    ).one_or_none()[0]
    await session.commit()

    if deleted_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} does not exist",
        )

    return ORJSONResponse({"id": deleted_id})
