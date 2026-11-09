-- ==============================================================================
-- GAONBAZAAR SUPABASE ROW LEVEL SECURITY (RLS) & MULTI-USER ISOLATION POLICIES
-- ==============================================================================

-- 1. Enable Row Level Security across all public schema tables
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

-- 2. Public Read Catalogs & Approved Stores
DROP POLICY IF EXISTS "global_catalog_public_read" ON "public"."global_catalog";
CREATE POLICY "global_catalog_public_read" ON "public"."global_catalog"
  FOR SELECT TO anon, authenticated USING (true);

DROP POLICY IF EXISTS "store_products_public_read" ON "public"."store_products";
CREATE POLICY "store_products_public_read" ON "public"."store_products"
  FOR SELECT TO anon, authenticated USING (in_stock = true);

DROP POLICY IF EXISTS "stores_public_read" ON "public"."stores";
CREATE POLICY "stores_public_read" ON "public"."stores"
  FOR SELECT TO anon, authenticated USING (is_online = true AND is_approved = true);

DROP POLICY IF EXISTS "runners_public_read" ON "public"."runners";
CREATE POLICY "runners_public_read" ON "public"."runners"
  FOR SELECT TO anon, authenticated USING (is_online = true AND is_approved = true);

-- 3. Strict User & Identity Isolation (Zero IDOR)
DROP POLICY IF EXISTS "users_owner_access" ON "public"."users";
CREATE POLICY "users_owner_access" ON "public"."users"
  FOR ALL TO authenticated
  USING (auth.uid()::text = id OR auth.uid()::text = firebase_uid);

DROP POLICY IF EXISTS "users_block_anon" ON "public"."users";
CREATE POLICY "users_block_anon" ON "public"."users"
  FOR ALL TO anon USING (false);

-- 4. Address & Geolocation Privacy
DROP POLICY IF EXISTS "addresses_owner_access" ON "public"."addresses";
CREATE POLICY "addresses_owner_access" ON "public"."addresses"
  FOR ALL TO authenticated
  USING (auth.uid()::text = user_id);

DROP POLICY IF EXISTS "addresses_block_anon" ON "public"."addresses";
CREATE POLICY "addresses_block_anon" ON "public"."addresses"
  FOR ALL TO anon USING (false);

-- 5. Order & Delivery Lifecycle Isolation
DROP POLICY IF EXISTS "orders_participant_access" ON "public"."orders";
CREATE POLICY "orders_participant_access" ON "public"."orders"
  FOR ALL TO authenticated
  USING (
    customer_id = auth.uid()::text 
    OR runner_id = auth.uid()::text
    OR EXISTS (SELECT 1 FROM "public"."stores" s WHERE s.id = orders.store_id AND s.owner_id = auth.uid()::text)
  );

DROP POLICY IF EXISTS "order_items_participant_access" ON "public"."order_items";
CREATE POLICY "order_items_participant_access" ON "public"."order_items"
  FOR SELECT TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM "public"."orders" o 
      WHERE o.id = order_items.order_id 
      AND (
        o.customer_id = auth.uid()::text 
        OR o.runner_id = auth.uid()::text 
        OR EXISTS (SELECT 1 FROM "public"."stores" s WHERE s.id = o.store_id AND s.owner_id = auth.uid()::text)
      )
    )
  );

DROP POLICY IF EXISTS "order_timeline_participant_access" ON "public"."order_timeline";
CREATE POLICY "order_timeline_participant_access" ON "public"."order_timeline"
  FOR SELECT TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM "public"."orders" o 
      WHERE o.id = order_timeline.order_id 
      AND (
        o.customer_id = auth.uid()::text 
        OR o.runner_id = auth.uid()::text 
        OR EXISTS (SELECT 1 FROM "public"."stores" s WHERE s.id = o.store_id AND s.owner_id = auth.uid()::text)
      )
    )
  );

-- 6. Support Tickets, Notifications, & Ration Lists Isolation
DROP POLICY IF EXISTS "support_tickets_owner_access" ON "public"."support_tickets";
CREATE POLICY "support_tickets_owner_access" ON "public"."support_tickets"
  FOR ALL TO authenticated USING (user_id = auth.uid()::text);

DROP POLICY IF EXISTS "ticket_messages_participant_access" ON "public"."ticket_messages";
CREATE POLICY "ticket_messages_participant_access" ON "public"."ticket_messages"
  FOR ALL TO authenticated
  USING (
    sender_id = auth.uid()::text 
    OR EXISTS (SELECT 1 FROM "public"."support_tickets" t WHERE t.id = ticket_messages.ticket_id AND t.user_id = auth.uid()::text)
  );

DROP POLICY IF EXISTS "notifications_owner_access" ON "public"."notifications";
CREATE POLICY "notifications_owner_access" ON "public"."notifications"
  FOR ALL TO authenticated USING (user_id = auth.uid()::text);

DROP POLICY IF EXISTS "monthly_ration_lists_owner_access" ON "public"."monthly_ration_lists";
CREATE POLICY "monthly_ration_lists_owner_access" ON "public"."monthly_ration_lists"
  FOR ALL TO authenticated USING (user_id = auth.uid()::text);

DROP POLICY IF EXISTS "monthly_ration_items_owner_access" ON "public"."monthly_ration_items";
CREATE POLICY "monthly_ration_items_owner_access" ON "public"."monthly_ration_items"
  FOR ALL TO authenticated
  USING (EXISTS (SELECT 1 FROM "public"."monthly_ration_lists" l WHERE l.id = monthly_ration_items.list_id AND l.user_id = auth.uid()::text));

-- 7. High-Security Tables: Complete Anon/Client Block
DROP POLICY IF EXISTS "otp_challenges_strictly_locked" ON "public"."otp_challenges";
CREATE POLICY "otp_challenges_strictly_locked" ON "public"."otp_challenges"
  FOR ALL TO anon, authenticated USING (false);

DROP POLICY IF EXISTS "audit_logs_strictly_locked" ON "public"."audit_logs";
CREATE POLICY "audit_logs_strictly_locked" ON "public"."audit_logs"
  FOR ALL TO anon, authenticated USING (false);
