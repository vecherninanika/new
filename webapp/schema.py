import re
from datetime import datetime
from typing import List, Optional

from dateutil import parser
from pydantic import BaseModel, Field


class CreateBook(BaseModel):
    title: str
    author: Optional[str] = None
    published_year: Optional[int] = Field(gt=1000, lt=datetime.now().year)
    isbn: Optional[str] = None
    created_at: Optional[str] = None

    def validate_isbn(self):
        isbn_pattern = re.compile(r"(?=(?:\D*\d){10}(?:(?:\D*\d){3})?$)")
        if self.isbn:
            if not isbn_pattern.match(self.isbn):
                raise ValueError("Invalid ISBN format")

    def validate_published_year(self):
        if self.published_year:
            if self.published_year not in list(range(1000, datetime.now().year)):
                raise ValueError(
                    "Published year should be greater than 1000 and less than current year"
                )


class UpdateBook(BaseModel):
    title: str
    author: Optional[str] = None
    published_year: Optional[int] = Field(gt=1000, lt=datetime.now().year)
    isbn: Optional[str] = None

    def validate_isbn(self):
        isbn_pattern = re.compile(r"(?=(?:\D*\d){10}(?:(?:\D*\d){3})?$)")
        if self.isbn:
            if not isbn_pattern.match(self.isbn):
                raise ValueError(message="Invalid ISBN format")

    def validate_published_year(self):
        if self.published_year:
            if self.published_year not in list(range(1000, datetime.now().year)):
                raise ValueError(
                    message="Published year should be greater than 1000 and less than current year"
                )


class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    published_year: int
    isbn: str
    created_at: Optional[parser.isoparse]


class BooksResponse(BaseModel):
    books: List[BookResponse]
