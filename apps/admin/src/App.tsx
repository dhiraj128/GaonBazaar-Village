import React, { useState, useEffect, useCallback } from 'react';
import { Sidebar } from './components/Sidebar';
import type { NavTab } from './components/Sidebar';
import { Header } from './components/Header';
import { LoginView } from './components/LoginView';
import { DashboardView } from './components/DashboardView';
import { KycUsersView } from './components/KycUsersView';
import { OrdersGodModeView } from './components/OrdersGodModeView';
import { LiveMapView } from './components/LiveMapView';
import { FinancialsLedgerView } from './components/FinancialsLedgerView';
import { CatalogSettingsView } from './components/CatalogSettingsView';
import { TicketsView } from './components/TicketsView';
import { RefundsView } from './components/RefundsView';
import { AuditLogsView } from './components/AuditLogsView';
import { ErrorBoundary } from './components/ErrorBoundary';

import { adminApi } from './api';
import type {
  AdminOverview,
  ExceptionAlert,
  HourlyTrendsData,
  PendingKycApplicant,
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

export function App() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(() => adminApi.isAuthenticated());
  const [currentUser, setCurrentUser] = useState<AdminUser | null>(() => adminApi.getCurrentUser());
  const [currentTab, setCurrentTab] = useState<NavTab>('dashboard');
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  // Core Data States
  const [overview, setOverview] = useState<AdminOverview | null>(null);
  const [alerts, setAlerts] = useState<ExceptionAlert[]>([]);
  const [trends, setTrends] = useState<HourlyTrendsData | null>(null);
  const [pendingKyc, setPendingKyc] = useState<PendingKycApplicant[]>([]);
  const [directoryUsers, setDirectoryUsers] = useState<DirectoryUser[]>([]);
  const [orders, setOrders] = useState<OrderItemRecord[]>([]);
  const [riders, setRiders] = useState<RiderMapPin[]>([]);
  const [heatmaps, setHeatmaps] = useState<DemandHeatmapZone[]>([]);
  const [codReconciliation, setCodReconciliation] = useState<CodReconciliationItem[]>([]);
  const [settlements, setSettlements] = useState<SettlementLedger | null>(null);
  const [catalog, setCatalog] = useState<CatalogItem[]>([]);
  const [settings, setSettings] = useState<PlatformSettings | null>(null);
  const [promos, setPromos] = useState<PromoCodeItem[]>([]);
  const [tickets, setTickets] = useState<SupportTicketItem[]>([]);
  const [auditLogs, setAuditLogs] = useState<AuditLogItem[]>([]);

  const fetchAllData = useCallback(async () => {
    if (!adminApi.isAuthenticated()) return;
    setIsLoading(true);
    try {
      const [
        ov,
        al,
        tr,
        kyc,
        dir,
        ord,
        mapRiders,
        mapHeat,
        cod,
        sett,
        cat,
        settRules,
        prm,
        tck,
        logs,
      ] = await Promise.allSettled([
        adminApi.getOverview(),
        adminApi.getCriticalAlerts(),
        adminApi.getHourlyTrends(),
        adminApi.getPendingKyc(),
        adminApi.getActiveDirectory(),
        adminApi.getOrders(),
        adminApi.getMapRiders(),
        adminApi.getDemandHeatmaps(),
        adminApi.getCodReconciliation(),
        adminApi.getSettlements(),
        adminApi.getCatalog(),
        adminApi.getSettings(),
        adminApi.getPromos(),
        adminApi.getTickets(),
        adminApi.getAuditLogs(),
      ]);

      if (ov.status === 'fulfilled') setOverview(ov.value);
      if (al.status === 'fulfilled') setAlerts(al.value);
      if (tr.status === 'fulfilled') setTrends(tr.value);
      if (kyc.status === 'fulfilled') setPendingKyc(kyc.value);
      if (dir.status === 'fulfilled') setDirectoryUsers(dir.value);
      if (ord.status === 'fulfilled') setOrders(ord.value);
      if (mapRiders.status === 'fulfilled') setRiders(mapRiders.value);
      if (mapHeat.status === 'fulfilled') setHeatmaps(mapHeat.value);
      if (cod.status === 'fulfilled') setCodReconciliation(cod.value);
      if (sett.status === 'fulfilled') setSettlements(sett.value);
      if (cat.status === 'fulfilled') setCatalog(cat.value);
      if (settRules.status === 'fulfilled') setSettings(settRules.value);
      if (prm.status === 'fulfilled') setPromos(prm.value);
      if (tck.status === 'fulfilled') setTickets(tck.value);
      if (logs.status === 'fulfilled') setAuditLogs(logs.value);
    } catch (err) {
      console.error('Failed to sync admin data', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Connect to Real-Time WebSocket for Live Updates
  useEffect(() => {
    if (!isAuthenticated) return;

    fetchAllData();

    const cleanupWs = adminApi.connectOperationsWebSocket(
      (event) => {
        if (event.type === 'ORDER_STATUS_UPDATED' || event.type === 'ORDER_CANCELLED') {
          // Refresh orders feed & overview
          adminApi.getOrders().then(setOrders).catch(() => {});
          adminApi.getOverview().then(setOverview).catch(() => {});
        } else if (event.type === 'RIDER_LOCATION') {
          setRiders((prev) =>
            prev.map((r) =>
              r.runner_id === event.data.runner_id
                ? { ...r, latitude: event.data.latitude, longitude: event.data.longitude, battery_level: event.data.battery_level }
                : r
            )
          );
        } else if (event.type === 'EXCEPTION_ALERT') {
          setAlerts((prev) => [event.data, ...prev.filter((a) => a.id !== event.data.id)]);
        } else if (event.type === 'KYC_STATUS_UPDATED') {
          adminApi.getPendingKyc().then(setPendingKyc).catch(() => {});
          adminApi.getActiveDirectory().then(setDirectoryUsers).catch(() => {});
        }
      },
      (err) => {
        console.warn('WebSocket notification notice', err);
      }
    );

    // Periodic 15-second sync timer
    const interval = setInterval(fetchAllData, 15000);

    return () => {
      cleanupWs();
      clearInterval(interval);
    };
  }, [isAuthenticated, fetchAllData]);

  const handleLoginSuccess = (user: AdminUser) => {
    setCurrentUser(user);
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    adminApi.logout();
    setIsAuthenticated(false);
    setCurrentUser(null);
  };

  const handleRoleChange = (newRole: AdminRole) => {
    if (!currentUser) return;
    const updatedUser = { ...currentUser, role: newRole };
    setCurrentUser(updatedUser);
    adminApi.login(newRole === 'hub_manager' ? '9800000098' : '9800000099', '123456', newRole)
      .then((res) => {
        setCurrentUser(res.user);
        fetchAllData();
      })
      .catch(() => {});
  };

  // Module 1 Alert Handlers
  const handleResolveAlert = async (alertId: string) => {
    await adminApi.resolveAlert(alertId);
    setAlerts((prev) => prev.filter((a) => a.id !== alertId));
  };

  // Module 2 KYC Handlers
  const handleOpenSideBySide = async (type: 'vendor' | 'runner', id: string) => {
    return adminApi.getKycSideBySide(type, id);
  };

  const handleApproveKyc = async (type: 'vendor' | 'runner', id: string) => {
    await adminApi.approveKyc(type, id);
    await fetchAllData();
  };

  const handleRejectKyc = async (type: 'vendor' | 'runner', id: string, reason: string) => {
    await adminApi.rejectKyc(type, id, reason);
    await fetchAllData();
  };

  const handleToggleUserStatus = async (userId: string, isActive: boolean, reason?: string) => {
    await adminApi.toggleUserSuspension(userId, isActive, reason);
    await fetchAllData();
  };

  // Module 3 Orders God Mode Handlers
  const handleUpdateOrderStatus = async (orderId: string, status: string, cashCollected?: boolean) => {
    await adminApi.updateOrderStatus(orderId, status, cashCollected);
    await fetchAllData();
  };

  const handleGodModeCancel = async (orderId: string, reason?: string, autoRefund?: boolean) => {
    await adminApi.godModeCancelOrder(orderId, reason, autoRefund);
    await fetchAllData();
  };

  const handleGodModeRefund = async (orderId: string, amount: number, reason?: string) => {
    await adminApi.godModeIssueRefund(orderId, amount, reason);
    await fetchAllData();
  };

  const handleGodModeReassignRunner = async (orderId: string, runnerId: string, notes?: string) => {
    await adminApi.godModeReassignRunner(orderId, runnerId, notes);
    await fetchAllData();
  };

  const handleGodModeOverrideStock = async (orderId: string, productId: string, isAvailable: boolean) => {
    await adminApi.godModeOverrideStock(orderId, productId, isAvailable);
    await fetchAllData();
  };

  // Module 4 Live Map Handlers
  const handlePingRider = async (runnerId: string, lat: number, lng: number) => {
    await adminApi.pingRiderLocation(runnerId, lat, lng);
  };

  const handleNotifyRedZone = async (zoneName: string, lat: number, lng: number, message?: string) => {
    await adminApi.notifyRidersToRedZone(zoneName, lat, lng, message);
  };

  // Module 5 Financials Handlers
  const handleRecordCodDeposit = async (runnerId: string, amount: number, receiptReference?: string, notes?: string) => {
    await adminApi.recordCodDeposit(runnerId, amount, receiptReference, notes);
    await fetchAllData();
  };

  const handleDownloadVendorCsv = async () => {
    try {
      const blob = await adminApi.downloadVendorPayoutsCsv();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `gaonbazaar_vendor_payouts_${new Date().toISOString().slice(0, 10)}.csv`;
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (err: any) {
      alert(`Download failed: ${err.message}`);
    }
  };

  const handleDownloadRunnerCsv = async () => {
    try {
      const blob = await adminApi.downloadRunnerPayoutsCsv();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `gaonbazaar_runner_payouts_${new Date().toISOString().slice(0, 10)}.csv`;
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (err: any) {
      alert(`Download failed: ${err.message}`);
    }
  };

  // Module 6 Catalog & Pricing Handlers
  const handleAddCatalogItem = async (item: CatalogItem) => {
    await adminApi.addCatalogItem(item);
    await fetchAllData();
  };

  const handleDeleteCatalogItem = async (id: string) => {
    await adminApi.deleteCatalogItem(id);
    await fetchAllData();
  };

  const handleUpdateSettings = async (newSettings: Partial<PlatformSettings>) => {
    await adminApi.updateSettings(newSettings);
    await fetchAllData();
  };

  const handleCreatePromo = async (code: string, discountPct: number, minOrder: number, maxDiscount: number) => {
    await adminApi.createPromo(code, discountPct, minOrder, maxDiscount);
    await fetchAllData();
  };

  const handleUpdateTicketStatus = async (id: string, status: 'OPEN' | 'RESOLVED' | 'CLOSED', notes?: string) => {
    await adminApi.updateTicketStatus(id, status, notes);
    await fetchAllData();
  };

  if (!isAuthenticated) {
    return <LoginView onLoginSuccess={handleLoginSuccess} />;
  }

  const activeOrdersCount = orders.filter(
    (o) => o.status !== 'DELIVERED' && o.status !== 'CANCELLED'
  ).length;
  const criticalAlertsCount = alerts.filter(
    (a) => a.severity === 'CRITICAL' || a.type === 'SOS_RIDER'
  ).length;
  const openTicketsCount = tickets.filter((t) => t.status === 'OPEN').length;

  return (
    <div className="min-h-screen bg-slate-50 flex font-sans">
      {/* Sidebar (Left, Fixed, Collapsible) */}
      <Sidebar
        currentTab={currentTab}
        onSelectTab={setCurrentTab}
        pendingKycCount={pendingKyc.length}
        activeOrdersCount={activeOrdersCount}
        criticalAlertsCount={criticalAlertsCount}
        openTicketsCount={openTicketsCount}
        userRole={currentUser?.role}
        isCollapsed={isSidebarCollapsed}
        onToggleCollapse={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
      />

      {/* Main Content Area (Right, Dynamic) */}
      <div
        className={`flex-1 flex flex-col min-h-screen transition-all duration-300 ${
          isSidebarCollapsed ? 'ml-20' : 'ml-64'
        }`}
      >
        {/* Sticky Top Nav */}
        <Header
          currentTab={currentTab}
          onRefresh={fetchAllData}
          isLoading={isLoading}
          currentUser={currentUser}
          onRoleChange={handleRoleChange}
          onLogout={handleLogout}
          alerts={alerts}
          onResolveAlert={handleResolveAlert}
          isSidebarCollapsed={isSidebarCollapsed}
        />

        {/* Dynamic View Body */}
        <main className="flex-1 p-6 lg:p-8 mt-16 max-w-7xl w-full mx-auto">
          <ErrorBoundary key={currentTab} sectionTitle={currentTab}>
          {currentTab === 'dashboard' && (
            <DashboardView
              overview={overview}
              alerts={alerts}
              trends={trends}
              onNavigate={setCurrentTab}
              onResolveAlert={handleResolveAlert}
            />
          )}

          {currentTab === 'users' && (
            <KycUsersView
              pendingApplicants={pendingKyc}
              directoryUsers={directoryUsers}
              onOpenSideBySide={handleOpenSideBySide}
              onApprove={handleApproveKyc}
              onReject={handleRejectKyc}
              onToggleUserStatus={handleToggleUserStatus}
            />
          )}

          {currentTab === 'orders' && (
            <OrdersGodModeView
              orders={orders}
              riders={riders}
              onUpdateStatus={handleUpdateOrderStatus}
              onGodModeCancel={handleGodModeCancel}
              onGodModeRefund={handleGodModeRefund}
              onGodModeReassignRunner={handleGodModeReassignRunner}
              onGodModeOverrideStock={handleGodModeOverrideStock}
            />
          )}

          {currentTab === 'map' && (
            <LiveMapView
              riders={riders}
              heatmaps={heatmaps}
              onPingRider={handlePingRider}
              onNotifyRedZone={handleNotifyRedZone}
              onRefresh={fetchAllData}
            />
          )}

          {currentTab === 'financials' && (
            <FinancialsLedgerView
              ledger={settlements}
              codItems={codReconciliation}
              userRole={currentUser?.role}
              onRecordCodDeposit={handleRecordCodDeposit}
              onDownloadVendorCsv={handleDownloadVendorCsv}
              onDownloadRunnerCsv={handleDownloadRunnerCsv}
            />
          )}

          {currentTab === 'catalog' && (
            <CatalogSettingsView
              catalog={catalog}
              settings={settings}
              promos={promos}
              userRole={currentUser?.role}
              onAddCatalogItem={handleAddCatalogItem}
              onDeleteCatalogItem={handleDeleteCatalogItem}
              onUpdateSettings={handleUpdateSettings}
              onCreatePromo={handleCreatePromo}
            />
          )}

          {currentTab === 'tickets' && (
            <TicketsView tickets={tickets} onUpdateStatus={handleUpdateTicketStatus} />
          )}

          {currentTab === 'refunds' && <RefundsView />}

          {currentTab === 'audit' && <AuditLogsView logs={auditLogs} />}
          </ErrorBoundary>
        </main>
      </div>
    </div>
  );
}

export default App;
