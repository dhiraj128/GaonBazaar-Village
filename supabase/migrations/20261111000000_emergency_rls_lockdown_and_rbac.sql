-- ==============================================================================
-- GAONBAZAAR EMERGENCY ROW LEVEL SECURITY (RLS) LOCKDOWN & STRICT RBAC POLICIES
-- Target Schema: public
-- Tables Protected: 19 tables (all tables in public schema)
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- 1. Helper Function: Super Admin Verification (SECURITY DEFINER)
-- ------------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION public.is_super_admin()
RETURNS boolean
LANGUAGE sql
STABLE
SET search_path = public
AS $$
  SELECT COALESCE(
    (auth.jwt() ->> 'role') IN ('super_admin', 'SUPER_ADMIN', 'service_role')
    OR (auth.jwt() -> 'app_metadata' ->> 'role') IN ('super_admin', 'SUPER_ADMIN')
    OR (auth.jwt() -> 'user_metadata' ->> 'role') IN ('super_admin', 'SUPER_ADMIN')
    OR (auth.jwt() ->> 'email') = 'admin@gaonbazaar.in'
    OR (auth.jwt() ->> 'email') LIKE '%admin%@gaonbazaar.in',
    false
  );
$$;

-- ------------------------------------------------------------------------------
-- 2. Enable Row-Level Security Globally Across All 19 Public Tables
-- ------------------------------------------------------------------------------
ALTER TABLE IF EXISTS "public"."users" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."addresses" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."stores" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."runners" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."global_catalog" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."store_products" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."orders" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."order_items" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."order_timeline" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."support_tickets" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."audit_logs" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."notifications" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."refunds" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."replacements" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."otp_challenges" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."order_messages" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."ticket_messages" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."monthly_ration_lists" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."monthly_ration_items" ENABLE ROW LEVEL SECURITY;

-- ------------------------------------------------------------------------------
-- 3. Clean Up Legacy / Overly Permissive Policies
-- ------------------------------------------------------------------------------
DO $$
DECLARE
  pol record;
BEGIN
  FOR pol IN 
    SELECT policyname, tablename 
    FROM pg_policies 
    WHERE schemaname = 'public'
  LOOP
    EXECUTE format('DROP POLICY IF EXISTS %I ON public.%I;', pol.policyname, pol.tablename);
  END LOOP;
END $$;

-- ------------------------------------------------------------------------------
-- 4. Service Role Universal Bypass (Durable backend worker access)
-- ------------------------------------------------------------------------------
CREATE POLICY "service_role_users_all" ON public.users FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_addresses_all" ON public.addresses FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_stores_all" ON public.stores FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_runners_all" ON public.runners FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_global_catalog_all" ON public.global_catalog FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_store_products_all" ON public.store_products FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_orders_all" ON public.orders FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_order_items_all" ON public.order_items FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_order_timeline_all" ON public.order_timeline FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_support_tickets_all" ON public.support_tickets FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_audit_logs_all" ON public.audit_logs FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_notifications_all" ON public.notifications FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_refunds_all" ON public.refunds FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_replacements_all" ON public.replacements FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_otp_challenges_all" ON public.otp_challenges FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_order_messages_all" ON public.order_messages FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_ticket_messages_all" ON public.ticket_messages FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_monthly_ration_lists_all" ON public.monthly_ration_lists FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_monthly_ration_items_all" ON public.monthly_ration_items FOR ALL TO service_role USING (true) WITH CHECK (true);

-- ------------------------------------------------------------------------------
-- 5. Super Admin Full God-Mode Bypass (authenticated)
-- ------------------------------------------------------------------------------
CREATE POLICY "admin_users_all" ON public.users FOR ALL TO authenticated
  USING (
    (auth.jwt() ->> 'role') IN ('super_admin', 'SUPER_ADMIN', 'service_role')
    OR (auth.jwt() -> 'app_metadata' ->> 'role') IN ('super_admin', 'SUPER_ADMIN')
    OR (auth.jwt() -> 'user_metadata' ->> 'role') IN ('super_admin', 'SUPER_ADMIN')
    OR (auth.jwt() ->> 'email') = 'admin@gaonbazaar.in'
  )
  WITH CHECK (
    (auth.jwt() ->> 'role') IN ('super_admin', 'SUPER_ADMIN', 'service_role')
    OR (auth.jwt() -> 'app_metadata' ->> 'role') IN ('super_admin', 'SUPER_ADMIN')
    OR (auth.jwt() -> 'user_metadata' ->> 'role') IN ('super_admin', 'SUPER_ADMIN')
    OR (auth.jwt() ->> 'email') = 'admin@gaonbazaar.in'
  );

