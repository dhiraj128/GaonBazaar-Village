from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Async engine for FastAPI endpoints
async_engine_kwargs = {
    "echo": False,
    "future": True,
    "pool_pre_ping": True,
}

# If connecting to Supabase connection pooler or remote PostgreSQL, disable statement cache for Supavisor compatibility and enforce SSL
if "pooler.supabase.com" in settings.ASYNC_DATABASE_URL or "supabase.co" in settings.ASYNC_DATABASE_URL:
    async_engine_kwargs["connect_args"] = {
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0,
        "ssl": "require",
    }

async_engine = create_async_engine(
    settings.ASYNC_DATABASE_URL,
    **async_engine_kwargs
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Sync engine for seed scripts / migrations
sync_engine = create_engine(
    settings.RESOLVED_SYNC_DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True
)

SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
