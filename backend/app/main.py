import os
import json
import logging
import asyncio
import secrets
from typing import Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI, Header, HTTPException, status, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.future import select
from sqlalchemy import text

from app.core.config import settings
from app.core.ws import ws_manager
from app.db.session import async_engine, AsyncSessionLocal
from app.models.base import Base, User, Store, StoreProduct, GlobalCatalogItem, Runner, Address, OrderMessage, Notification, MonthlyRationList, MonthlyRationItem
from app.api.v1 import auth, addresses, stores, orders, ai, admin, support, payments, notifications, ration_lists, kyc

logger = logging.getLogger("gaonbazaar")

async def init_db_and_seed():
    # 1. Initialize DB base tables in dedicated, committed transaction
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 2. Upgrade existing PostgreSQL columns to TIMESTAMPTZ (each in isolated safe transaction)
    if "postgresql" in settings.ASYNC_DATABASE_URL:
        alter_stmts = [
            "ALTER TABLE users ALTER COLUMN created_at TYPE TIMESTAMPTZ USING created_at AT TIME ZONE 'UTC';",
            "ALTER TABLE users ALTER COLUMN updated_at TYPE TIMESTAMPTZ USING updated_at AT TIME ZONE 'UTC';",
            "ALTER TABLE addresses ALTER COLUMN created_at TYPE TIMESTAMPTZ USING created_at AT TIME ZONE 'UTC';",
            "ALTER TABLE stores ALTER COLUMN created_at TYPE TIMESTAMPTZ USING created_at AT TIME ZONE 'UTC';",
            "ALTER TABLE orders ALTER COLUMN placed_at TYPE TIMESTAMPTZ USING placed_at AT TIME ZONE 'UTC';",
            "ALTER TABLE orders ALTER COLUMN cancel_until TYPE TIMESTAMPTZ USING cancel_until AT TIME ZONE 'UTC';",
            "ALTER TABLE orders ALTER COLUMN delivered_at TYPE TIMESTAMPTZ USING delivered_at AT TIME ZONE 'UTC';",
            "ALTER TABLE order_timeline ALTER COLUMN timestamp TYPE TIMESTAMPTZ USING timestamp AT TIME ZONE 'UTC';",
            "ALTER TABLE support_tickets ALTER COLUMN created_at TYPE TIMESTAMPTZ USING created_at AT TIME ZONE 'UTC';",
            "ALTER TABLE audit_logs ALTER COLUMN created_at TYPE TIMESTAMPTZ USING created_at AT TIME ZONE 'UTC';",
            "ALTER TABLE otp_challenges ALTER COLUMN created_at TYPE TIMESTAMPTZ USING created_at AT TIME ZONE 'UTC';",
            "ALTER TABLE otp_challenges ALTER COLUMN expires_at TYPE TIMESTAMPTZ USING expires_at AT TIME ZONE 'UTC';",
        ]
        for stmt in alter_stmts:
            try:
                async with async_engine.begin() as conn:
                    await conn.execute(text(stmt))
            except Exception as exc:
                logger.debug("TIMESTAMPTZ upgrade notice for '%s': %s", stmt[:40], exc)

    # 3. Ensure supplemental columns and tables exist using safe IF NOT EXISTS
    is_pg = "postgresql" in settings.ASYNC_DATABASE_URL
    add_col_prefix = "ALTER TABLE users ADD COLUMN IF NOT EXISTS " if is_pg else "ALTER TABLE users ADD COLUMN "
    add_order_prefix = "ALTER TABLE orders ADD COLUMN IF NOT EXISTS " if is_pg else "ALTER TABLE orders ADD COLUMN "
    add_ticket_prefix = "ALTER TABLE support_tickets ADD COLUMN IF NOT EXISTS " if is_pg else "ALTER TABLE support_tickets ADD COLUMN "
    add_store_prefix = "ALTER TABLE stores ADD COLUMN IF NOT EXISTS " if is_pg else "ALTER TABLE stores ADD COLUMN "
    add_runner_prefix = "ALTER TABLE runners ADD COLUMN IF NOT EXISTS " if is_pg else "ALTER TABLE runners ADD COLUMN "

    migration_stmts = [
        f"{add_col_prefix}avatar_url VARCHAR(500);",
        f"{add_col_prefix}primary_village VARCHAR(100);",
        f"{add_col_prefix}primary_panchayat VARCHAR(100);",
        f"{add_col_prefix}kyc_status VARCHAR(50) DEFAULT 'unverified';",
        f"{add_col_prefix}pan_number VARCHAR(20);",
        f"{add_col_prefix}pan_name VARCHAR(150);",
        f"{add_col_prefix}aadhaar_number VARCHAR(20);",
        f"{add_col_prefix}aadhaar_data JSONB;" if is_pg else f"{add_col_prefix}aadhaar_data TEXT;",
        f"{add_col_prefix}kyc_photo_url VARCHAR(500);",
        f"{add_col_prefix}payout_account_verified BOOLEAN DEFAULT FALSE;",
        f"{add_order_prefix}online_gateway_fee FLOAT DEFAULT 0.0;",
        f"{add_order_prefix}collection_mode VARCHAR(30) DEFAULT 'CASH';",
        f"{add_order_prefix}payment_order_id VARCHAR(100);",
        f"{add_order_prefix}transaction_id VARCHAR(100);",
        f"{add_ticket_prefix}category VARCHAR(50) DEFAULT 'GENERAL_HELP';",
        f"{add_ticket_prefix}affected_product_id VARCHAR(50);",
        f"{add_ticket_prefix}attachment_url TEXT;",
        f"{add_ticket_prefix}resolution_notes TEXT;",
        f"{add_ticket_prefix}resolved_at TIMESTAMP WITH TIME ZONE;",
        f"{add_ticket_prefix}updated_at TIMESTAMP WITH TIME ZONE;",
        f"{add_order_prefix}distance_km FLOAT DEFAULT 0.8;",
        f"{add_order_prefix}runner_payout FLOAT DEFAULT 10.0;",
        f"{add_store_prefix}rejection_reason TEXT;",
        f"{add_runner_prefix}rejection_reason TEXT;",
                """CREATE TABLE IF NOT EXISTS monthly_ration_lists (
            id VARCHAR(36) PRIMARY KEY,
            user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            name VARCHAR(100) NOT NULL DEFAULT 'My Monthly Ration',
            is_active BOOLEAN DEFAULT TRUE NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE,
            updated_at TIMESTAMP WITH TIME ZONE
        );""",
        """CREATE TABLE IF NOT EXISTS monthly_ration_items (
            id VARCHAR(36) PRIMARY KEY,
            list_id VARCHAR(36) NOT NULL REFERENCES monthly_ration_lists(id) ON DELETE CASCADE,
            product_id VARCHAR(50),
            product_name_en VARCHAR(150) NOT NULL,
            product_name_hi VARCHAR(150),
            unit VARCHAR(50) NOT NULL DEFAULT '1 kg',
            quantity INTEGER NOT NULL DEFAULT 1,
            notes VARCHAR(255),
            created_at TIMESTAMP WITH TIME ZONE
        );""",
        """CREATE TABLE IF NOT EXISTS notifications (
            id VARCHAR(36) PRIMARY KEY,
            user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            title VARCHAR(200) NOT NULL,
            body TEXT NOT NULL,
            type VARCHAR(50) DEFAULT 'system',
            is_read BOOLEAN DEFAULT FALSE NOT NULL,
            metadata_json TEXT,
            created_at TIMESTAMP WITH TIME ZONE
        );""",
        """CREATE TABLE IF NOT EXISTS refunds (
            id VARCHAR(36) PRIMARY KEY,
            order_id VARCHAR(36) NOT NULL REFERENCES orders(id),
            payment_id VARCHAR(100),
            gateway_refund_id VARCHAR(100),
            amount FLOAT NOT NULL,
            currency VARCHAR(10) DEFAULT 'INR',
            reason VARCHAR(255),
            status VARCHAR(30) DEFAULT 'COMPLETED',
            refund_type VARCHAR(30) DEFAULT 'FULL',
            created_by VARCHAR(36) REFERENCES users(id),
            admin_notes TEXT,
            created_at TIMESTAMP WITH TIME ZONE,
            updated_at TIMESTAMP WITH TIME ZONE
        );""",
        """CREATE TABLE IF NOT EXISTS replacements (
            id VARCHAR(36) PRIMARY KEY,
            original_order_id VARCHAR(36) NOT NULL REFERENCES orders(id),
            ticket_id VARCHAR(36) REFERENCES support_tickets(id),
            customer_id VARCHAR(36) NOT NULL REFERENCES users(id),
            store_id VARCHAR(36) NOT NULL REFERENCES stores(id),
            runner_id VARCHAR(36) REFERENCES runners(id),
            status VARCHAR(30) DEFAULT 'REQUESTED',
            reason VARCHAR(255) NOT NULL,
            items_json TEXT NOT NULL,
            customer_due FLOAT DEFAULT 0.0,
            delivery_otp VARCHAR(10),
            admin_notes TEXT,
            rejection_reason TEXT,
            created_at TIMESTAMP WITH TIME ZONE,
            updated_at TIMESTAMP WITH TIME ZONE
        );""",
    ]
    for stmt in migration_stmts:
        try:
            async with async_engine.begin() as conn:
                await conn.execute(text(stmt))
        except Exception as exc:
            logger.debug("Schema migration notice: %s", exc)

    try:
        async with async_engine.begin() as conn:
            if async_engine.dialect.name == "sqlite":
                await conn.execute(text("ALTER TABLE runners ADD COLUMN last_location_updated_at TIMESTAMP;"))
            else:
                await conn.execute(text("ALTER TABLE runners ADD COLUMN IF NOT EXISTS last_location_updated_at TIMESTAMP WITH TIME ZONE;"))
    except Exception as exc:
        logger.debug("Schema migration notice (runners.last_location_updated_at): %s", exc)

    # 3b. Ensure otp_challenges table and all its columns exist
    otp_cols = [
        ("code", "VARCHAR(20)"),
        ("used", "BOOLEAN DEFAULT FALSE"),
        ("verified", "BOOLEAN DEFAULT FALSE"),
        ("delivery_status", "VARCHAR(50) DEFAULT 'delivered'"),
    ]
    for col_name, col_type in otp_cols:
        try:
            async with async_engine.begin() as conn:
                if async_engine.dialect.name == "sqlite":
                    await conn.execute(text(f"ALTER TABLE otp_challenges ADD COLUMN {col_name} {col_type};"))
                else:
                    await conn.execute(text(f"ALTER TABLE otp_challenges ADD COLUMN IF NOT EXISTS {col_name} {col_type};"))
        except Exception as exc:
            logger.debug("Schema migration notice (otp_challenges.%s): %s", col_name, exc)

    # 3c. Supabase PostgreSQL Row-Level Security (RLS) auto-enforcement across all public tables
    if "postgresql" in settings.ASYNC_DATABASE_URL:
        rls_sweep_stmt = """
        DO $$
        DECLARE
            r RECORD;
        BEGIN
            FOR r IN (
                SELECT tablename 
                FROM pg_tables 
                WHERE schemaname = 'public'
            ) LOOP
                EXECUTE format('ALTER TABLE public.%I ENABLE ROW LEVEL SECURITY;', r.tablename);
            END LOOP;
        END $$;
        """
        try:
            async with async_engine.begin() as conn:
                await conn.execute(text(rls_sweep_stmt))
            logger.info("Supabase PostgreSQL Row-Level Security (RLS) successfully verified on all public tables")
        except Exception as exc:
            logger.debug("RLS auto-enforcement notice: %s", exc)

    # 4. Update verified product image URLs in existing database rows
    url_updates = [
        ("cat_mustard_oil", "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=500&q=80"),
        ("cat_soy_oil", "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=500&q=80"),
        ("cat_atta", "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=500&q=80"),
        ("cat_salt", "https://images.unsplash.com/photo-1518110903415-32e5b77c1d76?w=500&q=80"),
        ("cat_led_bulb", "https://images.unsplash.com/photo-1550985543-f47f38aeee65?w=500&q=80"),
        ("cat_tomato", "https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=500&q=80"),
        ("cat_toor_dal", "https://images.unsplash.com/photo-1585994192701-f1a505c817ea?w=500&q=80"),
        ("cat_moong_dal", "https://images.unsplash.com/photo-1585994192701-f1a505c817ea?w=500&q=80"),
        ("cat_chana_dal", "https://images.unsplash.com/photo-1585994192701-f1a505c817ea?w=500&q=80"),
        ("cat_bath_soap", "https://images.unsplash.com/photo-1600857544200-b2f666a9a2ec?w=500&q=80"),
        ("cat_detergent", "https://images.unsplash.com/photo-1585421514738-01798e348b17?w=500&q=80"),
    ]
    try:
        async with async_engine.begin() as conn:
            for cat_id, new_url in url_updates:
                await conn.execute(
                    text("UPDATE global_catalog SET image_url = :url WHERE id = :id"),
                    {"url": new_url, "id": cat_id}
                )
                await conn.execute(
                    text("""
                        UPDATE store_products 
                        SET image_url = :url 
                        WHERE global_product_id = :id 
                          AND (
                            image_url IS NULL 
                            OR image_url = '' 
                            OR image_url LIKE '%photo-1509440159596-0249088772ff%'
                            OR image_url LIKE '%photo-1515543237350-b3eea1ec8082%'
                            OR image_url LIKE '%photo-1626082896492-766af4eb6501%'
                            OR image_url LIKE '%photo-1584308666744-24d5c474f2ae%'
                            OR image_url LIKE '%photo-1620916566398-39f1143ab7be%' 
                            OR image_url LIKE '%photo-1507668077129-56e32842fceb%'
                            OR image_url LIKE '%Dune_Aura%'
                            OR image_url LIKE '%upload.wikimedia.org%'
                            OR image_url LIKE '%photo-1546470427-227c7369a941%'
                            OR image_url LIKE '%photo-1607006314144-8849b2f67232%'
                          )
                    """),
                    {"url": new_url, "id": cat_id}
                )
    except Exception as exc:
        logger.debug("Product image URL update notice: %s", exc)
        
    # Ensure Super Admin (9800000099) and Hub Manager (9800000098) always exist in DB
    async with AsyncSessionLocal() as session:
        adm_check = await session.execute(select(User).where(User.phone == "9800000099"))
        if not adm_check.scalars().first():
            session.add(User(
                id="usr_admin_01",
                phone="9800000099",
                name="GaonBazaar Super Admin",
                role="admin",
                preferred_language="en",
                is_active=True
            ))
        hub_check = await session.execute(select(User).where(User.phone == "9800000098"))
        if not hub_check.scalars().first():
            session.add(User(
                id="usr_hub_01",
                phone="9800000098",
                name="Minapur Hub Manager",
                role="hub_manager",
                preferred_language="hi",
                is_active=True
            ))
        await session.commit()

