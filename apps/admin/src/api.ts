import type {
  AdminOverview,
  ExceptionAlert,
  HourlyTrendsData,
  PendingKycApplicant,
  KycSideBySideDetail,
  DirectoryUser,
  OrderItemRecord,
  RiderMapPin,
  DemandHeatmapZone,
  CodReconciliationItem,
  SettlementLedger,
  CatalogItem,
  PromoCodeItem,
  PlatformSettings,
  CustomerItem,
  SupportTicketItem,
  AuditLogItem,
  AdminUser,
  AdminRole,
} from './types';

declare global {
  interface Window {
    supabase?: any;
  }
}

const SUPABASE_URL = "https://vxewgvrjhjpntfvsmuez.supabase.co";
const SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ4ZXdndnJqaGpwbnRmdnNtdWV6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTM1NDkwMzcsImV4cCI6MjEwOTEyNTAzN30.3jUR0U9RGcgc2q-zeWX7OeWaFqugSHOFdDieYoGFIwQ";

const getApiBase = (): string => {
  if (typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')) {
    return 'http://127.0.0.1:8000/api/v1/admin';
  }
  return ((import.meta.env.VITE_API_BASE_URL || 'https://gaonbazaar-village.onrender.com/api/v1') + '/admin');
};

const API_BASE = getApiBase();

const TOKEN_STORAGE_KEY = 'gaonbazaar_admin_jwt_token';
const USER_STORAGE_KEY = 'gaonbazaar_admin_user_info';

export const getAdminToken = (): string | null => {
  try {
    return localStorage.getItem(TOKEN_STORAGE_KEY);
  } catch {
    return null;
  }
};

export const setAdminToken = (token: string): void => {
  try {
    localStorage.setItem(TOKEN_STORAGE_KEY, token);
  } catch {}
};

export const clearAdminToken = (): void => {
  try {
    localStorage.removeItem(TOKEN_STORAGE_KEY);
    localStorage.removeItem(USER_STORAGE_KEY);
  } catch {}
};

export const getStoredAdminUser = (): AdminUser | null => {
  try {
    const raw = localStorage.getItem(USER_STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
};

export const setStoredAdminUser = (user: AdminUser): void => {
  try {
    localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(user));
  } catch {}
};

const getAuthHeaders = (): Record<string, string> => {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  const token = getAdminToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
};

// Generic fetch handler with strict error propagation — ZERO fake fallback arrays
async function apiRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      ...getAuthHeaders(),
      ...(options.headers || {}),
    },
  });

  if (!response.ok) {
    let errorDetail = `HTTP ${response.status} ${response.statusText}`;
    try {
      const body = await response.json();
      if (body.detail) {
        errorDetail = typeof body.detail === 'string' ? body.detail : JSON.stringify(body.detail);
      }
    } catch {
      // Body not JSON
    }
    throw new Error(errorDetail);
  }

  return response.json();
}