CREATE POLICY "admin_addresses_all" ON public.addresses FOR ALL TO authenticated USING (public.is_super_admin()) WITH CHECK (public.is_super_admin());
CREATE POLICY "admin_stores_all" ON public.stores FOR ALL TO authenticated USING (public.is_super_admin()) WITH CHECK (public.is_super_admin());
CREATE POLICY "admin_runners_all" ON public.runners FOR ALL TO authenticated USING (public.is_super_admin()) WITH CHECK (public.is_super_admin());
CREATE POLICY "admin_global_catalog_all" ON public.global_catalog FOR ALL TO authenticated USING (public.is_super_admin()) WITH CHECK (public.is_super_admin());
CREATE POLICY "admin_store_products_all" ON public.store_products FOR ALL TO authenticated USING (public.is_super_admin()) WITH CHECK (public.is_super_admin());
CREATE POLICY "admin_orders_all" ON public.orders FOR ALL TO authenticated USING (public.is_super_admin()) WITH CHECK (public.is_super_admin());
CREATE POLICY "admin_order_items_all" ON public.order_items FOR ALL TO authenticated USING (public.is_super_admin()) WITH CHECK (public.is_super_admin());
CREATE POLICY "admin_order_timeline_all" ON public.order_timeline FOR ALL TO authenticated USING (public.is_super_admin()) WITH CHECK (public.is_super_admin());
CREATE POLICY "admin_support_tickets_all" ON public.support_tickets FOR ALL TO authenticated USING (public.is_super_admin()) WITH CHECK (public.is_super_admin());
CREATE POLICY "admin_audit_logs_all" ON public.audit_logs FOR ALL TO authenticated USING (public.is_super_admin()) WITH CHECK (public.is_super_admin());
CREATE POLICY "admin_notifications_all" ON public.notifications FOR ALL TO authenticated USING (public.is_super_admin()) WITH CHECK (public.is_super_admin());
CREATE POLICY "admin_refunds_all" ON public.refunds FOR ALL TO authenticated USING (public.is_super_admin()) WITH CHECK (public.is_super_admin());
CREATE POLICY "admin_replacements_all" ON public.replacements FOR ALL TO authenticated USING (public.is_super_admin()) WITH CHECK (public.is_super_admin());
CREATE POLICY "admin_order_messages_all" ON public.order_messages FOR ALL TO authenticated USING (public.is_super_admin()) WITH CHECK (public.is_super_admin());
CREATE POLICY "admin_ticket_messages_all" ON public.ticket_messages FOR ALL TO authenticated USING (public.is_super_admin()) WITH CHECK (public.is_super_admin());
CREATE POLICY "admin_monthly_ration_lists_all" ON public.monthly_ration_lists FOR ALL TO authenticated USING (public.is_super_admin()) WITH CHECK (public.is_super_admin());
CREATE POLICY "admin_monthly_ration_items_all" ON public.monthly_ration_items FOR ALL TO authenticated USING (public.is_super_admin()) WITH CHECK (public.is_super_admin());

-- ------------------------------------------------------------------------------
-- 6. Public Catalogs & Stores (Browsing)
-- ------------------------------------------------------------------------------
CREATE POLICY "global_catalog_public_read" ON public.global_catalog
  FOR SELECT TO anon, authenticated
  USING (true);

CREATE POLICY "store_products_public_read" ON public.store_products
  FOR SELECT TO anon, authenticated
  USING (in_stock = true);

CREATE POLICY "stores_public_read" ON public.stores
  FOR SELECT TO anon, authenticated
  USING (is_online = true AND is_approved = true);

