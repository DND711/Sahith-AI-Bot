from __future__ import annotations

from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, declarative_base, sessionmaker

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_URL = f"sqlite:///{DATA_DIR / 'app.db'}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    future=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)

Base = declarative_base()


def init_db() -> None:
    """Create database tables if they do not exist."""
    from . import models  # noqa: F401  # pylint: disable=unused-import

    try:
        Base.metadata.create_all(bind=engine, checkfirst=True)
    except OperationalError as exc:  # pragma: no cover - defensive guard
        # When the SQLite file is mounted via a persistent Docker volume the
        # metadata "create" call can race against an existing schema and emit
        # a noisy "table already exists" error. Treat that case as benign so
        # the API can continue to boot.
        if "already exists" not in str(exc).lower():
            raise


def get_db() -> Generator[Session, None, None]:
    """Yield a SQLAlchemy session for FastAPI dependencies."""

    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
