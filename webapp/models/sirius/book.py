import re

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from webapp.models.meta import Base


class Book(Base):
    __tablename__ = "book"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    author: Mapped[str] = mapped_column(String(150), nullable=True)
    published_year: Mapped[int] = mapped_column(Integer)
    isbn: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())

    def validate_isbn(self):
        isbn_pattern = re.compile(r"^978[-\s]?[0-9]{10}$")
        if not isbn_pattern.match(self.isbn):
            raise ValueError("Invalid ISBN format")