CREATE POLICY "runners_public_read" ON public.runners
  FOR SELECT TO anon, authenticated
  USING (is_online = true AND is_approved = true);

-- ------------------------------------------------------------------------------
-- 7. User & Identity Strict Isolation (Zero IDOR)
-- ------------------------------------------------------------------------------
CREATE POLICY "users_owner_select" ON public.users
  FOR SELECT TO authenticated
  USING (id = auth.uid()::text OR firebase_uid = auth.uid()::text);

CREATE POLICY "users_owner_insert" ON public.users
  FOR INSERT TO authenticated
  WITH CHECK (id = auth.uid()::text OR firebase_uid = auth.uid()::text);

CREATE POLICY "users_owner_update" ON public.users
  FOR UPDATE TO authenticated
  USING (id = auth.uid()::text OR firebase_uid = auth.uid()::text)
  WITH CHECK (id = auth.uid()::text OR firebase_uid = auth.uid()::text);

CREATE POLICY "users_block_anon" ON public.users
  FOR ALL TO anon USING (false) WITH CHECK (false);

-- ------------------------------------------------------------------------------
-- 8. Customer Addresses & Geo Privacy
-- ------------------------------------------------------------------------------
CREATE POLICY "addresses_owner_all" ON public.addresses
  FOR ALL TO authenticated
  USING (
    user_id = auth.uid()::text 
    OR user_id IN (SELECT u.id FROM public.users u WHERE u.firebase_uid = auth.uid()::text)
  )
  WITH CHECK (
    user_id = auth.uid()::text 
    OR user_id IN (SELECT u.id FROM public.users u WHERE u.firebase_uid = auth.uid()::text)
  );

CREATE POLICY "addresses_block_anon" ON public.addresses
  FOR ALL TO anon USING (false) WITH CHECK (false);

-- ------------------------------------------------------------------------------
-- 9. Vendor Store Management & Product Catalog Ownership
-- ------------------------------------------------------------------------------
CREATE POLICY "stores_owner_all" ON public.stores
  FOR ALL TO authenticated
  USING (
    owner_id = auth.uid()::text 
    OR owner_id IN (SELECT u.id FROM public.users u WHERE u.firebase_uid = auth.uid()::text)
  )
  WITH CHECK (
    owner_id = auth.uid()::text 
    OR owner_id IN (SELECT u.id FROM public.users u WHERE u.firebase_uid = auth.uid()::text)
  );

CREATE POLICY "store_products_owner_all" ON public.store_products
  FOR ALL TO authenticated
  USING (
    store_id IN (
      SELECT s.id FROM public.stores s 
      WHERE s.owner_id = auth.uid()::text 
      OR s.owner_id IN (SELECT u.id FROM public.users u WHERE u.firebase_uid = auth.uid()::text)
    )
  )
  WITH CHECK (
    store_id IN (
      SELECT s.id FROM public.stores s 
      WHERE s.owner_id = auth.uid()::text 
      OR s.owner_id IN (SELECT u.id FROM public.users u WHERE u.firebase_uid = auth.uid()::text)
    )
  );

-- ------------------------------------------------------------------------------
-- 10. Runner Profile & Fleet Management
-- ------------------------------------------------------------------------------
CREATE POLICY "runners_owner_all" ON public.runners
  FOR ALL TO authenticated
  USING (
    user_id = auth.uid()::text 
    OR user_id IN (SELECT u.id FROM public.users u WHERE u.firebase_uid = auth.uid()::text)
  )
  WITH CHECK (
    user_id = auth.uid()::text 
    OR user_id IN (SELECT u.id FROM public.users u WHERE u.firebase_uid = auth.uid()::text)
  );

-- ------------------------------------------------------------------------------
-- 11. Orders & Delivery Lifecycle Isolation (Role-Based RBAC)
-- ------------------------------------------------------------------------------
-- Customers: SELECT, INSERT, UPDATE own orders
CREATE POLICY "orders_customer_select" ON public.orders
  FOR SELECT TO authenticated
  USING (
    customer_id = auth.uid()::text 
    OR customer_id IN (SELECT u.id FROM public.users u WHERE u.firebase_uid = auth.uid()::text)
  );

