export type AdminRole = 'super_admin' | 'hub_manager' | 'admin';

export interface AdminUser {
  id: string;
  phone: string;
  name: string;
  role: AdminRole;
}

export interface AdminOverview {
  pilot_area: string;
  max_delivery_radius_km: number;
  platform_fee: number;
  vendor_commission_pct: number;
  total_stores: number;
  active_stores: number;
  total_runners: number;
  online_runners: number;
  active_riders_online: number;
  active_riders_busy: number;
  active_riders_idle: number;
  total_orders: number;
  active_orders_count: number;
  delayed_orders_count: number;
  total_gmv: number;
  revenue_today: number;
  cash_to_collect_cod: number;
  pending_vendor_approvals: number;
  pending_runner_approvals: number;
}

export interface ExceptionAlert {
  id: string;
  type: 'SOS_RIDER' | 'ORDER_DELAYED' | 'STORE_UNACCEPTED';
  severity: 'CRITICAL' | 'HIGH' | 'WARNING';
  title: string;
  description: string;
  order_id?: string;
  store_name?: string;
  runner_id?: string;
  runner_name?: string;
  latitude?: number;
  longitude?: number;
  elapsed_minutes?: number;
  created_at: string;
  available_actions: string[];
}

export interface HourlyTrendPoint {
  hour: string;
  today: number;
  yesterday: number;
}

export interface HourlyTrendsData {
  trend_data: HourlyTrendPoint[];
  peak_hour_today: number;
  total_today_orders: number;
  total_yesterday_orders: number;
}

export interface PendingKycApplicant {
  id: string;
  type: 'VENDOR' | 'RUNNER';
  name: string;
  shop_name?: string;
  vehicle_type?: string;
  phone: string;
  village: string;
  status: 'Pending' | 'Approved' | 'Rejected';
  created_at?: string;
}

export interface KycSideBySideDetail {
  applicant_type: 'VENDOR' | 'RUNNER';
  id: string;
  is_approved: boolean;
  user_submitted: {
    name: string;
    shop_name?: string;
    category?: string;
    village: string;
    phone: string;
    bank_account_number: string;
    bank_ifsc: string;
    upi_id?: string;
    selfie_url?: string;
    shop_photo_url?: string;
    aadhaar_document_url?: string;
    vehicle_type?: string;
    vehicle_number?: string;
    driving_license_no?: string;
    driving_license_url?: string;
  };
  api_verified: {
    penny_drop_bank_match: {
      verified_account_holder: string;
      bank_name: string;
      account_status: string;
      match_status: string;
      penny_drop_reference?: string | null;
    };
    aadhaar_liveness: {
      liveness_score?: number | null;
      liveness_check: string;
      face_match_confidence: string;
      aadhaar_uidai_status: string;
      address_state_match?: string;
      dl_vahan_status?: string;
      review_mode?: string;
    };
  };
}

export interface DirectoryUser {
  id: string;
  name: string;
  phone: string;
  role: 'customer' | 'vendor' | 'runner' | 'admin' | string;
  is_active: boolean;
  village?: string;
  store_name?: string;
  runner_vehicle?: string;
  orders_count: number;
  created_at?: string;
}

export interface OrderItemDetail {
  id: string;
  product_id: string;
  name: string;
  quantity: number;
  unit_price: number;
  total_price: number;
}

export interface OrderItemRecord {
  id: string;
  customer_id: string;
  customer_name?: string;
  customer_phone?: string;
  store_id: string;
  store_name: string;
  runner_id?: string;
  runner_name?: string;
  runner_phone?: string;
  status: 'PLACED' | 'ACCEPTED' | 'PACKED' | 'RUNNER_ASSIGNED' | 'PICKED_UP' | 'OUT_FOR_DELIVERY' | 'DELIVERED' | 'CANCELLED';
  subtotal: number;
  delivery_fee: number;
  platform_fee: number;
  total_amount: number;
  payment_mode: 'COD' | 'ONLINE';
  payment_status: 'PENDING' | 'PAID' | 'REFUNDED';
  delivery_otp: string;
  items_count: number;
  items?: OrderItemDetail[];
  delivery_village?: string;
  elapsed_minutes?: number;
  created_at: string;
  is_cancellable?: boolean;
}

export interface RiderMapPin {
  runner_id: string;
  name: string;
  phone: string;
  vehicle_type: string;
  vehicle_number: string;
  latitude: number;
  longitude: number;
  state: 'IDLE' | 'BUSY' | 'OFFLINE' | 'ISSUE';
  color: 'green' | 'orange' | 'red';
  assigned_order_id?: string;
  assigned_order_status?: string;
  battery_level: number;
  speed_kmh: number;
  last_ping: string;
}

export interface DemandHeatmapZone {
  zone_id: string;
  zone_name: string;
  latitude: number;
  longitude: number;
  radius_meters: number;
  intensity: number;
  is_red_zone: boolean;
  active_orders: number;
  available_riders: number;
  description: string;
}

export interface CodReconciliationItem {
  runner_id: string;
  runner_name: string;
  phone: string;
  cash_held_inr: number;
  undeposited_orders_count: number;
  order_ids: string[];
  status: string;
}

export interface SettlementLedger {
  vendor_settlements: {
    store_id: string;
    store_name: string;
    gross_sales?: number;
    platform_commission?: number;
    total_payout: number;
    order_count: number;
    bank_account?: string;
    ifsc?: string;
  }[];
  runner_settlements: {
    runner_id: string;
    runner_name?: string;
    delivery_fees?: number;
    bonuses?: number;
    total_payout: number;
    order_count: number;
    bank_account?: string;
    ifsc?: string;
  }[];
  vendor_payouts_due: number;
  runner_payouts_due: number;
  platform_fee_collected: number;
  total_delivered_orders: number;
}

export interface CatalogItem {
  id?: string;
  name_en: string;
  name_hi: string;
  category: string;
  standard_unit?: string;
  default_unit?: string;
  suggested_price?: number;
  suggested_mrp?: number;
  image_url: string;
}

export interface PromoCodeItem {
  id: string;
  code: string;
  discount_pct: number;
  min_order_value: number;
  max_discount: number;
  created_at: string;
  is_active: boolean;
}

export interface PlatformSettings {
  pilot_block: string;
  pilot_district: string;
  pilot_state: string;
  pilot_localities: { name: string; lat: number; lng: number }[];
  max_delivery_radius_km: number;
  min_order_value?: number;
  base_delivery_fee?: number;
  per_km_fee?: number;
  platform_fee: number;
  vendor_commission_pct: number;
  cancel_window_seconds: number;
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

export interface TicketMessageItem {
  id: string;
  sender_id: string;
  sender_role: string;
  message: string;
  attachment_url?: string;
  created_at: string;
}

export interface SupportTicketItem {
  id: string;
  user_id: string;
  user_name?: string;
  user_phone?: string;
  order_id?: string;
  category?: string;
  affected_product_id?: string;
  subject: string;
  message: string;
  attachment_url?: string;
  status: 'OPEN' | 'RESOLVED' | 'CLOSED';
  resolution_notes?: string;
  resolved_at?: string;
  created_at: string;
  reply_count?: number;
  messages?: TicketMessageItem[];
}

export interface AuditLogItem {
  id: string;
  actor_id?: string;
  actor_role?: string;
  action: string;
  target_type: string;
  target_id: string;
  details?: string;
  ip_address?: string;
  created_at?: string;
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
