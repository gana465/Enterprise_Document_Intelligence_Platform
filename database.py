"""
database.py
----------------------------------------
Database Configuration
Enterprise Document Intelligence Platform
----------------------------------------
"""

from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import sessionmaker

from config import DATABASE_URL


# ----------------------------------------------------
# SQLAlchemy Engine
# ----------------------------------------------------

engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True
)


# ----------------------------------------------------
# Session Factory
# ----------------------------------------------------

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False
)


# ----------------------------------------------------
# Base Class
# ----------------------------------------------------

class Base(DeclarativeBase):
    pass


# ----------------------------------------------------
# Dependency (FastAPI compatible)
# ----------------------------------------------------

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# ----------------------------------------------------
# Context Manager
# ----------------------------------------------------

@contextmanager
def session_scope():

    session = SessionLocal()

    try:

        yield session

        session.commit()

    except Exception:

        session.rollback()

        raise

    finally:

        session.close()


# ----------------------------------------------------
# Initialize Database
# ----------------------------------------------------

def init_db():

    from models import User
    from models import Document
    from models import SearchHistory

    Base.metadata.create_all(bind=engine)


# ----------------------------------------------------
# Reset Database
# ----------------------------------------------------

def reset_database():

    Base.metadata.drop_all(bind=engine)

    Base.metadata.create_all(bind=engine)