CREATE POLICY "orders_customer_insert" ON public.orders
  FOR INSERT TO authenticated
  WITH CHECK (
    customer_id = auth.uid()::text 
    OR customer_id IN (SELECT u.id FROM public.users u WHERE u.firebase_uid = auth.uid()::text)
  );

CREATE POLICY "orders_customer_update" ON public.orders
  FOR UPDATE TO authenticated
  USING (
    customer_id = auth.uid()::text 
    OR customer_id IN (SELECT u.id FROM public.users u WHERE u.firebase_uid = auth.uid()::text)
  )
  WITH CHECK (
    customer_id = auth.uid()::text 
    OR customer_id IN (SELECT u.id FROM public.users u WHERE u.firebase_uid = auth.uid()::text)
  );

-- Vendors: SELECT, UPDATE orders for their store
CREATE POLICY "orders_vendor_select" ON public.orders
  FOR SELECT TO authenticated
  USING (
    store_id IN (
      SELECT s.id FROM public.stores s 
      WHERE s.owner_id = auth.uid()::text 
      OR s.owner_id IN (SELECT u.id FROM public.users u WHERE u.firebase_uid = auth.uid()::text)
    )
    OR vendor_id = auth.uid()::text
  );

CREATE POLICY "orders_vendor_update" ON public.orders
  FOR UPDATE TO authenticated
  USING (
    store_id IN (
      SELECT s.id FROM public.stores s 
      WHERE s.owner_id = auth.uid()::text 
      OR s.owner_id IN (SELECT u.id FROM public.users u WHERE u.firebase_uid = auth.uid()::text)
    )
    OR vendor_id = auth.uid()::text
  );

-- Runners: SELECT, UPDATE delivery tasks assigned to them or available for claim
CREATE POLICY "orders_runner_select" ON public.orders
  FOR SELECT TO authenticated
  USING (
    runner_id = auth.uid()::text
    OR runner_id IN (
      SELECT r.id FROM public.runners r 
      WHERE r.user_id = auth.uid()::text 
      OR r.user_id IN (SELECT u.id FROM public.users u WHERE u.firebase_uid = auth.uid()::text)
    )
    OR (runner_id IS NULL AND status IN ('READY_FOR_PICKUP', 'PACKED'))
  );

CREATE POLICY "orders_runner_update" ON public.orders
  FOR UPDATE TO authenticated
  USING (
    runner_id = auth.uid()::text
    OR runner_id IN (
      SELECT r.id FROM public.runners r 
      WHERE r.user_id = auth.uid()::text 
      OR r.user_id IN (SELECT u.id FROM public.users u WHERE u.firebase_uid = auth.uid()::text)
    )
    OR (runner_id IS NULL AND status IN ('READY_FOR_PICKUP', 'PACKED'))
  );

CREATE POLICY "orders_block_anon" ON public.orders
  FOR ALL TO anon USING (false) WITH CHECK (false);

-- ------------------------------------------------------------------------------
-- 12. Order Items & Timeline Isolation
-- ------------------------------------------------------------------------------
CREATE POLICY "order_items_participant_select" ON public.order_items
  FOR SELECT TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM public.orders o
      WHERE o.id = order_items.order_id
      AND (
        o.customer_id = auth.uid()::text
        OR o.customer_id IN (SELECT u.id FROM public.users u WHERE u.firebase_uid = auth.uid()::text)
        OR o.runner_id = auth.uid()::text
        OR o.runner_id IN (SELECT r.id FROM public.runners r WHERE r.user_id = auth.uid()::text OR r.user_id IN (SELECT u.id FROM public.users u WHERE u.firebase_uid = auth.uid()::text))
        OR o.store_id IN (SELECT s.id FROM public.stores s WHERE s.owner_id = auth.uid()::text OR s.owner_id IN (SELECT u.id FROM public.users u WHERE u.firebase_uid = auth.uid()::text))
        OR o.vendor_id = auth.uid()::text
      )
    )
  );

