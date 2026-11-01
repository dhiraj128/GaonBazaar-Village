import type {
  AdminOverview,
  StoreItem,
  RunnerItem,
  OrderItemRecord,
  CatalogItem,
  PlatformSettings,
  SettlementLedger,
  CustomerItem,
  SupportTicketItem,
  AuditLogItem,
} from './types';

const API_BASE = 'http://localhost:8000/api/v1/admin';

// Fallback initial in-memory state
let initialStores: StoreItem[] = [
  {
    id: 'store_001',
    owner_id: 'user_v1',
    shop_name: 'Minapur Central Kirana & General Store',
    owner_name: 'Ramesh Kumar Sahni',
    category: 'Grocery & Ration',
    latitude: 26.1950,
    longitude: 85.3450,
    village: 'Chaturshi',
    landmark: 'Near Hanuman Mandir Chowk',
    block: 'Minapur',
    district: 'Muzaffarpur',
    is_online: true,
    is_approved: true,
    rating: 4.8,
    payout_upi_id: 'ramesh.sahni@upi',
    digilocker_verified: true,
  },
  {
    id: 'store_002',
    owner_id: 'user_v2',
    shop_name: 'Sivay Patti Green Sabzi & Fruits',
    owner_name: 'Santosh Yadav',
    category: 'Vegetables & Fruits',
    latitude: 26.2250,
    longitude: 85.3600,
    village: 'Sivay Patti',
    landmark: 'Opposite High School Field',
    block: 'Minapur',
    district: 'Muzaffarpur',
    is_online: true,
    is_approved: true,
    rating: 4.6,
    payout_upi_id: 'santosh.sabzi@upi',
    digilocker_verified: true,
  },
  {
    id: 'store_003',
    owner_id: 'user_v3',
    shop_name: 'Tulsi Ganj Shudh Dugdh & Paneer Kendra',
    owner_name: 'Manoj Rai',
    category: 'Fresh Dairy',
    latitude: 26.1880,
    longitude: 85.3320,
    village: 'Tulsi Ganj / Bangaon',
    landmark: 'Near Primary Health Center',
    block: 'Minapur',
    district: 'Muzaffarpur',
    is_online: false,
    is_approved: false, // Pending KYC
    rating: 0.0,
    payout_upi_id: 'manoj.dairy@upi',
    digilocker_verified: true,
  },
  {
    id: 'store_004',
    owner_id: 'user_v4',
    shop_name: 'Benaghara Electrical & Hardware Mart',
    owner_name: 'Rajendra Mahto',
    category: 'Electrical & Hardware',
    latitude: 26.2100,
    longitude: 85.3550,
    village: 'Tubanaghara / Benaghara',
    landmark: 'Benaghara Bazar Pulia',
    block: 'Minapur',
    district: 'Muzaffarpur',
    is_online: true,
    is_approved: false, // Pending KYC
    rating: 0.0,
    payout_upi_id: 'rajendra.mahto@upi',
    digilocker_verified: false,
  },
];

let initialRunners: RunnerItem[] = [
  {
    id: 'runner_001',
    user_id: 'user_r1',
    full_name: 'Amit Kumar Paswan',
    phone_number: '+91 98765 43210',
    vehicle_type: 'Motorcycle (Hero Splendor)',
    vehicle_number: 'BR-06-AB-4592',
    driving_license_number: 'DL-BR-2022-09418',
    is_online: true,
    is_approved: true,
    rating: 4.9,
    payout_upi_id: 'amit.paswan@paytm',
    digilocker_verified: true,
  },
  {
    id: 'runner_002',
    user_id: 'user_r2',
    full_name: 'Vikash Kumar Thakur',
    phone_number: '+91 98765 43211',
    vehicle_type: 'Bicycle (Hero Jet)',
    vehicle_number: 'CYCLE-NA',
    driving_license_number: 'AADHAAR-VERIFIED',
    is_online: true,
    is_approved: true,
    rating: 4.7,
    payout_upi_id: 'vikash.thakur@oksbi',
    digilocker_verified: true,
  },
  {
    id: 'runner_003',
    user_id: 'user_r3',
    full_name: 'Deepak Kumar Singh',
    phone_number: '+91 98765 43212',
    vehicle_type: 'Scooter (Honda Activa)',
    vehicle_number: 'BR-06-XY-1122',
    driving_license_number: 'DL-BR-2024-11029',
    is_online: false,
    is_approved: false, // Pending KYC
    rating: 0.0,
    payout_upi_id: 'deepak.singh@gpay',
    digilocker_verified: true,
  },
];

