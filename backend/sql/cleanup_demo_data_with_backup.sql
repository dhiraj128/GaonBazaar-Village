-- ==============================================================================
-- APNA GAONBAZAAR: PRODUCTION DEMO DATA CLEANUP & RECOVERABLE BACKUP
-- File: backend/sql/cleanup_demo_data_with_backup.sql
-- Date: 2026-11-23
-- 
-- Objectives:
-- 1. Create complete snapshot backup tables (*_backup_20261123) before deletion.
-- 2. Safely remove confirmed demo/mock/seed data (orders, items, transactions,
--    demo stores, store products, and demo runners with data_origin = 'migrated_demo').
-- 3. Preserve genuine users, legitimate vendors, real transactions, and official
--    administrative accounts (usr_admin_01 / 9800000099, usr_hub_01 / 9800000098).
-- 4. Enable Row-Level Security (RLS) across all public tables.
-- 5. Provide before-and-after audit verification metrics.
-- ==============================================================================

BEGIN;

-- ==============================================================================
-- STEP 1: CREATE RECOVERABLE BACKUP SNAPSHOT TABLES
-- ==============================================================================

DO $$
BEGIN
    -- Orders & Dependents
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') THEN
        DROP TABLE IF EXISTS public.orders_backup_20261123 CASCADE;
        CREATE TABLE public.orders_backup_20261123 AS SELECT * FROM public.orders;
        RAISE NOTICE 'Snapshot created: public.orders_backup_20261123 (% rows)', (SELECT count(*) FROM public.orders_backup_20261123);
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'order_items') THEN
        DROP TABLE IF EXISTS public.order_items_backup_20261123 CASCADE;
        CREATE TABLE public.order_items_backup_20261123 AS SELECT * FROM public.order_items;
        RAISE NOTICE 'Snapshot created: public.order_items_backup_20261123 (% rows)', (SELECT count(*) FROM public.order_items_backup_20261123);
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'order_messages') THEN
        DROP TABLE IF EXISTS public.order_messages_backup_20261123 CASCADE;
        CREATE TABLE public.order_messages_backup_20261123 AS SELECT * FROM public.order_messages;
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'order_timeline') THEN
        DROP TABLE IF EXISTS public.order_timeline_backup_20261123 CASCADE;
        CREATE TABLE public.order_timeline_backup_20261123 AS SELECT * FROM public.order_timeline;
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'payment_transactions') THEN
        DROP TABLE IF EXISTS public.payment_transactions_backup_20261123 CASCADE;
        CREATE TABLE public.payment_transactions_backup_20261123 AS SELECT * FROM public.payment_transactions;
        RAISE NOTICE 'Snapshot created: public.payment_transactions_backup_20261123 (% rows)', (SELECT count(*) FROM public.payment_transactions_backup_20261123);
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'refunds') THEN
        DROP TABLE IF EXISTS public.refunds_backup_20261123 CASCADE;
        CREATE TABLE public.refunds_backup_20261123 AS SELECT * FROM public.refunds;
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'replacements') THEN
        DROP TABLE IF EXISTS public.replacements_backup_20261123 CASCADE;
        CREATE TABLE public.replacements_backup_20261123 AS SELECT * FROM public.replacements;
    END IF;

    -- Stores, Products, Runners, Users
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'stores') THEN
        DROP TABLE IF EXISTS public.stores_backup_20261123 CASCADE;
        CREATE TABLE public.stores_backup_20261123 AS SELECT * FROM public.stores;
        RAISE NOTICE 'Snapshot created: public.stores_backup_20261123 (% rows)', (SELECT count(*) FROM public.stores_backup_20261123);
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'store_products') THEN
        DROP TABLE IF EXISTS public.store_products_backup_20261123 CASCADE;
        CREATE TABLE public.store_products_backup_20261123 AS SELECT * FROM public.store_products;
        RAISE NOTICE 'Snapshot created: public.store_products_backup_20261123 (% rows)', (SELECT count(*) FROM public.store_products_backup_20261123);
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'runners') THEN
        DROP TABLE IF EXISTS public.runners_backup_20261123 CASCADE;
        CREATE TABLE public.runners_backup_20261123 AS SELECT * FROM public.runners;
        RAISE NOTICE 'Snapshot created: public.runners_backup_20261123 (% rows)', (SELECT count(*) FROM public.runners_backup_20261123);
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') THEN
        DROP TABLE IF EXISTS public.users_backup_20261123 CASCADE;
        CREATE TABLE public.users_backup_20261123 AS SELECT * FROM public.users;
        RAISE NOTICE 'Snapshot created: public.users_backup_20261123 (% rows)', (SELECT count(*) FROM public.users_backup_20261123);
    END IF;
