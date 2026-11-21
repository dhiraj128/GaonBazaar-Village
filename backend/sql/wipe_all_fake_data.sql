-- ==============================================================================
-- APNA GAONBAZAAR: COMPLETE PURGE OF ALL MOCK, PILOT & DUMMY DATA
-- Safely wipes all business rows, resets sequences, preserves schema & RLS.
-- Retains platform administration accounts (admin, hub_manager).
-- ==============================================================================

BEGIN;

-- 1. Truncate all child business tables and reset sequences
TRUNCATE TABLE 
    public.order_messages,
    public.order_timeline,
    public.order_items,
    public.ticket_messages,
    public.support_tickets,
    public.refunds,
    public.replacements,
    public.orders,
    public.store_products,
    public.global_catalog,
    public.stores,
    public.runners,
    public.addresses,
    public.monthly_ration_items,
    public.monthly_ration_lists,
    public.notifications,
    public.otp_challenges,
    public.payout_accounts,
    public.audit_logs
RESTART IDENTITY CASCADE;

-- 2. Delete non-admin / non-management test users
DELETE FROM public.users 
WHERE role NOT IN ('admin', 'hub_manager');

-- 3. Ensure official Super Admin account exists
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
    phone = '9800000099';

-- 4. Ensure official Minapur Hub Manager account exists
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
    phone = '9800000098';

-- 5. Verify RLS is enabled across all tables
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
