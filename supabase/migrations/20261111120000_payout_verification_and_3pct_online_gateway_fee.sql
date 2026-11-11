-- ==============================================================================
-- GAONBAZAAR PAYOUT VERIFICATION & 3% ONLINE GATEWAY FEE MIGRATION
-- ==============================================================================

-- 1. Add payout_account_verified flag to users table
ALTER TABLE public.users 
ADD COLUMN IF NOT EXISTS payout_account_verified BOOLEAN DEFAULT false;

-- 2. Add online_gateway_fee (strict 3% on ONLINE, 0% on COD) to orders table
ALTER TABLE public.orders 
ADD COLUMN IF NOT EXISTS online_gateway_fee DOUBLE PRECISION DEFAULT 0.0;

-- 3. Add collection_mode ('CASH', 'ADMIN_QR') for Doorstep QR Digital COD
ALTER TABLE public.orders 
ADD COLUMN IF NOT EXISTS collection_mode VARCHAR(30) DEFAULT 'CASH';

-- 4. Index for performance
CREATE INDEX IF NOT EXISTS idx_users_payout_verified ON public.users(payout_account_verified);
CREATE INDEX IF NOT EXISTS idx_orders_online_gateway_fee ON public.orders(online_gateway_fee);
CREATE INDEX IF NOT EXISTS idx_orders_collection_mode ON public.orders(collection_mode);