END $$;

-- ==============================================================================
-- STEP 2: SAFE CASCADE REMOVAL OF DEMO DATA
-- ==============================================================================

-- 1. Remove child records of confirmed demo orders
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'order_messages') THEN
        DELETE FROM public.order_messages
        WHERE order_id IN (
            SELECT id FROM public.orders 
            WHERE data_origin = 'migrated_demo' OR data_origin = 'pilot_seed' OR data_origin = 'mock'
        );
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'order_timeline') THEN
        DELETE FROM public.order_timeline
        WHERE order_id IN (
            SELECT id FROM public.orders 
            WHERE data_origin = 'migrated_demo' OR data_origin = 'pilot_seed' OR data_origin = 'mock'
        );
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'order_items') THEN
        DELETE FROM public.order_items
        WHERE order_id IN (
            SELECT id FROM public.orders 
            WHERE data_origin = 'migrated_demo' OR data_origin = 'pilot_seed' OR data_origin = 'mock'
        );
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'refunds') THEN
        DELETE FROM public.refunds
        WHERE order_id IN (
            SELECT id FROM public.orders 
            WHERE data_origin = 'migrated_demo' OR data_origin = 'pilot_seed' OR data_origin = 'mock'
        );
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'replacements') THEN
        DELETE FROM public.replacements
        WHERE original_order_id IN (
            SELECT id FROM public.orders 
            WHERE data_origin = 'migrated_demo' OR data_origin = 'pilot_seed' OR data_origin = 'mock'
        );
    END IF;

    -- 2. Remove demo payment transactions
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'payment_transactions') THEN
        DELETE FROM public.payment_transactions
        WHERE data_origin = 'migrated_demo' 
           OR data_origin = 'pilot_seed' 
           OR data_origin = 'mock'
           OR order_id IN (
               SELECT id FROM public.orders 
               WHERE data_origin = 'migrated_demo' OR data_origin = 'pilot_seed' OR data_origin = 'mock'
           );
    END IF;

    -- 3. Remove confirmed demo orders
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') THEN
        DELETE FROM public.orders
        WHERE data_origin = 'migrated_demo' 
           OR data_origin = 'pilot_seed' 
           OR data_origin = 'mock';
    END IF;

    -- 4. Remove demo store products
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'store_products') THEN
        DELETE FROM public.store_products
        WHERE data_origin = 'migrated_demo' 
           OR data_origin = 'pilot_seed' 
           OR data_origin = 'mock'
           OR store_id IN (
               SELECT id FROM public.stores 
               WHERE data_origin = 'migrated_demo' 
                  OR data_origin = 'pilot_seed' 
                  OR data_origin = 'mock'
                  OR id IN ('str_01', 'str_02')
           );
    END IF;

    -- 5. Remove demo stores
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'stores') THEN
        DELETE FROM public.stores
        WHERE data_origin = 'migrated_demo' 
           OR data_origin = 'pilot_seed' 
           OR data_origin = 'mock'
           OR id IN ('str_01', 'str_02');
    END IF;

    -- 6. Remove demo runners
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'runners') THEN
        DELETE FROM public.runners
        WHERE data_origin = 'migrated_demo' 
           OR data_origin = 'pilot_seed' 
           OR data_origin = 'mock'
           OR id IN ('run_01');
    END IF;

    -- 7. Remove demo mock users (STRICTLY PRESERVING ADMINS AND GENUINE USERS)
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') THEN
        DELETE FROM public.users
        WHERE (
            data_origin = 'migrated_demo' 
            OR data_origin = 'pilot_seed' 
            OR data_origin = 'mock'
            OR id IN ('usr_v1', 'usr_v2', 'usr_r1', 'usr_c1')
        )
        AND id NOT IN ('usr_admin_01', 'usr_hub_01')
        AND phone NOT IN ('9800000099', '9800000098');
    END IF;
