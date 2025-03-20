# app/db/session.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Lấy URL từ biến môi trường hoặc sử dụng URL mặc định
SQLALCHEMY_DATABASE_URI = os.environ.get("SQL_DATABASE_URL", "postgresql+psycopg2://postgres:postgres@db:5432/app")

engine = create_engine(SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    Dependency for getting a database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()