async def run_resilient_init_db(app: FastAPI):
    max_retries = 3
    retry_delay = 2
    for attempt in range(1, max_retries + 1):
        try:
            logger.info("Initializing database schema (attempt %d/%d)...", attempt, max_retries)
            await init_db_and_seed()
            app.state.db_healthy = True
            app.state.db_error = None
            logger.info("Database schema verified and admin accounts synchronized successfully.")
            return
        except Exception as exc:
            app.state.db_healthy = False
            app.state.db_error = str(exc)
            logger.warning("Database initialization attempt %d/%d encountered error: %s", attempt, max_retries, exc)
            if attempt < max_retries:
                await asyncio.sleep(retry_delay)
            else:
                logger.error(
                    "Database initialization could not complete during startup. "
                    "Web server will remain online to serve health checks and retry queries."
                )

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db_healthy = False
    app.state.db_error = None
    
    if settings.TESTING:
        # In test environments, synchronously initialize schema and seed data
        await run_resilient_init_db(app)
        yield
    else:
        # In production/staging, launch database initialization asynchronously in the background
        # so FastAPI immediately binds to $PORT and satisfies Render platform health checks
        init_task = asyncio.create_task(run_resilient_init_db(app))
        yield
        if not init_task.done():
            init_task.cancel()

is_prod = settings.ENVIRONMENT.lower() == "production"
if is_prod:
    if not settings.SECRET_KEY or settings.SECRET_KEY.startswith("dev-insecure-"):
        raise RuntimeError("Production JWT signing key is not configured securely")
    if not settings.ADMIN_API_KEY or settings.ADMIN_API_KEY.startswith("dev-insecure-"):
        raise RuntimeError("Production administrative API key is not configured securely")
    if getattr(settings, "TESTING", False):
        raise RuntimeError("TESTING mode must not be enabled in production")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url=None if is_prod else "/docs",
    redoc_url=None if is_prod else "/redoc",
    openapi_url=None if is_prod else "/openapi.json"
)