let initialOrders: OrderItemRecord[] = [
  {
    id: 'ord_1001',
    customer_id: 'cust_01',
    store_id: 'store_001',
    store_name: 'Minapur Central Kirana & General Store',
    runner_id: 'runner_001',
    status: 'OUT_FOR_DELIVERY',
    subtotal: 345.0,
    delivery_fee: 25.0,
    platform_fee: 3.0,
    total_amount: 373.0,
    payment_mode: 'COD',
    payment_status: 'PENDING',
    delivery_otp: '7829',
    items_count: 4,
    created_at: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
    is_cancellable: false,
  },
  {
    id: 'ord_1002',
    customer_id: 'cust_02',
    store_id: 'store_002',
    store_name: 'Sivay Patti Green Sabzi & Fruits',
    runner_id: undefined,
    status: 'PACKED',
    subtotal: 180.0,
    delivery_fee: 20.0,
    platform_fee: 3.0,
    total_amount: 203.0,
    payment_mode: 'ONLINE',
    payment_status: 'PAID',
    delivery_otp: '4410',
    items_count: 3,
    created_at: new Date(Date.now() - 8 * 60 * 1000).toISOString(),
    is_cancellable: false,
  },
  {
    id: 'ord_1003',
    customer_id: 'cust_03',
    store_id: 'store_001',
    store_name: 'Minapur Central Kirana & General Store',
    runner_id: undefined,
    status: 'PLACED',
    subtotal: 510.0,
    delivery_fee: 30.0,
    platform_fee: 3.0,
    total_amount: 543.0,
    payment_mode: 'COD',
    payment_status: 'PENDING',
    delivery_otp: '9152',
    items_count: 5,
    created_at: new Date(Date.now() - 60 * 1000).toISOString(),
    is_cancellable: true,
  },
  {
    id: 'ord_1000',
    customer_id: 'cust_00',
    store_id: 'store_001',
    store_name: 'Minapur Central Kirana & General Store',
    runner_id: 'runner_002',
    status: 'DELIVERED',
    subtotal: 290.0,
    delivery_fee: 20.0,
    platform_fee: 3.0,
    total_amount: 313.0,
    payment_mode: 'COD',
    payment_status: 'PAID',
    delivery_otp: '6331',
    items_count: 2,
    created_at: new Date(Date.now() - 65 * 60 * 1000).toISOString(),
    is_cancellable: false,
  },
];

