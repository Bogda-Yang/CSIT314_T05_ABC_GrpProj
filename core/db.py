from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from core.config import DATABASE_URL


engine_options = {
    "pool_pre_ping": True,
    "future": True,
}
if DATABASE_URL.startswith("sqlite"):
    engine_options["connect_args"] = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    **engine_options,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_session() -> Session:
    return SessionLocal()