CREATE POLICY "order_items_customer_insert" ON public.order_items
  FOR INSERT TO authenticated
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM public.orders o
      WHERE o.id = order_items.order_id
      AND (o.customer_id = auth.uid()::text OR o.customer_id IN (SELECT u.id FROM public.users u WHERE u.firebase_uid = auth.uid()::text))
    )
  );

CREATE POLICY "order_items_block_anon" ON public.order_items
  FOR ALL TO anon USING (false) WITH CHECK (false);

CREATE POLICY "order_timeline_participant_select" ON public.order_timeline
  FOR SELECT TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM public.orders o
      WHERE o.id = order_timeline.order_id
      AND (
        o.customer_id = auth.uid()::text
        OR o.customer_id IN (SELECT u.id FROM public.users u WHERE u.firebase_uid = auth.uid()::text)
        OR o.runner_id = auth.uid()::text
        OR o.runner_id IN (SELECT r.id FROM public.runners r WHERE r.user_id = auth.uid()::text OR r.user_id IN (SELECT u.id FROM public.users u WHERE u.firebase_uid = auth.uid()::text))
        OR o.store_id IN (SELECT s.id FROM public.stores s WHERE s.owner_id = auth.uid()::text OR s.owner_id IN (SELECT u.id FROM public.users u WHERE u.firebase_uid = auth.uid()::text))
        OR o.vendor_id = auth.uid()::text
      )
    )
  );

CREATE POLICY "order_timeline_block_anon" ON public.order_timeline
  FOR ALL TO anon USING (false) WITH CHECK (false);

-- ------------------------------------------------------------------------------
-- 13. Order Messages & Customer Support Chat
-- ------------------------------------------------------------------------------
CREATE POLICY "order_messages_participant_all" ON public.order_messages
  FOR ALL TO authenticated
  USING (
    sender_id = auth.uid()::text
    OR EXISTS (
      SELECT 1 FROM public.orders o
      WHERE o.id = order_messages.order_id
      AND (
        o.customer_id = auth.uid()::text
        OR o.customer_id IN (SELECT u.id FROM public.users u WHERE u.firebase_uid = auth.uid()::text)
        OR o.runner_id = auth.uid()::text
        OR o.runner_id IN (SELECT r.id FROM public.runners r WHERE r.user_id = auth.uid()::text OR r.user_id IN (SELECT u.id FROM public.users u WHERE u.firebase_uid = auth.uid()::text))
        OR o.store_id IN (SELECT s.id FROM public.stores s WHERE s.owner_id = auth.uid()::text OR s.owner_id IN (SELECT u.id FROM public.users u WHERE u.firebase_uid = auth.uid()::text))
        OR o.vendor_id = auth.uid()::text
      )
    )
  )
  WITH CHECK (
    sender_id = auth.uid()::text
    OR EXISTS (
      SELECT 1 FROM public.orders o
      WHERE o.id = order_messages.order_id
      AND (
        o.customer_id = auth.uid()::text
        OR o.customer_id IN (SELECT u.id FROM public.users u WHERE u.firebase_uid = auth.uid()::text)
        OR o.runner_id = auth.uid()::text
        OR o.runner_id IN (SELECT r.id FROM public.runners r WHERE r.user_id = auth.uid()::text OR r.user_id IN (SELECT u.id FROM public.users u WHERE u.firebase_uid = auth.uid()::text))
        OR o.store_id IN (SELECT s.id FROM public.stores s WHERE s.owner_id = auth.uid()::text OR s.owner_id IN (SELECT u.id FROM public.users u WHERE u.firebase_uid = auth.uid()::text))
        OR o.vendor_id = auth.uid()::text
      )
    )
  );

CREATE POLICY "order_messages_block_anon" ON public.order_messages
  FOR ALL TO anon USING (false) WITH CHECK (false);