prod_origins = [
    "https://apnagaonbazaar.in",
    "https://www.apnagaonbazaar.in",
    "https://dukaan.apnagaonbazaar.in",
    "https://mitra.apnagaonbazaar.in",
    "https://admin.apnagaonbazaar.in",
    "https://gaonbazaar-village.onrender.com",
]

dev_origins = prod_origins + [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "http://localhost:3003",
    "http://localhost:5173",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=prod_origins if is_prod else dev_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Attach API routes
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(addresses.router, prefix=settings.API_V1_STR)
app.include_router(stores.router, prefix=settings.API_V1_STR)
app.include_router(orders.router, prefix=settings.API_V1_STR)
app.include_router(ai.router, prefix=settings.API_V1_STR)
app.include_router(admin.router, prefix=settings.API_V1_STR)
app.include_router(support.router, prefix=settings.API_V1_STR)
app.include_router(payments.router, prefix=settings.API_V1_STR)
app.include_router(notifications.router, prefix=settings.API_V1_STR)
app.include_router(ration_lists.router, prefix=settings.API_V1_STR)
app.include_router(kyc.router, prefix=settings.API_V1_STR)

@app.websocket("/ws/orders")
@app.websocket("/ws/{client_role}")
async def websocket_orders_endpoint(
    websocket: WebSocket,
    client_role: str = "all",
    token: Optional[str] = Query(None)
):
    await ws_manager.connect(websocket, role=client_role, token=token)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                if msg.get("action") == "ping":
                    await websocket.send_text(json.dumps({"event": "pong"}))
            except Exception:
                pass
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as exc:
        logger.debug("WS connection ended: %s", exc)
        ws_manager.disconnect(websocket)

@app.get("/")
async def root():
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "pilot_location": f"{settings.PILOT_BLOCK}, {settings.PILOT_DISTRICT}, {settings.PILOT_STATE}",
        "max_delivery_radius_km": settings.MAX_DELIVERY_RADIUS_KM,
        "platform_fee": settings.PLATFORM_FEE,
        "cancel_window_seconds": settings.CUSTOMER_CANCEL_WINDOW_SECONDS,
        "docs_url": "/docs"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database": "connected" if getattr(app.state, "db_healthy", False) else "initializing",
        "commit": os.getenv("RENDER_GIT_COMMIT", "latest")
    }

