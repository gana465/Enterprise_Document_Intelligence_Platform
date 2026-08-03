"""
models.py
----------------------------------------
Database Models
Enterprise Document Intelligence Platform
----------------------------------------
"""

from datetime import datetime
from typing import List

from sqlalchemy import (
    String,
    Text,
    Integer,
    Float,
    Boolean,
    ForeignKey,
    DateTime,
    Index
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from database import Base


# ----------------------------------------------------
# User Model
# ----------------------------------------------------

class User(Base):

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    username: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    email: Mapped[str] = mapped_column(
        String(200),
        unique=True,
        nullable=False,
        index=True
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    role: Mapped[str] = mapped_column(
        String(30),
        default="User"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    last_login: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    documents: Mapped[List["Document"]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan"
    )

    searches: Mapped[List["SearchHistory"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def __repr__(self):

        return f"<User(username='{self.username}')>"


# ----------------------------------------------------
# Document Model
# ----------------------------------------------------

class Document(Base):

    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    filepath: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )

    filetype: Mapped[str] = mapped_column(
        String(30)
    )

    filesize: Mapped[float] = mapped_column(
        Float
    )

    pages: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    extracted_text: Mapped[str] = mapped_column(
        Text
    )

    summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    embedding_created: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    upload_time: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        index=True
    )

    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id")
    )

    owner: Mapped["User"] = relationship(
        back_populates="documents"
    )

    def __repr__(self):

        return f"<Document(title='{self.title}')>"


# ----------------------------------------------------
# Search History
# ----------------------------------------------------

class SearchHistory(Base):

    __tablename__ = "search_history"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    query: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    similarity_score: Mapped[float] = mapped_column(
        Float,
        default=0
    )

    searched_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    results_found: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id")
    )

    user: Mapped["User"] = relationship(
        back_populates="searches"
    )


# ----------------------------------------------------
# Indexes
# ----------------------------------------------------

Index(
    "idx_document_title",
    Document.title
)

Index(
    "idx_document_filename",
    Document.filename
)

Index(
    "idx_search_query",
    SearchHistory.query
)