-- ------------------------------------------------------------------------------
-- 14. Support Tickets & Ticket Messages
-- ------------------------------------------------------------------------------
CREATE POLICY "support_tickets_owner_all" ON public.support_tickets
  FOR ALL TO authenticated
  USING (
    user_id = auth.uid()::text 
    OR user_id IN (SELECT u.id FROM public.users u WHERE u.firebase_uid = auth.uid()::text)
  )
  WITH CHECK (
    user_id = auth.uid()::text 
    OR user_id IN (SELECT u.id FROM public.users u WHERE u.firebase_uid = auth.uid()::text)
  );

CREATE POLICY "support_tickets_block_anon" ON public.support_tickets
  FOR ALL TO anon USING (false) WITH CHECK (false);

CREATE POLICY "ticket_messages_participant_all" ON public.ticket_messages
  FOR ALL TO authenticated
  USING (
    sender_id = auth.uid()::text
    OR EXISTS (
      SELECT 1 FROM public.support_tickets t
      WHERE t.id = ticket_messages.ticket_id
      AND (
        t.user_id = auth.uid()::text 
        OR t.user_id IN (SELECT u.id FROM public.users u WHERE u.firebase_uid = auth.uid()::text)
      )
    )
  )
  WITH CHECK (
    sender_id = auth.uid()::text
    OR EXISTS (
      SELECT 1 FROM public.support_tickets t
      WHERE t.id = ticket_messages.ticket_id
      AND (
        t.user_id = auth.uid()::text 
        OR t.user_id IN (SELECT u.id FROM public.users u WHERE u.firebase_uid = auth.uid()::text)
      )
    )
  );

CREATE POLICY "ticket_messages_block_anon" ON public.ticket_messages
  FOR ALL TO anon USING (false) WITH CHECK (false);

-- ------------------------------------------------------------------------------
-- 15. User Notifications
-- ------------------------------------------------------------------------------
CREATE POLICY "notifications_owner_all" ON public.notifications
  FOR ALL TO authenticated
  USING (
    user_id = auth.uid()::text 
    OR user_id IN (SELECT u.id FROM public.users u WHERE u.firebase_uid = auth.uid()::text)
  )
  WITH CHECK (
    user_id = auth.uid()::text 
    OR user_id IN (SELECT u.id FROM public.users u WHERE u.firebase_uid = auth.uid()::text)
  );

CREATE POLICY "notifications_block_anon" ON public.notifications
  FOR ALL TO anon USING (false) WITH CHECK (false);

-- ------------------------------------------------------------------------------
-- 16. Monthly Ration Lists & Items
-- ------------------------------------------------------------------------------
CREATE POLICY "monthly_ration_lists_owner_all" ON public.monthly_ration_lists
  FOR ALL TO authenticated
  USING (
    user_id = auth.uid()::text 
    OR user_id IN (SELECT u.id FROM public.users u WHERE u.firebase_uid = auth.uid()::text)
  )
  WITH CHECK (
    user_id = auth.uid()::text 
    OR user_id IN (SELECT u.id FROM public.users u WHERE u.firebase_uid = auth.uid()::text)
  );

CREATE POLICY "monthly_ration_lists_block_anon" ON public.monthly_ration_lists
  FOR ALL TO anon USING (false) WITH CHECK (false);

CREATE POLICY "monthly_ration_items_owner_all" ON public.monthly_ration_items
  FOR ALL TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM public.monthly_ration_lists l
      WHERE l.id = monthly_ration_items.list_id
      AND (
        l.user_id = auth.uid()::text 
        OR l.user_id IN (SELECT u.id FROM public.users u WHERE u.firebase_uid = auth.uid()::text)
      )
    )
  )
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM public.monthly_ration_lists l
      WHERE l.id = monthly_ration_items.list_id
      AND (
        l.user_id = auth.uid()::text 
        OR l.user_id IN (SELECT u.id FROM public.users u WHERE u.firebase_uid = auth.uid()::text)
      )
    )
  );

CREATE POLICY "monthly_ration_items_block_anon" ON public.monthly_ration_items
  FOR ALL TO anon USING (false) WITH CHECK (false);

