from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from core.config import POSTGRES_URL

if not POSTGRES_URL:
    raise RuntimeError("POSTGRES_URL is not set. Add it to your .env.")

Base = declarative_base()

engine = create_async_engine(
    POSTGRES_URL,
    echo=False,
    pool_pre_ping=True,
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
