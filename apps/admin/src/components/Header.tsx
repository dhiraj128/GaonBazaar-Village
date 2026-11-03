import { RefreshCw, MapPin } from 'lucide-react';
import type { NavTab } from './Sidebar';

interface HeaderProps {
  currentTab: NavTab;
  onRefresh: () => void;
  isLoading: boolean;
  onLogout?: () => void;
}

export const Header: React.FC<HeaderProps> = ({ currentTab, onRefresh, isLoading, onLogout }) => {
  const getTabTitle = (tab: NavTab) => {
    switch (tab) {
      case 'overview':
        return 'System Overview & Executive Dashboard';
      case 'vendors':
        return 'Vendor Verification & Kirana Management';
      case 'runners':
        return 'Delivery Runner Fleet & KYC Verification';
      case 'orders':
        return 'Live Hyperlocal Order Operations';
      case 'zones':
        return 'Service Geofencing & Rural Pricing Rules';
      case 'catalog':
        return 'Master Centralized Product Library';
      case 'settlements':
        return 'Settlements, Subtotal Payouts & Platform Fee';
      default:
        return 'Super Admin Portal';
    }
  };

  return (
    <header className="h-16 bg-white border-b border-slate-200 fixed top-0 right-0 left-64 z-20 px-8 flex items-center justify-between shadow-sm">
      <div className="flex items-center space-x-4">
        <h1 className="text-lg font-bold text-slate-800">{getTabTitle(currentTab)}</h1>
        <span className="hidden lg:inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
          <MapPin className="w-3.5 h-3.5 text-emerald-600" />
          Rural Operations Zone Active
        </span>
      </div>

      <div className="flex items-center space-x-4">
        <button
          onClick={onRefresh}
          disabled={isLoading}
          className="flex items-center space-x-1.5 px-3 py-1.5 text-xs font-semibold text-slate-600 hover:text-slate-900 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors border border-slate-200"
          title="Refresh Data"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
          <span>Sync</span>
        </button>

        <div className="flex items-center space-x-3 border-l pl-4 border-slate-200">
          <div className="w-8 h-8 rounded-full bg-slate-800 text-white flex items-center justify-center font-bold text-xs">
            SA
          </div>
          <div className="hidden sm:block text-left">
            <div className="text-xs font-bold text-slate-800">Super Admin</div>
            <div className="text-[10px] text-slate-500">Muzaffarpur Operations</div>
          </div>
          {onLogout && (
            <button
              onClick={onLogout}
              className="ml-2 px-2.5 py-1 text-xs font-semibold text-rose-700 bg-rose-50 hover:bg-rose-100 rounded border border-rose-200 transition-colors"
              title="Sign Out"
            >
              लॉग आउट
            </button>
          )}
        </div>
      </div>
    </header>
  );
};