-- ------------------------------------------------------------------------------
-- 17. Refunds & Replacements
-- ------------------------------------------------------------------------------
CREATE POLICY "refunds_participant_select" ON public.refunds
  FOR SELECT TO authenticated
  USING (
    created_by = auth.uid()::text
    OR EXISTS (
      SELECT 1 FROM public.orders o
      WHERE o.id = refunds.order_id
      AND (
        o.customer_id = auth.uid()::text
        OR o.customer_id IN (SELECT u.id FROM public.users u WHERE u.firebase_uid = auth.uid()::text)
        OR o.store_id IN (
          SELECT s.id FROM public.stores s 
          WHERE s.owner_id = auth.uid()::text 
          OR s.owner_id IN (SELECT u.id FROM public.users u WHERE u.firebase_uid = auth.uid()::text)
        )
      )
    )
  );

CREATE POLICY "refunds_block_anon" ON public.refunds
  FOR ALL TO anon USING (false) WITH CHECK (false);

CREATE POLICY "replacements_participant_all" ON public.replacements
  FOR ALL TO authenticated
  USING (
    customer_id = auth.uid()::text
    OR customer_id IN (SELECT u.id FROM public.users u WHERE u.firebase_uid = auth.uid()::text)
    OR runner_id = auth.uid()::text
    OR runner_id IN (
      SELECT r.id FROM public.runners r 
      WHERE r.user_id = auth.uid()::text 
      OR r.user_id IN (SELECT u.id FROM public.users u WHERE u.firebase_uid = auth.uid()::text)
    )
    OR store_id IN (
      SELECT s.id FROM public.stores s 
      WHERE s.owner_id = auth.uid()::text 
      OR s.owner_id IN (SELECT u.id FROM public.users u WHERE u.firebase_uid = auth.uid()::text)
    )
  )
  WITH CHECK (
    customer_id = auth.uid()::text
    OR customer_id IN (SELECT u.id FROM public.users u WHERE u.firebase_uid = auth.uid()::text)
    OR runner_id = auth.uid()::text
    OR runner_id IN (
      SELECT r.id FROM public.runners r 
      WHERE r.user_id = auth.uid()::text 
      OR r.user_id IN (SELECT u.id FROM public.users u WHERE u.firebase_uid = auth.uid()::text)
    )
    OR store_id IN (
      SELECT s.id FROM public.stores s 
      WHERE s.owner_id = auth.uid()::text 
      OR s.owner_id IN (SELECT u.id FROM public.users u WHERE u.firebase_uid = auth.uid()::text)
    )
  );

CREATE POLICY "replacements_block_anon" ON public.replacements
  FOR ALL TO anon USING (false) WITH CHECK (false);

-- ------------------------------------------------------------------------------
-- 18. High-Security Tables: Complete Client Block (Backend Service Role Only)
-- ------------------------------------------------------------------------------
-- OTP Challenges: Pure backend API access only. Zero anon or authenticated access.
CREATE POLICY "otp_challenges_locked" ON public.otp_challenges
  FOR ALL TO anon, authenticated
  USING (false)
  WITH CHECK (false);

-- Audit Logs: Super Admin only. Block regular users and anon.
CREATE POLICY "audit_logs_block_anon" ON public.audit_logs
  FOR ALL TO anon
  USING (false)
  WITH CHECK (false);

-- ------------------------------------------------------------------------------
-- 19. Performance Indexes for Foreign Keys in RLS Policies
-- ------------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON public.orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_store_id ON public.orders(store_id);
CREATE INDEX IF NOT EXISTS idx_orders_runner_id ON public.orders(runner_id);
CREATE INDEX IF NOT EXISTS idx_stores_owner_id ON public.stores(owner_id);
CREATE INDEX IF NOT EXISTS idx_runners_user_id ON public.runners(user_id);
CREATE INDEX IF NOT EXISTS idx_addresses_user_id ON public.addresses(user_id);
CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON public.order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_timeline_order_id ON public.order_timeline(order_id);
CREATE INDEX IF NOT EXISTS idx_support_tickets_user_id ON public.support_tickets(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON public.notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_monthly_ration_lists_user_id ON public.monthly_ration_lists(user_id);
CREATE INDEX IF NOT EXISTS idx_monthly_ration_items_list_id ON public.monthly_ration_items(list_id);
