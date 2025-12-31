
# app/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# 1) Get DATABASE_URL from env; default to local SQLite for development
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

# 2) If using Render Postgres and URL does not include sslmode, add it
#    (Most Internal URLs already have ?sslmode=require; this is a safe guard.)
if DATABASE_URL.startswith("postgresql://") and "sslmode=" not in DATABASE_URL:
    sep = "&" if "?" in DATABASE_URL else "?"
    DATABASE_URL = f"{DATABASE_URL}{sep}sslmode=require"

# 3) Create engine with sensible pool settings for production
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,   # checks connection health
    pool_size=5,          # small pool for free tier
    max_overflow=10,      # allow bursts
    future=True,          # SQLAlchemy 2.0-style engine
)

class Base(DeclarativeBase):
    pass

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# 4) Only enable SQLite foreign keys when actually using SQLite
if DATABASE_URL.startswith("sqlite://"):
    from sqlalchemy import event

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
