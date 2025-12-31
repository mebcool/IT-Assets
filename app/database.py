
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy import event
import os
from sqlalchemy import create_engine


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

engine = create_engine(DATABASE_URL)

class Base(DeclarativeBase):
    pass

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Ensure SQLite enforces foreign keys
@event.listens_for(engine, 'connect')
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute('PRAGMA foreign_keys=ON')
    cursor.close()
