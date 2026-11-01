import { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import type { NavTab } from './components/Sidebar';
import { Header } from './components/Header';
import { LoginView } from './components/LoginView';
import { OverviewView } from './components/OverviewView';
import { VendorsView } from './components/VendorsView';
import { RunnersView } from './components/RunnersView';
import { OrdersView } from './components/OrdersView';
import { ZonesView } from './components/ZonesView';
import { CatalogView } from './components/CatalogView';
import { SettlementsView } from './components/SettlementsView';
import { CustomersView } from './components/CustomersView';
import { TicketsView } from './components/TicketsView';
import { AuditLogsView } from './components/AuditLogsView';
import { adminApi } from './api';
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

export function App() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(() => adminApi.isAuthenticated());
  const [currentTab, setCurrentTab] = useState<NavTab>('overview');
  const [isLoading, setIsLoading] = useState(false);
  const [overview, setOverview] = useState<AdminOverview | null>(null);
  const [stores, setStores] = useState<StoreItem[]>([]);
  const [runners, setRunners] = useState<RunnerItem[]>([]);
  const [orders, setOrders] = useState<OrderItemRecord[]>([]);
  const [catalog, setCatalog] = useState<CatalogItem[]>([]);
  const [settings, setSettings] = useState<PlatformSettings | null>(null);
  const [settlements, setSettlements] = useState<SettlementLedger | null>(null);
  const [customers, setCustomers] = useState<CustomerItem[]>([]);
  const [tickets, setTickets] = useState<SupportTicketItem[]>([]);
  const [auditLogs, setAuditLogs] = useState<AuditLogItem[]>([]);

  const fetchData = async () => {
    if (!adminApi.isAuthenticated()) return;
    setIsLoading(true);
    try {
      const [ov, st, rn, ord, cat, sett, stt, cust, tck, logs] = await Promise.all([
        adminApi.getOverview(),
        adminApi.getVendors(),
        adminApi.getRunners(),
        adminApi.getOrders(),
        adminApi.getCatalog(),
        adminApi.getSettings(),
        adminApi.getSettlements(),
        adminApi.getCustomers(),
        adminApi.getTickets(),
        adminApi.getAuditLogs(),
      ]);
      setOverview(ov);
      setStores(st);
      setRunners(rn);
      setOrders(ord);
      setCatalog(cat);
      setSettings(sett);
      setSettlements(stt);
      setCustomers(cust);
      setTickets(tck);
      setAuditLogs(logs);
    } catch (err) {
      console.error('Failed to fetch admin data', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (isAuthenticated) {
      fetchData();
    }
  }, [isAuthenticated]);

  const handleLogout = () => {
    adminApi.logout();
    setIsAuthenticated(false);
  };

  if (!isAuthenticated) {
    return <LoginView onLoginSuccess={() => setIsAuthenticated(true)} />;
  }

  const handleApproveVendor = async (id: string) => {
    await adminApi.approveVendor(id);
    await fetchData();
  };

  const handleRejectVendor = async (id: string) => {
    await adminApi.rejectVendor(id);
    await fetchData();
  };

  const handleApproveRunner = async (id: string) => {
    await adminApi.approveRunner(id);
    await fetchData();
  };

  const handleRejectRunner = async (id: string) => {
    await adminApi.rejectRunner(id);
    await fetchData();
  };

  const handleUpdateOrderStatus = async (id: string, status: OrderItemRecord['status']) => {
    await adminApi.updateOrderStatus(id, status);
    await fetchData();
  };

  const handleAddCatalogItem = async (item: CatalogItem) => {
    await adminApi.addCatalogItem(item);
    await fetchData();
  };

  const handleUpdateTicketStatus = async (id: string, status: 'OPEN' | 'RESOLVED' | 'CLOSED') => {
    await adminApi.updateTicketStatus(id, status);
    await fetchData();
  };

  const pendingVendorsCount = stores.filter((s) => !s.is_approved).length;
  const pendingRunnersCount = runners.filter((r) => !r.is_approved).length;
  const activeOrdersCount = orders.filter(
    (o) => o.status !== 'DELIVERED' && o.status !== 'CANCELLED'
  ).length;
  const openTicketsCount = tickets.filter((t) => t.status === 'OPEN').length;

  return (
    <div className="min-h-screen bg-slate-50 flex font-sans">
      {/* Sidebar */}
      <Sidebar
        currentTab={currentTab}
        onSelectTab={setCurrentTab}
        pendingVendorsCount={pendingVendorsCount}
        pendingRunnersCount={pendingRunnersCount}
        activeOrdersCount={activeOrdersCount}
        openTicketsCount={openTicketsCount}
      />

      {/* Main Content Area */}
      <div className="flex-1 ml-64 flex flex-col min-h-screen">
        <Header currentTab={currentTab} onRefresh={fetchData} isLoading={isLoading} onLogout={handleLogout} />

        <main className="flex-1 p-8 mt-16 max-w-7xl w-full">
          {currentTab === 'overview' && (
            <OverviewView
              overview={overview}
              recentOrders={orders}
              onNavigate={setCurrentTab}
            />
          )}

          {currentTab === 'vendors' && (
            <VendorsView
              stores={stores}
              onApprove={handleApproveVendor}
              onReject={handleRejectVendor}
            />
          )}

          {currentTab === 'runners' && (
            <RunnersView
              runners={runners}
              onApprove={handleApproveRunner}
              onReject={handleRejectRunner}
            />
          )}

          {currentTab === 'orders' && (
            <OrdersView orders={orders} onUpdateStatus={handleUpdateOrderStatus} />
          )}

          {currentTab === 'customers' && <CustomersView customers={customers} />}

          {currentTab === 'tickets' && (
            <TicketsView tickets={tickets} onUpdateStatus={handleUpdateTicketStatus} />
          )}

          {currentTab === 'zones' && <ZonesView settings={settings} />}

          {currentTab === 'catalog' && (
            <CatalogView catalog={catalog} onAddItem={handleAddCatalogItem} />
          )}

          {currentTab === 'settlements' && <SettlementsView ledger={settlements} />}

          {currentTab === 'audit' && <AuditLogsView logs={auditLogs} />}
        </main>
      </div>
    </div>
  );
}

export default App;