@app.get("/health/db")
async def health_db():
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT 1"))
            val = result.scalar()
            is_healthy = bool(getattr(app.state, "db_healthy", False))
            if not is_healthy and val == 1:
                try:
                    store_check = await session.execute(text("SELECT 1 FROM stores LIMIT 1"))
                    if store_check.scalar() is not None:
                        app.state.db_healthy = True
                        is_healthy = True
                except Exception:
                    pass
            return {
                "status": "connected",
                "database_engine": "postgresql" if "postgresql" in settings.ASYNC_DATABASE_URL else "sqlite",
                "ping": val == 1,
                "readiness": "ready" if is_healthy else "degraded",
                "schema_seeded": is_healthy
            }
    except Exception as exc:
        logger.error("Health check database probe failed: %s", exc)
        return {
            "status": "disconnected",
            "readiness": "offline",
            "detail": "Database connection attempt failed"
        }

@app.post("/api/v1/system/seed-database")
async def seed_database(
    x_admin_key: Optional[str] = Header(None, alias="X-Admin-Key"),
    authorization: Optional[str] = Header(None)
):
    """
    Restricted maintenance endpoint to trigger schema sync and table verification.
    Requires authorized Admin credentials or X-Admin-Key.
    """
    is_authorized = False
    if x_admin_key and secrets.compare_digest(x_admin_key.strip(), settings.ADMIN_API_KEY.strip()):
        is_authorized = True
    elif authorization and authorization.startswith("Bearer "):
        token = authorization.split("Bearer ", 1)[1]
        try:
            from app.core.security import decode_token
            payload = decode_token(token)
            if payload and payload.get("role") == "admin":
                is_authorized = True
        except Exception:
            pass

    if not is_authorized:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Administrative maintenance access required to verify database schema"
        )

    try:
        await init_db_and_seed()
        app.state.db_healthy = True
        app.state.db_error = None
        return {"status": "success", "message": "Database schema verified successfully"}
    except Exception as exc:
        app.state.db_healthy = False
        app.state.db_error = str(exc)
        logger.error("Manual seed-database error: %s", exc, exc_info=True)
        return {"status": "error", "message": "Database verification encountered an internal error"}
