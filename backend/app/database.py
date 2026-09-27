import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Get Database URL from environment or fallback to a local PostgreSQL instance
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/smart_store_db"
)

# Render / Heroku compatibility fix for 'postgres://' vs 'postgresql://'
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# pool_pre_ping avoids "server closed the connection" errors on free-tier
# Postgres instances (like Render's) that recycle idle connections.
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency to yield a clean database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
