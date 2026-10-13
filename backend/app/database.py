import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DEFAULT_DATABASE_URL = "sqlite:///./fakeguard.db"


def normalize_database_url(url: str) -> str:
    """
    Accept the URL forms hosting providers hand out. Render and Heroku give
    ``postgres://`` / ``postgresql://`` URLs; SQLAlchemy needs an explicit
    driver to use psycopg 3 instead of the (uninstalled) psycopg2.
    """
    url = url.strip()
    for prefix in ("postgres://", "postgresql://"):
        if url.startswith(prefix):
            return "postgresql+psycopg://" + url[len(prefix):]
    return url


def make_engine(url: str) -> Engine:
    url = normalize_database_url(url)
    if url.startswith("sqlite"):
        return create_engine(url, connect_args={"check_same_thread": False})
    # pool_pre_ping recovers from connections dropped by the server or a proxy.
    return create_engine(url, pool_pre_ping=True)


DATABASE_URL = normalize_database_url(os.getenv("DATABASE_URL") or DEFAULT_DATABASE_URL)

engine = make_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db(bind: Engine = engine):
    # Import models so they are registered on Base.metadata before create_all.
    from . import models  # noqa: F401

    Base.metadata.create_all(bind=bind)

    # create_all() does not touch existing tables, so add any indexes that were
    # introduced after a database was first created. This is purely additive.
    for table in Base.metadata.sorted_tables:
        for index in table.indexes:
            index.create(bind=bind, checkfirst=True)
