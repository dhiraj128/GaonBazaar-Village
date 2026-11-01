import { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import type { NavTab } from './components/Sidebar';
import { Header } from './components/Header';
import { OverviewView } from './components/OverviewView';
import { VendorsView } from './components/VendorsView';
import { RunnersView } from './components/RunnersView';
import { OrdersView } from './components/OrdersView';
import { ZonesView } from './components/ZonesView';
import { CatalogView } from './components/CatalogView';
import { SettlementsView } from './components/SettlementsView';
import { adminApi } from './api';
import type {
  AdminOverview,
  StoreItem,
  RunnerItem,
  OrderItemRecord,
  CatalogItem,
  PlatformSettings,
  SettlementLedger,
} from './types';

export function App() {
  const [currentTab, setCurrentTab] = useState<NavTab>('overview');
  const [isLoading, setIsLoading] = useState(false);
  const [overview, setOverview] = useState<AdminOverview | null>(null);
  const [stores, setStores] = useState<StoreItem[]>([]);
  const [runners, setRunners] = useState<RunnerItem[]>([]);
  const [orders, setOrders] = useState<OrderItemRecord[]>([]);
  const [catalog, setCatalog] = useState<CatalogItem[]>([]);
  const [settings, setSettings] = useState<PlatformSettings | null>(null);
  const [settlements, setSettlements] = useState<SettlementLedger | null>(null);

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const [ov, st, rn, ord, cat, sett, stt] = await Promise.all([
        adminApi.getOverview(),
        adminApi.getVendors(),
        adminApi.getRunners(),
        adminApi.getOrders(),
        adminApi.getCatalog(),
        adminApi.getSettings(),
        adminApi.getSettlements(),
      ]);
      setOverview(ov);
      setStores(st);
      setRunners(rn);
      setOrders(ord);
      setCatalog(cat);
      setSettings(sett);
      setSettlements(stt);
    } catch (err) {
      console.error('Failed to fetch admin data', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

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

  const pendingVendorsCount = stores.filter((s) => !s.is_approved).length;
  const pendingRunnersCount = runners.filter((r) => !r.is_approved).length;
  const activeOrdersCount = orders.filter(
    (o) => o.status !== 'DELIVERED' && o.status !== 'CANCELLED'
  ).length;

  return (
    <div className="min-h-screen bg-slate-50 flex font-sans">
      {/* Sidebar */}
      <Sidebar
        currentTab={currentTab}
        onSelectTab={setCurrentTab}
        pendingVendorsCount={pendingVendorsCount}
        pendingRunnersCount={pendingRunnersCount}
        activeOrdersCount={activeOrdersCount}
      />

      {/* Main Content Area */}
      <div className="flex-1 ml-64 flex flex-col min-h-screen">
        <Header currentTab={currentTab} onRefresh={fetchData} isLoading={isLoading} />

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

          {currentTab === 'zones' && <ZonesView settings={settings} />}

          {currentTab === 'catalog' && (
            <CatalogView catalog={catalog} onAddItem={handleAddCatalogItem} />
          )}

          {currentTab === 'settlements' && <SettlementsView ledger={settlements} />}
        </main>
      </div>
    </div>
  );
}

export default App;
