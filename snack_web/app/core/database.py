import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

POSTGRES_USER = os.getenv("POSTGRES_USER", "snack_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "snack_pass")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "db")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "snack_db")

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# Remove query parameters from URL and use connect_args instead
# This ensures psycopg2 receives SSL settings correctly
connect_args = {}
if DATABASE_URL and ("neon.tech" in DATABASE_URL or "sslmode=require" in DATABASE_URL):
    # Strip query parameters from URL
    parsed = urlparse(DATABASE_URL)
    # Rebuild URL without query string
    DATABASE_URL = urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        '',  # params
        '',  # query - removed
        ''   # fragment
    ))
    # Set SSL mode in connect_args
    connect_args = {"sslmode": "require"}

engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
