import os
import ssl
import certifi
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

# Locate Supabase root CA certificate
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SUPABASE_CA_CERT = os.path.join(BASE_DIR, "certs", "prod-ca-2021.crt")

# If connecting to Supabase connection pooler or remote PostgreSQL, disable statement cache for Supavisor compatibility and enforce strict verified TLS
if "pooler.supabase.com" in settings.ASYNC_DATABASE_URL or "supabase.co" in settings.ASYNC_DATABASE_URL or "postgresql" in settings.ASYNC_DATABASE_URL:
    if os.path.exists(SUPABASE_CA_CERT):
        ssl_ctx = ssl.create_default_context(cafile=SUPABASE_CA_CERT)
    else:
        ssl_ctx = ssl.create_default_context(cafile=certifi.where())
    ssl_ctx.check_hostname = True
    ssl_ctx.verify_mode = ssl.CERT_REQUIRED
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
    sync_conn_args = {"sslmode": "verify-full"}
    if os.path.exists(SUPABASE_CA_CERT):
        sync_conn_args["sslrootcert"] = SUPABASE_CA_CERT
    sync_engine_kwargs["connect_args"] = sync_conn_args

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
