from __future__ import annotations

from typing import Iterator

from sqlalchemy.orm import Session

from .database import SessionLocal


def get_db() -> Iterator[Session]:
    """Yield a scoped SQLAlchemy session for each request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
