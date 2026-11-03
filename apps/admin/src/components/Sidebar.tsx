import React from 'react';
import {
  LayoutDashboard,
  ShieldCheck,
  ShoppingBag,
  MapPin,
  CircleDollarSign,
  Package,
  Headphones,
  FileText,
  ChevronLeft,
  ChevronRight,
  RotateCcw,
} from 'lucide-react';
import type { AdminRole } from '../types';

export type NavTab =
  | 'dashboard'
  | 'users'
  | 'orders'
  | 'map'
  | 'financials'
  | 'catalog'
  | 'tickets'
  | 'refunds'
  | 'audit';

interface SidebarProps {
  currentTab: NavTab;
  onSelectTab: (tab: NavTab) => void;
  pendingKycCount: number;
  activeOrdersCount: number;
  criticalAlertsCount: number;
  openTicketsCount?: number;
  userRole?: AdminRole;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentTab,
  onSelectTab,
  pendingKycCount,
  activeOrdersCount,
  criticalAlertsCount,
  openTicketsCount = 0,
  userRole = 'super_admin',
  isCollapsed,
  onToggleCollapse,
}) => {
  const isHubManager = userRole === 'hub_manager';

  const primaryModules = [
    {
      id: 'dashboard' as NavTab,
      label: 'Dashboard',
      subtitle: 'Overview & Critical Alerts',
      icon: LayoutDashboard,
      badge: criticalAlertsCount > 0 ? `${criticalAlertsCount} SOS` : null,
      badgeColor: 'bg-rose-500 text-white animate-pulse',
    },
    {
      id: 'users' as NavTab,
      label: 'Users & KYC',
      subtitle: 'Pending Approvals & Directory',
      icon: ShieldCheck,
      badge: pendingKycCount > 0 ? `${pendingKycCount} New` : null,
      badgeColor: 'bg-amber-500 text-white',
    },
    {
      id: 'orders' as NavTab,
      label: 'Orders (God Mode)',
      subtitle: 'Real-Time WebSocket Feed',
      icon: ShoppingBag,
      badge: activeOrdersCount > 0 ? `${activeOrdersCount}` : null,
      badgeColor: 'bg-emerald-600 text-white',
    },
    {
      id: 'map' as NavTab,
      label: 'Live Operations Map',
      subtitle: 'Rider GPS & Heatmaps',
      icon: MapPin,
      badge: null,
    },
    {
      id: 'financials' as NavTab,
      label: 'Financials & Ledger',
      subtitle: isHubManager ? 'COD Hub Reconciliation' : 'COD & Batch Payouts CSV',
      icon: CircleDollarSign,
      badge: isHubManager ? 'COD Only' : null,
      badgeColor: 'bg-slate-700 text-slate-200 text-[10px]',
    },
    {
      id: 'catalog' as NavTab,
      label: 'Catalog & Settings',
      subtitle: 'Master MRP & Pricing Rules',
      icon: Package,
      badge: isHubManager ? 'Read Only' : null,
      badgeColor: 'bg-slate-700 text-slate-300 text-[10px]',
    },
  ];

  const secondaryModules = [
    {
      id: 'tickets' as NavTab,
      label: 'Support Tickets',
      icon: Headphones,
      badge: openTicketsCount > 0 ? `${openTicketsCount}` : null,
      badgeColor: 'bg-rose-500 text-white',
    },
    {
      id: 'refunds' as NavTab,
      label: 'Refunds Ledger',
      icon: RotateCcw,
      badge: null,
    },
    {
      id: 'audit' as NavTab,
      label: 'Security Audit Logs',
      icon: FileText,
      badge: null,
      restrictedToSuperAdmin: true,
    },
  ];

  return (
    <aside
      className={`fixed top-0 bottom-0 left-0 bg-slate-900 border-r border-slate-800 z-30 transition-all duration-300 flex flex-col justify-between ${
        isCollapsed ? 'w-20' : 'w-64'
      }`}
    >
      <div>
        {/* Brand Header */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-slate-800">
          {!isCollapsed && (
            <div className="flex items-center space-x-2.5">
              <div className="w-8 h-8 rounded-lg bg-emerald-600 text-white flex items-center justify-center font-black text-base shadow-sm">
                GB
              </div>
              <div>
                <span className="font-extrabold text-sm tracking-wide text-white block">
                  गांवबाज़ार
                </span>
                <span className="text-[10px] text-emerald-400 font-semibold tracking-wider uppercase block">
                  Super Admin Panel
                </span>
              </div>
            </div>
          )}
          {isCollapsed && (
            <div className="w-8 h-8 mx-auto rounded-lg bg-emerald-600 text-white flex items-center justify-center font-black text-sm">
              GB
            </div>
          )}

          <button
            onClick={onToggleCollapse}
            className="text-slate-400 hover:text-white p-1 rounded hover:bg-slate-800 transition"
            title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {isCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </button>
        </div>

        {/* Primary 6 Core Modules */}
        <div className="px-3 py-3">
          {!isCollapsed && (
            <p className="px-3 mb-2 text-[10px] font-bold text-slate-400 uppercase tracking-wider">
              Core Modules
            </p>
          )}
          <nav className="space-y-1">
            {primaryModules.map((item) => {
              const Icon = item.icon;
              const isActive = currentTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => onSelectTab(item.id)}
                  title={isCollapsed ? item.label : undefined}
                  className={`w-full flex items-center rounded-lg transition-all text-left text-xs font-semibold ${
                    isCollapsed ? 'justify-center p-3' : 'px-3 py-2.5 space-x-3'
                  } ${
                    isActive
                      ? 'bg-emerald-600 text-white shadow-md shadow-emerald-950/40'
                      : 'text-slate-300 hover:bg-slate-800/80 hover:text-white'
                  }`}
                >
                  <Icon className={`w-4 h-4 shrink-0 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                  {!isCollapsed && (
                    <div className="flex-1 flex items-center justify-between min-w-0">
                      <div className="truncate">
                        <div className="truncate leading-tight">{item.label}</div>
                        <div className={`text-[10px] truncate ${isActive ? 'text-emerald-100' : 'text-slate-400'}`}>
                          {item.subtitle}
                        </div>
                      </div>
                      {item.badge && (
                        <span
                          className={`ml-2 px-1.5 py-0.5 text-[10px] font-bold rounded-full ${
                            item.badgeColor || 'bg-slate-800 text-white'
                          }`}
                        >
                          {item.badge}
                        </span>
                      )}
                    </div>
                  )}
                </button>
              );
            })}
          </nav>

          {/* Secondary Operational Modules */}
          {!isCollapsed && (
            <p className="px-3 mt-4 mb-2 text-[10px] font-bold text-slate-400 uppercase tracking-wider">
              Operations & Audit
            </p>
          )}
          <nav className="space-y-1 mt-1">
            {secondaryModules.map((item) => {
              if (item.restrictedToSuperAdmin && isHubManager) return null;
              const Icon = item.icon;
              const isActive = currentTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => onSelectTab(item.id)}
                  title={isCollapsed ? item.label : undefined}
                  className={`w-full flex items-center rounded-lg transition-all text-left text-xs font-semibold ${
                    isCollapsed ? 'justify-center p-3' : 'px-3 py-2 space-x-3'
                  } ${
                    isActive
                      ? 'bg-emerald-600 text-white shadow'
                      : 'text-slate-400 hover:bg-slate-800/70 hover:text-white'
                  }`}
                >
                  <Icon className={`w-4 h-4 shrink-0 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                  {!isCollapsed && (
                    <div className="flex-1 flex items-center justify-between min-w-0">
                      <span className="truncate">{item.label}</span>
                      {item.badge && (
                        <span
                          className={`ml-2 px-1.5 py-0.5 text-[10px] font-bold rounded-full ${
                            item.badgeColor || 'bg-slate-800 text-white'
                          }`}
                        >
                          {item.badge}
                        </span>
                      )}
                    </div>
                  )}
                </button>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Role Footer */}
      <div className="p-3 border-t border-slate-800 bg-slate-950/60">
        {!isCollapsed ? (
          <div className="flex items-center space-x-2.5">
            <div className={`w-7 h-7 rounded-full flex items-center justify-center font-bold text-xs text-white ${isHubManager ? 'bg-amber-600' : 'bg-emerald-600'}`}>
              {isHubManager ? 'HM' : 'SA'}
            </div>
            <div className="min-w-0 flex-1">
              <div className="text-xs font-bold text-white truncate">
                {isHubManager ? 'Hub Manager' : 'Super Admin'}
              </div>
              <div className="text-[10px] text-slate-400 truncate">
                Minapur Central Hub
              </div>
            </div>
          </div>
        ) : (
          <div className={`w-7 h-7 mx-auto rounded-full flex items-center justify-center font-bold text-xs text-white ${isHubManager ? 'bg-amber-600' : 'bg-emerald-600'}`}>
            {isHubManager ? 'HM' : 'SA'}
          </div>
        )}
      </div>
    </aside>
  );
};
