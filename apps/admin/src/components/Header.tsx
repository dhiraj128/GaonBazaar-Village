import React, { useState } from 'react';
import {
  Search,
  Bell,
  RefreshCw,
  AlertTriangle,
  Radio,
  ChevronDown,
  X,
  PhoneCall,
  ExternalLink,
} from 'lucide-react';
import type { NavTab } from './Sidebar';
import type { AdminRole, ExceptionAlert, AdminUser } from '../types';

interface HeaderProps {
  currentTab: NavTab;
  onRefresh: () => void;
  isLoading: boolean;
  currentUser: AdminUser | null;
  onRoleChange: (newRole: AdminRole) => void;
  onLogout: () => void;
  alerts: ExceptionAlert[];
  onResolveAlert: (alertId: string) => void;
  onSearchSelect?: (result: any) => void;
  isSidebarCollapsed: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  currentTab,
  onRefresh,
  isLoading,
  currentUser,
  onRoleChange,
  onLogout,
  alerts,
  onResolveAlert,
  isSidebarCollapsed,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [showAlertCenter, setShowAlertCenter] = useState(false);
  const [showRoleDropdown, setShowRoleDropdown] = useState(false);

  const getTabTitle = (tab: NavTab) => {
    switch (tab) {
      case 'dashboard':
        return 'Executive Command Center & Real-Time Pulse';
      case 'users':
        return 'KYC Gatekeeper & User Directory';
      case 'orders':
        return 'Live Hyperlocal Order Feed & God Mode';
      case 'map':
        return 'Live Operations District Map & Fleet Tracking';
      case 'financials':
        return 'Settlements, Hub COD & Corporate Payouts';
      case 'catalog':
        return 'Master Product Catalog & Pricing Engine';
      case 'tickets':
        return 'Rural Support & Dispute Resolution';
      case 'refunds':
        return 'Gateway Refunds & Replacements Audit';
      case 'audit':
        return 'Immutable Platform Audit Trail';
      default:
        return 'GaonBazaar Operations';
    }
  };

  const criticalCount = alerts.filter(
    (a) => a.severity === 'CRITICAL' || a.type === 'SOS_RIDER'
  ).length;