export const adminApi = {
  isAuthenticated(): boolean {
    return !!getAdminToken();
  },

  getCurrentUser(): AdminUser | null {
    return getStoredAdminUser();
  },

  async login(phone: string, secretKey: string, role?: AdminRole): Promise<{ token: string; user: AdminUser }> {
    const response = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        phone: phone.trim(),
        secret_key: secretKey.trim(),
        otp: secretKey.trim(),
        role: role || undefined,
      }),
    });

    if (!response.ok) {
      let err = 'Login failed';
      try {
        const body = await response.json();
        err = body.detail || err;
      } catch {}
      throw new Error(err);
    }

    const data = await response.json();
    setAdminToken(data.access_token);
    const user: AdminUser = {
      id: data.user.id,
      phone: data.user.phone,
      name: data.user.name,
      role: data.user.role || 'super_admin',
    };
    setStoredAdminUser(user);
    return { token: data.access_token, user };
  },

  logout(): void {
    clearAdminToken();
  },

  // Module 1: Dashboard Overview, Metrics, Alerts & Trends
  async getOverview(): Promise<AdminOverview> {
    return apiRequest<AdminOverview>('/overview');
  },

  async getCriticalAlerts(): Promise<ExceptionAlert[]> {
    return apiRequest<ExceptionAlert[]>('/alerts');
  },

  async triggerSosAlert(runnerId: string, reason: string): Promise<any> {
    return apiRequest(`/alerts/sos?runner_id=${encodeURIComponent(runnerId)}&reason=${encodeURIComponent(reason)}`, {
      method: 'POST',
    });
  },

  async resolveAlert(alertId: string, notes?: string): Promise<any> {
    return apiRequest(`/alerts/${encodeURIComponent(alertId)}/resolve`, {
      method: 'POST',
      body: JSON.stringify({ resolution_notes: notes || 'Resolved from dashboard' }),
    });
  },

  async getHourlyTrends(): Promise<HourlyTrendsData> {
    return apiRequest<HourlyTrendsData>('/dashboard/trends');
  },

  // Module 2: KYC & User Management
  async getPendingKyc(): Promise<PendingKycApplicant[]> {
    return apiRequest<PendingKycApplicant[]>('/kyc/pending');
  },

  async getKycSideBySide(type: 'vendor' | 'runner', id: string): Promise<KycSideBySideDetail> {
    return apiRequest<KycSideBySideDetail>(`/kyc/${type}/${id}`);
  },

  async approveKyc(type: 'vendor' | 'runner', id: string): Promise<{ message: string; is_approved: boolean }> {
    return apiRequest(`/kyc/${type}/${id}/approve`, { method: 'POST' });
  },

  async rejectKyc(type: 'vendor' | 'runner', id: string, reason: string): Promise<{ message: string; is_approved: boolean }> {
    return apiRequest(`/kyc/${type}/${id}/reject?reason=${encodeURIComponent(reason)}`, { method: 'POST' });
  },

  async getActiveDirectory(query?: string, role?: string): Promise<DirectoryUser[]> {
    const params = new URLSearchParams();
    if (query) params.append('query', query);
    if (role) params.append('role', role);
    return apiRequest<DirectoryUser[]>(`/users/directory?${params.toString()}`);
  },

  async toggleUserSuspension(userId: string, isActive: boolean, reason?: string): Promise<any> {
    return apiRequest(`/users/${userId}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ is_active: isActive, reason }),
    });
  },

  // Legacy vendor/runner helpers
  async getVendors(): Promise<any[]> {
    return apiRequest<any[]>('/vendors');
  },

  async getRunners(): Promise<any[]> {
    return apiRequest<any[]>('/runners');
  },

  async approveVendor(id: string): Promise<any> {
    return this.approveKyc('vendor', id);
  },

  async rejectVendor(id: string, reason: string = 'Rejected by Admin'): Promise<any> {
    return this.rejectKyc('vendor', id, reason);
  },

  async approveRunner(id: string): Promise<any> {
    return this.approveKyc('runner', id);
  },

  async rejectRunner(id: string, reason: string = 'Rejected by Admin'): Promise<any> {
    return this.rejectKyc('runner', id, reason);
  },

  // Module 3: Order Management & God Mode
  async getOrders(): Promise<OrderItemRecord[]> {
    return apiRequest<OrderItemRecord[]>('/orders');
  },

  async updateOrderStatus(orderId: string, status: string, cashCollected?: boolean): Promise<any> {
    return apiRequest(`/orders/${orderId}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ status, cash_collected: cashCollected }),
    });
  },

  async godModeCancelOrder(orderId: string, reason?: string, autoRefund: boolean = true): Promise<any> {
    return apiRequest(`/orders/${orderId}/god-mode/cancel?reason=${encodeURIComponent(reason || 'Admin Cancel')}&auto_refund=${autoRefund}`, {
      method: 'POST',
    });
  },

  async godModeIssueRefund(orderId: string, amount: number, reason?: string): Promise<any> {
    return apiRequest(`/orders/${orderId}/god-mode/refund`, {
      method: 'POST',
      body: JSON.stringify({ amount, reason: reason || 'God Mode instant refund' }),
    });
  },

  async godModeReassignRunner(orderId: string, runnerId: string, notes?: string): Promise<any> {
    return apiRequest(`/orders/${orderId}/god-mode/reassign-runner`, {
      method: 'POST',
      body: JSON.stringify({ runner_id: runnerId, notes }),
    });
  },

  async godModeOverrideStock(orderId: string, productId: string, isAvailable: boolean, priceOverride?: number): Promise<any> {
    return apiRequest(`/orders/${orderId}/god-mode/override-stock`, {
      method: 'POST',
      body: JSON.stringify({ product_id: productId, is_available: isAvailable, price_override: priceOverride }),
    });
  },

  // Module 4: Live Map Tracking & Heatmaps
  async getMapRiders(): Promise<RiderMapPin[]> {
    return apiRequest<RiderMapPin[]>('/map/riders');
  },

  async pingRiderLocation(runnerId: string, lat: number, lng: number, status: string = 'IDLE'): Promise<any> {
    return apiRequest(`/map/riders/${runnerId}/ping`, {
      method: 'POST',
      body: JSON.stringify({ latitude: lat, longitude: lng, status }),
    });
  },

  async getDemandHeatmaps(): Promise<DemandHeatmapZone[]> {
    return apiRequest<DemandHeatmapZone[]>('/map/heatmaps');
  },

  async notifyRidersToRedZone(zoneName: string, lat: number, lng: number, message?: string): Promise<any> {
    return apiRequest('/map/heatmaps/notify-riders', {
      method: 'POST',
      body: JSON.stringify({ zone_name: zoneName, latitude: lat, longitude: lng, message }),
    });
  },

  // Module 5: Financials & Ledger (Settlements)
  async getSettlements(): Promise<SettlementLedger> {
    return apiRequest<SettlementLedger>('/settlements');
  },

  async getCodReconciliation(): Promise<CodReconciliationItem[]> {
    return apiRequest<CodReconciliationItem[]>('/settlements/cod');
  },

  async recordCodDeposit(runnerId: string, amount: number, receiptReference?: string, notes?: string): Promise<any> {
    return apiRequest('/settlements/cod-deposit', {
      method: 'POST',
      body: JSON.stringify({ runner_id: runnerId, amount, receipt_reference: receiptReference, notes }),
    });
  },

  getVendorPayoutsCsvUrl(): string {
    const token = getAdminToken() || '';
    return `${API_BASE}/settlements/payouts/vendor-csv`;
  },

  getRunnerPayoutsCsvUrl(): string {
    return `${API_BASE}/settlements/payouts/runner-csv`;
  },

  async downloadVendorPayoutsCsv(): Promise<Blob> {
    const res = await fetch(`${API_BASE}/settlements/payouts/vendor-csv`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to download CSV' }));
      throw new Error(err.detail || 'Download forbidden');
    }
    return res.blob();
  },

  async downloadRunnerPayoutsCsv(): Promise<Blob> {
    const res = await fetch(`${API_BASE}/settlements/payouts/runner-csv`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to download CSV' }));
      throw new Error(err.detail || 'Download forbidden');
    }
    return res.blob();
  },

  // Module 6: Catalog & Platform Settings
  async getCatalog(): Promise<CatalogItem[]> {
    return apiRequest<CatalogItem[]>('/catalog');
  },

  async addCatalogItem(item: CatalogItem): Promise<CatalogItem> {
    return apiRequest<CatalogItem>('/catalog', {
      method: 'POST',
      body: JSON.stringify({
        name_en: item.name_en,
        name_hi: item.name_hi,
        category: item.category,
        standard_unit: item.standard_unit || item.default_unit || '1 kg',
        suggested_price: item.suggested_price || item.suggested_mrp || 50,
        image_url: item.image_url,
      }),
    });
  },

  async updateCatalogItem(id: string, item: Partial<CatalogItem>): Promise<CatalogItem> {
    return apiRequest<CatalogItem>(`/catalog/${id}`, {
      method: 'PUT',
      body: JSON.stringify(item),
    });
  },

  async deleteCatalogItem(id: string): Promise<any> {
    return apiRequest(`/catalog/${id}`, { method: 'DELETE' });
  },

  async getSettings(): Promise<PlatformSettings> {
    return apiRequest<PlatformSettings>('/settings');
  },

  async updateSettings(settings: Partial<PlatformSettings>): Promise<any> {
    return apiRequest('/settings', {
      method: 'PATCH',
      body: JSON.stringify(settings),
    });
  },

  async getPromos(): Promise<PromoCodeItem[]> {
    return apiRequest<PromoCodeItem[]>('/pricing/promos');
  },

  async createPromo(code: string, discountPct: number, minOrder: number = 99, maxDiscount: number = 100): Promise<any> {
    return apiRequest('/pricing/promos', {
      method: 'POST',
      body: JSON.stringify({
        code,
        discount_pct: discountPct,
        min_order_value: minOrder,
        max_discount: maxDiscount,
      }),
    });
  },

  // Secondary Modules: Customers, Tickets, Audit Logs, Refunds
  async getCustomers(): Promise<CustomerItem[]> {
    return apiRequest<CustomerItem[]>('/customers');
  },

  async getTickets(category?: string, status?: string): Promise<SupportTicketItem[]> {
    const params = new URLSearchParams();
    if (category) params.append('category', category);
    if (status) params.append('status', status);
    return apiRequest<SupportTicketItem[]>(`/tickets?${params.toString()}`);
  },

  async replyTicket(ticketId: string, message: string): Promise<any> {
    return apiRequest(`/tickets/${ticketId}/reply`, {
      method: 'POST',
      body: JSON.stringify({ message }),
    });
  },

  async updateTicketStatus(ticketId: string, status: 'OPEN' | 'RESOLVED' | 'CLOSED', notes?: string): Promise<any> {
    return apiRequest(`/tickets/${ticketId}`, {
      method: 'PATCH',
      body: JSON.stringify({ status, resolution_notes: notes }),
    });
  },

  async getAuditLogs(): Promise<AuditLogItem[]> {
    return apiRequest<AuditLogItem[]>('/audit-logs');
  },

  async getRefunds(): Promise<any[]> {
    return apiRequest<any[]>('/refunds');
  },

  // Real-Time WebSocket & Supabase Realtime Listener
  connectOperationsWebSocket(
    onMessage: (msg: any) => void,
    onError?: (err: any) => void
  ): () => void {
    const token = getAdminToken();
    if (!token) return () => {};

    const baseWsUrl = API_BASE.replace(/^http/, 'ws');
    const wsUrl = `${baseWsUrl}/ws?token=${encodeURIComponent(token)}`;

    let socket: WebSocket | null = null;
    let isClosedExplicitly = false;
    let supabaseChannel: any = null;

    const connect = () => {
      try {
        socket = new WebSocket(wsUrl);
        socket.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            onMessage(data);
          } catch {}
        };
        socket.onerror = (err) => {
          if (onError) onError(err);
        };
        socket.onclose = () => {
          if (!isClosedExplicitly) {
            setTimeout(connect, 4000); // Auto reconnect
          }
        };
      } catch (e) {
        if (onError) onError(e);
      }
    };

    connect();

    // Native Supabase Realtime live sync across devices
    try {
      if (typeof window !== 'undefined' && window.supabase && typeof window.supabase.createClient === 'function') {
        const sbClient = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
        supabaseChannel = sbClient
          .channel('super_admin_live_feed')
          .on('postgres_changes', { event: '*', schema: 'public', table: 'orders' }, (payload: any) => {
            onMessage({
              type: 'ORDER_STATUS_UPDATED',
              data: payload.new || payload.old || payload,
            });
          })
          .subscribe();
      }
    } catch (e) {
      console.warn('Supabase Realtime subscription notice:', e);
    }

    return () => {
      isClosedExplicitly = true;
      if (socket) {
        socket.close();
      }
      if (supabaseChannel) {
        try {
          supabaseChannel.unsubscribe();
        } catch {}
      }
    };
  },
};
