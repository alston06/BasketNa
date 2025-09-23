import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Build default SQLite URL pointing to <project_root>/data/basketna.db
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_default_sqlite_path = os.path.join(_project_root, "backend", "data", "basketna.db")
os.makedirs(os.path.dirname(_default_sqlite_path), exist_ok=True)
_default_sqlite_url = f"sqlite:///{_default_sqlite_path.replace(os.sep, '/')}"

DATABASE_URL = os.getenv("DATABASE_URL", _default_sqlite_url)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base() 