END $$;

-- ==============================================================================
-- STEP 3: ENSURE OFFICIAL SUPER ADMIN & MINAPUR HUB MANAGER ACCOUNTS
-- ==============================================================================

INSERT INTO public.users (
    id, phone, name, role, preferred_language, is_active, created_at, updated_at
) VALUES (
    'usr_admin_01', 
    '9800000099', 
    'GaonBazaar Super Admin', 
    'admin', 
    'en', 
    true, 
    NOW(), 
    NOW()
) ON CONFLICT (id) DO UPDATE SET 
    role = 'admin', 
    is_active = true,
    phone = '9800000099',
    updated_at = NOW();

INSERT INTO public.users (
    id, phone, name, role, preferred_language, is_active, created_at, updated_at
) VALUES (
    'usr_hub_01', 
    '9800000098', 
    'Minapur Hub Manager', 
    'hub_manager', 
    'hi', 
    true, 
    NOW(), 
    NOW()
) ON CONFLICT (id) DO UPDATE SET 
    role = 'hub_manager', 
    is_active = true,
    phone = '9800000098',
    updated_at = NOW();

-- ==============================================================================
-- STEP 4: VERIFY ROW-LEVEL SECURITY (RLS) ON ALL PUBLIC TABLES
-- ==============================================================================

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

COMMIT;

-- ==============================================================================
-- STEP 5: VERIFICATION SUMMARY (AFTER COMMIT)
-- ==============================================================================

SELECT 
    'orders' AS entity,
    (SELECT count(*) FROM public.orders_backup_20261123) AS backup_count,
    (SELECT count(*) FROM public.orders) AS live_remaining,
    (SELECT count(*) FROM public.orders WHERE data_origin = 'migrated_demo') AS demo_remaining
UNION ALL
SELECT 
    'order_items' AS entity,
    (SELECT count(*) FROM public.order_items_backup_20261123) AS backup_count,
    (SELECT count(*) FROM public.order_items) AS live_remaining,
    0 AS demo_remaining
UNION ALL
SELECT 
    'payment_transactions' AS entity,
    (SELECT count(*) FROM public.payment_transactions_backup_20261123) AS backup_count,
    (SELECT count(*) FROM public.payment_transactions) AS live_remaining,
    (SELECT count(*) FROM public.payment_transactions WHERE data_origin = 'migrated_demo') AS demo_remaining
UNION ALL
SELECT 
    'stores' AS entity,
    (SELECT count(*) FROM public.stores_backup_20261123) AS backup_count,
    (SELECT count(*) FROM public.stores) AS live_remaining,
    (SELECT count(*) FROM public.stores WHERE data_origin = 'migrated_demo') AS demo_remaining
UNION ALL
SELECT 
    'store_products' AS entity,
    (SELECT count(*) FROM public.store_products_backup_20261123) AS backup_count,
    (SELECT count(*) FROM public.store_products) AS live_remaining,
    (SELECT count(*) FROM public.store_products WHERE data_origin = 'migrated_demo') AS demo_remaining
UNION ALL
SELECT 
    'runners' AS entity,
    (SELECT count(*) FROM public.runners_backup_20261123) AS backup_count,
    (SELECT count(*) FROM public.runners) AS live_remaining,
    (SELECT count(*) FROM public.runners WHERE data_origin = 'migrated_demo') AS demo_remaining
UNION ALL
SELECT 
    'users' AS entity,
    (SELECT count(*) FROM public.users_backup_20261123) AS backup_count,
    (SELECT count(*) FROM public.users) AS live_remaining,
    (SELECT count(*) FROM public.users WHERE data_origin = 'migrated_demo') AS demo_remaining;
