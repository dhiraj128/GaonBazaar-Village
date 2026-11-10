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
import type { Language } from '../i18n';
import { translations } from '../i18n';

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
  lang: Language;
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
  lang,
}) => {
  const t = translations[lang];
  const isHubManager = userRole === 'hub_manager';

  const primaryModules = [
    {
      id: 'dashboard' as NavTab,
      label: t.tabDashboard,
      subtitle: t.tabDashboardSub,
      icon: LayoutDashboard,
      badge: criticalAlertsCount > 0 ? `${criticalAlertsCount} SOS` : null,
      badgeColor: 'bg-rose-500 text-white animate-pulse',
    },
    {
      id: 'users' as NavTab,
      label: t.tabUsers,
      subtitle: t.tabUsersSub,
      icon: ShieldCheck,
      badge: pendingKycCount > 0 ? `${pendingKycCount}` : null,
      badgeColor: 'bg-amber-500 text-white',
    },
    {
      id: 'orders' as NavTab,
      label: t.tabOrders,
      subtitle: t.tabOrdersSub,
      icon: ShoppingBag,
      badge: activeOrdersCount > 0 ? `${activeOrdersCount}` : null,
      badgeColor: 'bg-emerald-600 text-white',
    },
    {
      id: 'map' as NavTab,
      label: t.tabMap,
      subtitle: t.tabMapSub,
      icon: MapPin,
      badge: null,
    },
    {
      id: 'financials' as NavTab,
      label: t.tabFinancials,
      subtitle: isHubManager ? (lang === 'hi' ? 'सीओडी समाधान' : 'COD Hub Reconciliation') : t.tabFinancialsSub,
      icon: CircleDollarSign,
      badge: isHubManager ? 'COD' : null,
      badgeColor: 'bg-slate-700 text-slate-200 text-[10px]',
    },
    {
      id: 'catalog' as NavTab,
      label: t.tabCatalog,
      subtitle: t.tabCatalogSub,
      icon: Package,
      badge: isHubManager ? (lang === 'hi' ? 'केवल पठन' : 'Read Only') : null,
      badgeColor: 'bg-slate-700 text-slate-300 text-[10px]',
    },
  ];

  const secondaryModules = [
    {
      id: 'tickets' as NavTab,
      label: t.tabTickets,
      icon: Headphones,
      badge: openTicketsCount > 0 ? `${openTicketsCount}` : null,
      badgeColor: 'bg-rose-500 text-white',
    },
    {
      id: 'refunds' as NavTab,
      label: t.tabRefunds,
      icon: RotateCcw,
      badge: null,
    },
    {
      id: 'audit' as NavTab,
      label: t.tabAudit,
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
                  {t.brand}
                </span>
                <span className="text-[10px] text-emerald-400 font-semibold tracking-wider uppercase block">
                  {t.panelName}
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
              {lang === 'hi' ? 'मुख्य मॉड्यूल' : 'Core Modules'}
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
                            item.badgeColor || 'bg-slate-800 text-slate-300'
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

        {/* Secondary Modules */}
        <div className="px-3 py-2 border-t border-slate-800/80">
          {!isCollapsed && (
            <p className="px-3 mb-2 text-[10px] font-bold text-slate-400 uppercase tracking-wider">
              {lang === 'hi' ? 'सहायक नियंत्रण' : 'Secondary Controls'}
            </p>
          )}
          <nav className="space-y-1">
            {secondaryModules.map((item) => {
              const Icon = item.icon;
              const isActive = currentTab === item.id;
              if (item.restrictedToSuperAdmin && isHubManager) return null;
              return (
                <button
                  key={item.id}
                  onClick={() => onSelectTab(item.id)}
                  title={isCollapsed ? item.label : undefined}
                  className={`w-full flex items-center rounded-lg transition-all text-left text-xs font-semibold ${
                    isCollapsed ? 'justify-center p-3' : 'px-3 py-2 space-x-3'
                  } ${
                    isActive
                      ? 'bg-emerald-600 text-white shadow-md'
                      : 'text-slate-400 hover:bg-slate-800/80 hover:text-slate-200'
                  }`}
                >
                  <Icon className="w-4 h-4 shrink-0" />
                  {!isCollapsed && (
                    <div className="flex-1 flex items-center justify-between min-w-0">
                      <span className="truncate">{item.label}</span>
                      {item.badge && (
                        <span
                          className={`ml-2 px-1.5 py-0.5 text-[10px] font-bold rounded-full ${
                            item.badgeColor || 'bg-slate-800 text-slate-300'
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

      {/* Footer System Status */}
      <div className="p-3 border-t border-slate-800">
        {!isCollapsed ? (
          <div className="bg-slate-950 p-2.5 rounded-xl border border-slate-800/60 flex items-center justify-between text-xs">
            <div className="flex items-center space-x-2">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <div className="text-[11px] font-bold text-slate-300">
                {lang === 'hi' ? 'सिस्टम ऑनलाइन' : 'System Online'}
              </div>
            </div>
            <span className="text-[9px] font-mono text-slate-500 font-bold uppercase">
              v2.4.0
            </span>
          </div>
        ) : (
          <div className="flex justify-center">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" title="System Online" />
          </div>
        )}
      </div>
    </aside>
  );
};
