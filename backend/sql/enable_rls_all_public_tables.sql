-- ====================================================================
-- Apna GaonBazaar - Supabase PostgreSQL RLS Auto-Enforcement
-- Idempotent Security Script: Enables RLS on ALL public tables
-- Resolves all Supabase Security Advisor "RLS Disabled in Public" alerts
-- ====================================================================

-- 1. Dynamically iterate over all tables in the public schema and enable RLS
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
        RAISE NOTICE 'Row-Level Security enabled on table: public.%', r.tablename;
    END LOOP;
END $$;

-- 2. Audit Verification Query
-- Expected result: rls_disabled_tables = 0
SELECT 
    count(*) AS total_public_tables,
    sum(CASE WHEN rowsecurity THEN 1 ELSE 0 END) AS rls_enabled_tables,
    sum(CASE WHEN NOT rowsecurity THEN 1 ELSE 0 END) AS rls_disabled_tables
FROM pg_tables 
WHERE schemaname = 'public';
