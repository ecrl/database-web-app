from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base

from src.config import DATABASE_URL


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


@contextmanager
def get_db() -> Iterator[Session]:
    """A session that is closed (its connection returned to the pool) when
    the `with` block ends, including on an exception. Use as
    `with get_db() as db:`; `next(get_db())` left sessions to the garbage
    collector, which leaked pool connections until searches timed out."""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_db_and_tables() -> None:

    Base.metadata.create_all(bind=engine)