let initialCatalog: CatalogItem[] = [
  {
    id: 'cat_01',
    name_en: 'Aashirvaad Shudh Chakki Atta',
    name_hi: 'आशीर्वाद शुद्ध चक्की आटा',
    category: 'Grocery & Ration',
    standard_unit: '5 kg',
    suggested_price: 245.0,
    image_url: 'https://images.unsplash.com/photo-1586201375761-83865001e31c?w=500&q=80',
  },
  {
    id: 'cat_02',
    name_en: 'Fresh Farm Mustard Oil (Kachhi Ghani)',
    name_hi: 'सरसों का शुद्ध तेल',
    category: 'Grocery & Ration',
    standard_unit: '1 Litre',
    suggested_price: 155.0,
    image_url: 'https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=500&q=80',
  },
  {
    id: 'cat_03',
    name_en: 'Fresh Village Cow Milk',
    name_hi: 'ताज़ा गाय का दूध',
    category: 'Fresh Dairy',
    standard_unit: '1 Litre',
    suggested_price: 56.0,
    image_url: 'https://images.unsplash.com/photo-1550583724-b2692b85b150?w=500&q=80',
  },
  {
    id: 'cat_04',
    name_en: 'Local Farm Potatoes (Aloo)',
    name_hi: 'देसी नया आलू',
    category: 'Vegetables & Fruits',
    standard_unit: '2 kg',
    suggested_price: 48.0,
    image_url: 'https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=500&q=80',
  },
  {
    id: 'cat_05',
    name_en: 'Pure Camphor Tablets (Karpur)',
    name_hi: 'शुद्ध भीमसेनी कपूर',
    category: 'Pooja & Rituals',
    standard_unit: '50 g',
    suggested_price: 35.0,
    image_url: 'https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?w=500&q=80',
  },
  {
    id: 'cat_06',
    name_en: 'Philips 9W LED Cool Day Bulb',
    name_hi: 'फिलिप्स 9 वाट एलईडी बल्ब',
    category: 'Electrical & Hardware',
    standard_unit: '1 Piece',
    suggested_price: 90.0,
    image_url: 'https://images.unsplash.com/photo-1550985543-f47f38aeee65?w=500&q=80',
  },
  {
    id: 'cat_07',
    name_en: 'Fresh Desi Tomatoes (Tamatar)',
    name_hi: 'देशी लाल टमाटर',
    category: 'Vegetables & Fruits',
    standard_unit: '1 kg',
    suggested_price: 32.0,
    image_url: 'https://images.unsplash.com/photo-1546470427-227c7369a941?w=500&q=80',
  },
  {
    id: 'cat_08',
    name_en: 'Nashik Red Onions (Pyaz)',
    name_hi: 'ताज़ा लाल प्याज',
    category: 'Vegetables & Fruits',
    standard_unit: '1 kg',
    suggested_price: 38.0,
    image_url: 'https://images.unsplash.com/photo-1618512496248-a07fe83aa8cb?w=500&q=80',
  },
  {
    id: 'cat_09',
    name_en: 'Madhur Pure Refined Sugar',
    name_hi: 'सफ़ेद चीनी (शक्कर)',
    category: 'Grocery & Ration',
    standard_unit: '1 kg',
    suggested_price: 45.0,
    image_url: 'https://images.unsplash.com/photo-1622484212850-eb596d769edc?w=500&q=80',
  },
  {
    id: 'cat_10',
    name_en: 'Tata Salt Vacuum Evaporated Iodized',
    name_hi: 'टाटा नमक आयोडीन युक्त',
    category: 'Grocery & Ration',
    standard_unit: '1 kg',
    suggested_price: 28.0,
    image_url: 'https://images.unsplash.com/photo-1626082896492-766af4eb6501?w=500&q=80',
  },
  {
    id: 'cat_11',
    name_en: 'Parle-G Gold Glucose Biscuits',
    name_hi: 'पारले-जी ग्लूकोज बिस्कुट',
    category: 'Grocery & Ration',
    standard_unit: '250 g',
    suggested_price: 25.0,
    image_url: 'https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=500&q=80',
  },
  {
    id: 'cat_12',
    name_en: 'Fresh Green Chili & Coriander Combo',
    name_hi: 'हरी मिर्च एवं धनिया पत्ती',
    category: 'Vegetables & Fruits',
    standard_unit: '250 g',
    suggested_price: 20.0,
    image_url: 'https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=500&q=80',
  },
  {
    id: 'cat_13',
    name_en: 'Unpolished Desi Toor / Arhar Dal',
    name_hi: 'शुद्ध अरहर दाल',
    category: 'Grocery & Ration',
    standard_unit: '1 kg',
    suggested_price: 145.0,
    image_url: 'https://images.unsplash.com/photo-1585994192701-f1a505c817ea?w=500&q=80',
  },
  {
    id: 'cat_14',
    name_en: 'Premium Chandan Incense Sticks (Agarbatti)',
    name_hi: 'प्रीमियम चंदन अगरबत्ती',
    category: 'Pooja & Rituals',
    standard_unit: '1 Pack',
    suggested_price: 30.0,
    image_url: 'https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?w=500&q=80',
  },
];