  return (
    <header
      className={`h-16 bg-white border-b border-slate-200 fixed top-0 right-0 z-20 px-6 flex items-center justify-between shadow-xs transition-all duration-300 ${
        isSidebarCollapsed ? 'left-20' : 'left-64'
      }`}
    >
      {/* Left: Tab Title & Global Search */}
      <div className="flex items-center space-x-6 flex-1 max-w-2xl">
        <div className="hidden xl:block min-w-max">
          <h1 className="text-sm font-bold text-slate-800">{getTabTitle(currentTab)}</h1>
          <span className="text-[11px] text-slate-500 flex items-center gap-1.5 font-medium">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
            Minapur Pilot District Live
          </span>
        </div>

        {/* Global Search Bar (Order ID, Phone, Name) */}
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Global search by Order ID, Phone (+91), or Partner name..."
            className="w-full bg-slate-100 hover:bg-slate-50 focus:bg-white text-xs pl-9 pr-8 py-2 rounded-lg border border-slate-200 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 outline-none text-slate-800 placeholder-slate-400 transition"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-2.5 top-2.5 text-slate-400 hover:text-slate-600"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>

      {/* Right: Actions, Alert Center, Role Selector, User Profile */}
      <div className="flex items-center space-x-3">
        {/* Sync Button */}
        <button
          onClick={onRefresh}
          disabled={isLoading}
          className="flex items-center space-x-1.5 px-3 py-1.5 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg transition border border-slate-200"
          title="Sync Real-Time Data"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin text-emerald-600' : ''}`} />
          <span className="hidden md:inline">Sync</span>
        </button>

        {/* Ringing Bell Live Alert Center */}
        <div className="relative">
          <button
            onClick={() => setShowAlertCenter(!showAlertCenter)}
            className={`relative p-2 rounded-lg transition border ${
              criticalCount > 0
                ? 'bg-rose-50 text-rose-600 border-rose-200 animate-bounce'
                : 'bg-slate-100 text-slate-700 hover:bg-slate-200 border-slate-200'
            }`}
            title="Live Alert Center (SOS / Delay / Exceptions)"
          >
            <Bell className="w-4 h-4" />
            {alerts.length > 0 && (
              <span
                className={`absolute -top-1 -right-1 text-[10px] font-black w-4 h-4 rounded-full flex items-center justify-center text-white ${
                  criticalCount > 0 ? 'bg-rose-600' : 'bg-amber-500'
                }`}
              >
                {alerts.length}
              </span>
            )}
          </button>

          {/* Alert Center Dropdown Drawer */}
          {showAlertCenter && (
            <div className="absolute right-0 mt-2 w-96 bg-white rounded-xl shadow-2xl border border-slate-200 z-50 overflow-hidden animate-in fade-in slide-in-from-top-2 duration-150">
              <div className="bg-slate-900 px-4 py-3 flex items-center justify-between text-white">
                <div className="flex items-center space-x-2">
                  <Radio className="w-4 h-4 text-rose-500 animate-pulse" />
                  <span className="font-bold text-xs">Live Exception Alerts ({alerts.length})</span>
                </div>
                <button
                  onClick={() => setShowAlertCenter(false)}
                  className="text-slate-400 hover:text-white"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              <div className="max-h-96 overflow-y-auto divide-y divide-slate-100">
                {alerts.length === 0 ? (
                  <div className="p-6 text-center text-slate-400 text-xs">
                    <AlertTriangle className="w-8 h-8 text-emerald-500 mx-auto mb-2 opacity-60" />
                    All operational systems normal. Zero active exceptions.
                  </div>
                ) : (
                  alerts.map((item) => (
                    <div
                      key={item.id}
                      className={`p-3.5 transition ${
                        item.type === 'SOS_RIDER'
                          ? 'bg-rose-50/60'
                          : item.type === 'ORDER_DELAYED'
                          ? 'bg-amber-50/60'
                          : 'bg-white'
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex items-center space-x-1.5">
                          <span
                            className={`px-1.5 py-0.5 text-[9px] font-extrabold rounded ${
                              item.type === 'SOS_RIDER'
                                ? 'bg-rose-600 text-white animate-pulse'
                                : item.type === 'ORDER_DELAYED'
                                ? 'bg-amber-600 text-white'
                                : 'bg-slate-700 text-white'
                            }`}
                          >
                            {item.type}
                          </span>
                          <span className="text-[11px] font-bold text-slate-900 truncate">
                            {item.title}
                          </span>
                        </div>
                        <span className="text-[10px] text-slate-400 whitespace-nowrap">
                          {item.elapsed_minutes ? `${item.elapsed_minutes}m ago` : 'Live'}
                        </span>
                      </div>
                      <p className="text-xs text-slate-600 mt-1 leading-snug">
                        {item.description}
                      </p>

                      <div className="mt-2.5 flex items-center justify-between gap-2">
                        {item.type === 'SOS_RIDER' ? (
                          <div className="flex items-center gap-1.5">
                            <button
                              onClick={() => {
                                onResolveAlert(item.id);
                                window.alert(`Emergency support team dispatched for rider ${item.runner_name || ''}!`);
                              }}
                              className="px-2 py-1 text-[10px] font-bold bg-rose-600 hover:bg-rose-700 text-white rounded shadow-xs"
                            >
                              Dispatch Support
                            </button>
                            <button
                              onClick={() => window.alert(`Calling rider emergency contact...`)}
                              className="px-2 py-1 text-[10px] font-bold bg-slate-800 hover:bg-slate-900 text-white rounded flex items-center gap-1"
                            >
                              <PhoneCall className="w-3 h-3" /> Call
                            </button>
                          </div>
                        ) : item.type === 'ORDER_DELAYED' ? (
                          <div className="flex items-center gap-1.5">
                            <button
                              onClick={() => {
                                onResolveAlert(item.id);
                                window.alert(`Rerouting runner for order ${item.order_id}!`);
                              }}
                              className="px-2 py-1 text-[10px] font-bold bg-amber-600 hover:bg-amber-700 text-white rounded"
                            >
                              Reroute Runner
                            </button>
                          </div>
                        ) : (
                          <div className="flex items-center gap-1.5">
                            <button
                              onClick={() => {
                                onResolveAlert(item.id);
                                window.alert(`Store alerted via priority call!`);
                              }}
                              className="px-2 py-1 text-[10px] font-bold bg-slate-800 hover:bg-slate-900 text-white rounded"
                            >
                              Call Store
                            </button>
                          </div>
                        )}

                        <button
                          onClick={() => onResolveAlert(item.id)}
                          className="text-[10px] text-slate-500 hover:text-slate-800 font-medium underline"
                        >
                          Dismiss
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        {/* Role Pill & Switcher */}
        <div className="relative">
          <button
            onClick={() => setShowRoleDropdown(!showRoleDropdown)}
            className={`flex items-center space-x-1 px-2.5 py-1.5 rounded-lg text-xs font-bold transition border ${
              currentUser?.role === 'hub_manager'
                ? 'bg-amber-50 text-amber-800 border-amber-300'
                : 'bg-emerald-50 text-emerald-800 border-emerald-300'
            }`}
            title="Current RBAC Role (Click to switch view)"
          >
            <span>{currentUser?.role === 'hub_manager' ? 'Hub Manager' : 'Super Admin'}</span>
            <ChevronDown className="w-3 h-3 text-slate-500" />
          </button>

          {showRoleDropdown && (
            <div className="absolute right-0 mt-2 w-48 bg-white rounded-xl shadow-lg border border-slate-200 z-50 py-1 text-xs">
              <div className="px-3 py-1.5 font-bold text-slate-400 text-[10px] uppercase">
                Switch Admin Tier
              </div>
              <button
                onClick={() => {
                  onRoleChange('super_admin');
                  setShowRoleDropdown(false);
                }}
                className={`w-full text-left px-3 py-2 flex items-center justify-between hover:bg-slate-50 ${
                  currentUser?.role !== 'hub_manager' ? 'font-bold text-emerald-700' : 'text-slate-700'
                }`}
              >
                <span>Super Admin (Full Access)</span>
                {currentUser?.role !== 'hub_manager' && <span className="text-emerald-600">✓</span>}
              </button>
              <button
                onClick={() => {
                  onRoleChange('hub_manager');
                  setShowRoleDropdown(false);
                }}
                className={`w-full text-left px-3 py-2 flex items-center justify-between hover:bg-slate-50 ${
                  currentUser?.role === 'hub_manager' ? 'font-bold text-amber-700' : 'text-slate-700'
                }`}
              >
                <span>Hub Manager (Restricted)</span>
                {currentUser?.role === 'hub_manager' && <span className="text-amber-600">✓</span>}
              </button>
            </div>
          )}
        </div>

        {/* User Avatar & Logout */}
        <div className="flex items-center space-x-2 pl-2 border-l border-slate-200">
          <div className="w-8 h-8 rounded-full bg-slate-900 text-white flex items-center justify-center font-bold text-xs shadow-xs">
            {currentUser?.role === 'hub_manager' ? 'HM' : 'SA'}
          </div>
          <button
            onClick={onLogout}
            className="px-2.5 py-1 text-xs font-semibold text-rose-700 bg-rose-50 hover:bg-rose-100 rounded-md border border-rose-200 transition"
            title="Sign Out"
          >
            लॉग आउट
          </button>
        </div>
      </div>
    </header>
  );
};
