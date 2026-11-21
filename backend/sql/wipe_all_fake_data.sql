-- =====================================================================
-- Apna GaonBazaar - Clean Slate Database Wipe Script
-- Purges all mock, fake, test, and auto-seeded business records while strictly
-- preserving Super Admin (9800000099), Hub Manager (9800000098),
-- table structures, constraints, and Row Level Security (RLS) policies.
-- =====================================================================

BEGIN;

-- 1. Truncate all business transactional and child tables
TRUNCATE TABLE
  ticket_messages,
  support_tickets,
  order_timeline,
  order_messages,
  refunds,
  replacements,
  order_items,
  orders,
  store_products,
  stores,
  runners,
  addresses,
  notifications,
  monthly_ration_items,
  monthly_ration_lists,
  payout_accounts,
  otp_challenges,
  audit_logs,
  global_catalog
RESTART IDENTITY CASCADE;

-- 2. Delete pilot / test users while strictly keeping Super Admin and Hub Manager
DELETE FROM users
WHERE phone NOT IN ('9800000099', '9800000098')
  AND id NOT IN ('usr_admin_01', 'usr_hub_01');

-- 3. Ensure Super Admin account is permanently present and active
INSERT INTO users (id, phone, name, role, is_active, preferred_language, created_at, updated_at)
VALUES (
  'usr_admin_01',
  '9800000099',
  'Super Admin',
  'admin',
  TRUE,
  'en',
  NOW(),
  NOW()
)
ON CONFLICT (phone) DO UPDATE
SET role = 'admin',
    is_active = TRUE;

COMMIT;

-- =====================================================================
-- Verification Audit Query
-- =====================================================================
SELECT 'orders' AS table_name, count(*) AS count FROM orders
UNION ALL
SELECT 'stores', count(*) FROM stores
UNION ALL
SELECT 'store_products', count(*) FROM store_products
UNION ALL
SELECT 'runners', count(*) FROM runners
UNION ALL
SELECT 'global_catalog', count(*) FROM global_catalog
UNION ALL
SELECT 'users (non-admin)', count(*) FROM users WHERE role != 'admin'
UNION ALL
SELECT 'super_admins', count(*) FROM users WHERE role = 'admin';
