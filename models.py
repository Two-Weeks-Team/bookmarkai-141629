import os
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    DateTime,
    ForeignKey,
    Table,
    Boolean,
    Text,
    create_engine,
)
from sqlalchemy.orm import relationship, sessionmaker, declarative_base

# ---------------------------------------------------------------------------
# Database URL handling (includes auto‑fix for async schemes and sslmode)
# ---------------------------------------------------------------------------
raw_url = os.getenv("DATABASE_URL", os.getenv("POSTGRES_URL", "sqlite:///./app.db"))
if raw_url.startswith("postgresql+asyncpg://"):
    raw_url = raw_url.replace("postgresql+asyncpg://", "postgresql+psycopg://")
elif raw_url.startswith("postgres://"):
    raw_url = raw_url.replace("postgres://", "postgresql+psycopg://")

# Determine if we need SSL (non‑localhost and not sqlite)
connect_args = {}
if not raw_url.startswith("sqlite") and "localhost" not in raw_url and "127.0.0.1" not in raw_url:
    connect_args["sslmode"] = "require"

engine = create_engine(raw_url, connect_args=connect_args, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

# ---------------------------------------------------------------------------
# Association table for many‑to‑many Bookmark <-> Tag relationship
# ---------------------------------------------------------------------------
bookmark_tag_table = Table(
    "bm_bookmark_tags",
    Base.metadata,
    Column("bookmark_id", String, ForeignKey("bm_bookmarks.id"), primary_key=True),
    Column("tag_id", String, ForeignKey("bm_tags.id"), primary_key=True),
    Column("confidence_score", String, default="0.0"),
)

# ---------------------------------------------------------------------------
# Core models
# ---------------------------------------------------------------------------
class Bookmark(Base):
    __tablename__ = "bm_bookmarks"

    id = Column(String, primary_key=True, index=True)
    url = Column(String, nullable=False, unique=True)
    title = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_archived = Column(Boolean, default=False)
    # Relationships
    tags = relationship("Tag", secondary=bookmark_tag_table, backref="bookmarks")
    # For simplicity we store the AI‑generated summary directly here
    short_summary = Column(Text)
    detailed_summary = Column(Text)

class Tag(Base):
    __tablename__ = "bm_tags"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    parent_id = Column(String, ForeignKey("bm_tags.id"), nullable=True)
    confidence_score = Column(String, default="0.0")
    # Self‑referential relationship for hierarchy (no type annotation on relationship)
    parent = relationship("Tag", remote_side=[id], backref="children")

# ---------------------------------------------------------------------------
# Helper for dependency injection
# ---------------------------------------------------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
