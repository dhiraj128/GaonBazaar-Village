export interface AdminOverview {
  pilot_area: string;
  max_delivery_radius_km: number;
  platform_fee: number;
  vendor_commission_pct: number;
  total_stores: number;
  active_stores: number;
  total_runners: number;
  online_runners: number;
  total_orders: number;
  active_orders_count: number;
  total_gmv: number;
  pending_vendor_approvals: number;
  pending_runner_approvals: number;
}

export interface StoreItem {
  id: string;
  owner_id: string;
  shop_name: string;
  owner_name: string;
  category: string;
  latitude: number;
  longitude: number;
  village: string;
  landmark?: string;
  block: string;
  district: string;
  is_online: boolean;
  is_approved: boolean;
  rating: number;
  payout_upi_id?: string;
  digilocker_verified?: boolean;
}

export interface RunnerItem {
  id: string;
  user_id: string;
  full_name: string;
  phone_number?: string;
  vehicle_type: string;
  vehicle_number: string;
  driving_license_number: string;
  is_online: boolean;
  is_approved: boolean;
  rating: number;
  payout_upi_id?: string;
  digilocker_verified?: boolean;
}

export interface OrderItemRecord {
  id: string;
  customer_id: string;
  store_id: string;
  store_name: string;
  runner_id?: string;
  status: 'PLACED' | 'ACCEPTED' | 'PACKED' | 'RUNNER_ASSIGNED' | 'PICKED_UP' | 'OUT_FOR_DELIVERY' | 'DELIVERED' | 'CANCELLED';
  subtotal: number;
  delivery_fee: number;
  platform_fee: number;
  total_amount: number;
  payment_mode: 'COD' | 'ONLINE';
  payment_status: 'PENDING' | 'PAID' | 'REFUNDED';
  delivery_otp: string;
  items_count: number;
  created_at: string;
  is_cancellable?: boolean;
}

export interface CatalogItem {
  id?: string;
  name_en: string;
  name_hi: string;
  category: string;
  standard_unit: string;
  suggested_price: number;
  image_url: string;
}

export interface ZoneLocality {
  name: string;
  lat: number;
  lng: number;
}

export interface PlatformSettings {
  pilot_block: string;
  pilot_district: string;
  pilot_state: string;
  pilot_localities: ZoneLocality[];
  max_delivery_radius_km: number;
  platform_fee: number;
  vendor_commission_pct: number;
  cancel_window_seconds: number;
}

export interface SettlementLedger {
  vendor_settlements: {
    store_id: string;
    store_name: string;
    total_payout: number;
    order_count: number;
  }[];
  runner_settlements: {
    runner_id: string;
    total_payout: number;
    order_count: number;
  }[];
  platform_fee_collected: number;
  total_delivered_orders: number;
}

export interface CustomerItem {
  id: string;
  phone: string;
  name: string;
  preferred_language: string;
  is_active: boolean;
  addresses_count: number;
  orders_count: number;
  created_at: string;
}

export interface SupportTicketItem {
  id: string;
  user_id: string;
  order_id?: string;
  subject: string;
  message: string;
  status: 'OPEN' | 'RESOLVED' | 'CLOSED';
  created_at: string;
}

export interface AuditLogItem {
  id: string;
  actor_id?: string;
  actor_role: string;
  action: string;
  target_type: string;
  target_id?: string;
  details?: string;
  created_at: string;
}