export const adminApi = {
  async getOverview(): Promise<AdminOverview> {
    try {
      const res = await fetch(`${API_BASE}/overview`);
      if (res.ok) return await res.json();
    } catch {}
    
    // Fallback calculation
    const totalGmv = initialOrders
      .filter((o) => o.status === 'DELIVERED')
      .reduce((sum, o) => sum + o.total_amount, 0);
    const activeOrders = initialOrders.filter(
      (o) => o.status !== 'DELIVERED' && o.status !== 'CANCELLED'
    );
    const pendingVendors = initialStores.filter((s) => !s.is_approved).length;
    const pendingRunners = initialRunners.filter((r) => !r.is_approved).length;

    return {
      pilot_area: 'Minapur Block, Muzaffarpur, Bihar',
      max_delivery_radius_km: 8.0,
      platform_fee: 3.0,
      vendor_commission_pct: 0.0,
      total_stores: initialStores.length,
      active_stores: initialStores.filter((s) => s.is_online && s.is_approved).length,
      total_runners: initialRunners.length,
      online_runners: initialRunners.filter((r) => r.is_online && r.is_approved).length,
      total_orders: initialOrders.length,
      active_orders_count: activeOrders.length,
      total_gmv: totalGmv,
      pending_vendor_approvals: pendingVendors,
      pending_runner_approvals: pendingRunners,
    };
  },

  async getVendors(): Promise<StoreItem[]> {
    try {
      const res = await fetch(`${API_BASE}/vendors`);
      if (res.ok) return await res.json();
    } catch {}
    return [...initialStores];
  },

  async approveVendor(id: string): Promise<void> {
    try {
      await fetch(`${API_BASE}/vendors/${id}/approve`, { method: 'POST' });
    } catch {}
    initialStores = initialStores.map((s) => (s.id === id ? { ...s, is_approved: true } : s));
  },

  async rejectVendor(id: string): Promise<void> {
    try {
      await fetch(`${API_BASE}/vendors/${id}/reject`, { method: 'POST' });
    } catch {}
    initialStores = initialStores.map((s) => (s.id === id ? { ...s, is_approved: false } : s));
  },

  async getRunners(): Promise<RunnerItem[]> {
    try {
      const res = await fetch(`${API_BASE}/runners`);
      if (res.ok) return await res.json();
    } catch {}
    return [...initialRunners];
  },

  async approveRunner(id: string): Promise<void> {
    try {
      await fetch(`${API_BASE}/runners/${id}/approve`, { method: 'POST' });
    } catch {}
    initialRunners = initialRunners.map((r) => (r.id === id ? { ...r, is_approved: true } : r));
  },

  async rejectRunner(id: string): Promise<void> {
    try {
      await fetch(`${API_BASE}/runners/${id}/reject`, { method: 'POST' });
    } catch {}
    initialRunners = initialRunners.map((r) => (r.id === id ? { ...r, is_approved: false } : r));
  },

  async getOrders(): Promise<OrderItemRecord[]> {
    try {
      const res = await fetch(`${API_BASE}/orders`);
      if (res.ok) return await res.json();
    } catch {}
    return [...initialOrders];
  },

  async updateOrderStatus(id: string, status: OrderItemRecord['status']): Promise<void> {
    try {
      await fetch(`${API_BASE}/orders/${id}/status`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status }),
      });
    } catch {}
    initialOrders = initialOrders.map((o) => (o.id === id ? { ...o, status } : o));
  },

  async getCatalog(): Promise<CatalogItem[]> {
    try {
      const res = await fetch(`${API_BASE}/catalog`);
      if (res.ok) return await res.json();
    } catch {}
    return [...initialCatalog];
  },

  async addCatalogItem(item: CatalogItem): Promise<CatalogItem> {
    try {
      const res = await fetch(`${API_BASE}/catalog`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(item),
      });
      if (res.ok) return await res.json();
    } catch {}
    const newItem = { ...item, id: `cat_${Date.now()}` };
    initialCatalog.push(newItem);
    return newItem;
  },

  async getSettings(): Promise<PlatformSettings> {
    try {
      const res = await fetch(`${API_BASE}/settings`);
      if (res.ok) return await res.json();
    } catch {}
    return {
      pilot_block: 'Minapur Block',
      pilot_district: 'Muzaffarpur',
      pilot_state: 'Bihar',
      pilot_localities: [
        { name: 'Chaturshi / Chatursi', lat: 26.1950, lng: 85.3450 },
        { name: 'Tubanaghara / Benaghara', lat: 26.2100, lng: 85.3550 },
        { name: 'Sivay Patti', lat: 26.2250, lng: 85.3600 },
        { name: 'Tulsi Ganj / Bangaon', lat: 26.1880, lng: 85.3320 },
      ],
      max_delivery_radius_km: 8.0,
      platform_fee: 3.0,
      vendor_commission_pct: 0.0,
      cancel_window_seconds: 180,
    };
  },

  async getSettlements(): Promise<SettlementLedger> {
    try {
      const res = await fetch(`${API_BASE}/settlements`);
      if (res.ok) return await res.json();
    } catch {}
    const delivered = initialOrders.filter((o) => o.status === 'DELIVERED');
    return {
      vendor_settlements: [
        {
          store_id: 'store_001',
          store_name: 'Minapur Central Kirana & General Store',
          total_payout: 290.0,
          order_count: 1,
        },
      ],
      runner_settlements: [
        {
          runner_id: 'runner_002',
          total_payout: 20.0,
          order_count: 1,
        },
      ],
      platform_fee_collected: delivered.length * 3.0,
      total_delivered_orders: delivered.length,
    };
  },

  async getCustomers(): Promise<CustomerItem[]> {
    try {
      const res = await fetch(`${API_BASE}/customers`);
      if (res.ok) return await res.json();
    } catch {}
    return [
      {
        id: 'cust_001',
        phone: '9876543210',
        name: 'Amit Kumar Singh',
        preferred_language: 'hi',
        is_active: true,
        addresses_count: 2,
        orders_count: 5,
        created_at: '2026-10-25T10:00:00Z',
      },
      {
        id: 'cust_002',
        phone: '9812345678',
        name: 'Pooja Kumari',
        preferred_language: 'hi',
        is_active: true,
        addresses_count: 1,
        orders_count: 3,
        created_at: '2026-10-28T14:30:00Z',
      },
    ];
  },

  async getTickets(): Promise<SupportTicketItem[]> {
    try {
      const res = await fetch(`${API_BASE}/tickets`);
      if (res.ok) return await res.json();
    } catch {}
    return [
      {
        id: 'tick_001',
        user_id: 'cust_001',
        order_id: 'ORD-20261031-001',
        subject: 'Delivery delayed due to rain',
        message: 'Runner informed road waterlogged near Sivay Patti culvert',
        status: 'OPEN',
        created_at: '2026-11-01T11:00:00Z',
      },
      {
        id: 'tick_002',
        user_id: 'user_v1',
        subject: 'Product pricing update request',
        message: 'Want to update local mustard oil brand price to match village rate',
        status: 'RESOLVED',
        created_at: '2026-10-31T16:00:00Z',
      },
    ];
  },

  async updateTicketStatus(id: string, status: 'OPEN' | 'RESOLVED' | 'CLOSED'): Promise<void> {
    try {
      await fetch(`${API_BASE}/tickets/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status }),
      });
    } catch {}
  },

  async getAuditLogs(): Promise<AuditLogItem[]> {
    try {
      const res = await fetch(`${API_BASE}/audit-logs`);
      if (res.ok) return await res.json();
    } catch {}
    return [
      {
        id: 'log_001',
        actor_role: 'super_admin',
        action: 'VENDOR_APPROVED',
        target_type: 'STORE',
        target_id: 'store_001',
        details: 'Approved Minapur Central Kirana & General Store after physical verification',
        created_at: '2026-10-30T09:15:00Z',
      },
      {
        id: 'log_002',
        actor_role: 'system',
        action: 'SETTINGS_UPDATED',
        target_type: 'PLATFORM_SETTINGS',
        target_id: 'global',
        details: 'Radius: 8.0km, PlatformFee: ₹3, Commission: 0%',
        created_at: '2026-10-31T12:00:00Z',
      },
    ];
  },

  async updateSettings(settings: Partial<PlatformSettings>): Promise<PlatformSettings> {
    try {
      const res = await fetch(`${API_BASE}/settings`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settings),
      });
      if (res.ok) return await res.json();
    } catch {}
    return {
      pilot_block: 'Minapur Block',
      pilot_district: 'Muzaffarpur',
      pilot_state: 'Bihar',
      pilot_localities: [
        { name: 'Chaturshi / Chatursi', lat: 26.1950, lng: 85.3450 },
        { name: 'Tubanaghara / Benaghara', lat: 26.2100, lng: 85.3550 },
        { name: 'Sivay Patti', lat: 26.2250, lng: 85.3600 },
        { name: 'Tulsi Ganj / Bangaon', lat: 26.1880, lng: 85.3320 },
      ],
      max_delivery_radius_km: settings.max_delivery_radius_km ?? 8.0,
      platform_fee: settings.platform_fee ?? 3.0,
      vendor_commission_pct: settings.vendor_commission_pct ?? 0.0,
      cancel_window_seconds: 180,
    };
  },
};
