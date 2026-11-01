import React from 'react';
import {
  LayoutDashboard,
  Store,
  Bike,
  ShoppingBag,
  MapPin,
  Package,
  CircleDollarSign,
  ShieldCheck,
} from 'lucide-react';

export type NavTab =
  | 'overview'
  | 'vendors'
  | 'runners'
  | 'orders'
  | 'zones'
  | 'catalog'
  | 'settlements';

interface SidebarProps {
  currentTab: NavTab;
  onSelectTab: (tab: NavTab) => void;
  pendingVendorsCount: number;
  pendingRunnersCount: number;
  activeOrdersCount: number;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentTab,
  onSelectTab,
  pendingVendorsCount,
  pendingRunnersCount,
  activeOrdersCount,
}) => {
  const navItems = [
    {
      id: 'overview' as NavTab,
      label: 'Dashboard Overview',
      icon: LayoutDashboard,
      badge: null,
    },
    {
      id: 'vendors' as NavTab,
      label: 'Vendor Approvals',
      icon: Store,
      badge: pendingVendorsCount > 0 ? `${pendingVendorsCount} New` : null,
      badgeColor: 'bg-amber-500 text-white',
    },
    {
      id: 'runners' as NavTab,
      label: 'Runner Fleet',
      icon: Bike,
      badge: pendingRunnersCount > 0 ? `${pendingRunnersCount} New` : null,
      badgeColor: 'bg-amber-500 text-white',
    },
    {
      id: 'orders' as NavTab,
      label: 'Live Orders',
      icon: ShoppingBag,
      badge: activeOrdersCount > 0 ? `${activeOrdersCount}` : null,
      badgeColor: 'bg-emerald-600 text-white',
    },
    {
      id: 'zones' as NavTab,
      label: 'Zones & Pricing Rules',
      icon: MapPin,
      badge: null,
    },
    {
      id: 'catalog' as NavTab,
      label: 'Master Product Library',
      icon: Package,
      badge: null,
    },
    {
      id: 'settlements' as NavTab,
      label: 'Settlements & Finance',
      icon: CircleDollarSign,
      badge: null,
    },
  ];

  return (
    <aside className="w-64 bg-slate-900 text-slate-100 flex flex-col h-screen fixed left-0 top-0 z-30 shadow-xl border-r border-slate-800">
      {/* Brand Header */}
      <div className="p-5 border-b border-slate-800 flex items-center space-x-3">
        <div className="w-10 h-10 rounded-xl bg-emerald-600 flex items-center justify-center text-white shadow-md shadow-emerald-900/30">
          <ShieldCheck className="w-6 h-6" />
        </div>
        <div>
          <div className="font-extrabold text-lg tracking-tight text-white flex items-center gap-1.5">
            Gaon<span className="text-emerald-400">Bazaar</span>
          </div>
          <div className="text-[11px] font-semibold text-emerald-400 tracking-wider uppercase">
            Super Admin Portal
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectTab(item.id)}
              className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-emerald-600 text-white shadow-sm shadow-emerald-900/40'
                  : 'text-slate-300 hover:bg-slate-800/80 hover:text-white'
              }`}
            >
              <div className="flex items-center space-x-3">
                <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </div>
              {item.badge && (
                <span
                  className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${item.badgeColor || 'bg-slate-700 text-slate-300'}`}
                >
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Pilot Zone Status Card */}
      <div className="p-4 border-t border-slate-800 bg-slate-950/50">
        <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1">
          Active Pilot Block
        </div>
        <div className="text-xs font-bold text-white flex items-center gap-1">
          <MapPin className="w-3.5 h-3.5 text-emerald-400" />
          Minapur, Muzaffarpur (Bihar)
        </div>
        <div className="mt-2 text-[11px] text-slate-400 flex flex-col gap-0.5">
          <span>• Max Radius: <b className="text-emerald-400">8.0 km</b></span>
          <span>• Platform Fee: <b className="text-emerald-400">₹3.00</b></span>
          <span>• Vendor Comm: <b className="text-emerald-400">0.0%</b></span>
        </div>
      </div>
    </aside>
  );
};
