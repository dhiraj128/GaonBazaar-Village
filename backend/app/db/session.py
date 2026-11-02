import ssl
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

# If connecting to Supabase connection pooler or remote PostgreSQL, disable statement cache for Supavisor compatibility and enforce robust SSL context
if "pooler.supabase.com" in settings.ASYNC_DATABASE_URL or "supabase.co" in settings.ASYNC_DATABASE_URL or "postgresql" in settings.ASYNC_DATABASE_URL:
    ssl_ctx = ssl.create_default_context()
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_NONE
    async_engine_kwargs["connect_args"] = {
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0,
        "ssl": ssl_ctx,
        "command_timeout": 15,
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
sync_engine_kwargs = {
    "echo": False,
    "future": True,
    "pool_pre_ping": True,
}
if "pooler.supabase.com" in settings.RESOLVED_SYNC_DATABASE_URL or "supabase.co" in settings.RESOLVED_SYNC_DATABASE_URL or "postgresql" in settings.RESOLVED_SYNC_DATABASE_URL:
    sync_engine_kwargs["connect_args"] = {"sslmode": "require"}

sync_engine = create_engine(
    settings.RESOLVED_SYNC_DATABASE_URL,
    **sync_engine_kwargs
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
