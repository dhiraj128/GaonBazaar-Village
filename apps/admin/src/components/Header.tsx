import React, { useState } from 'react';
import {
  Search,
  Bell,
  RefreshCw,
  AlertTriangle,
  Radio,
  X,
  PhoneCall,
  ExternalLink,
  Languages,
  ShieldCheck,
} from 'lucide-react';
import type { NavTab } from './Sidebar';
import type { ExceptionAlert, AdminUser } from '../types';
import type { Language } from '../i18n';
import { translations } from '../i18n';

interface HeaderProps {
  currentTab: NavTab;
  onRefresh: () => void;
  isLoading: boolean;
  currentUser: AdminUser | null;
  onLogout: () => void;
  alerts: ExceptionAlert[];
  onResolveAlert: (alertId: string) => void;
  onSearchSelect?: (result: any) => void;
  isSidebarCollapsed: boolean;
  lang: Language;
  onToggleLang: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  currentTab,
  onRefresh,
  isLoading,
  currentUser,
  onLogout,
  alerts,
  onResolveAlert,
  isSidebarCollapsed,
  lang,
  onToggleLang,
}) => {
  const t = translations[lang];
  const [searchQuery, setSearchQuery] = useState('');
  const [showAlertCenter, setShowAlertCenter] = useState(false);

  const getTabTitle = (tab: NavTab) => {
    if (lang === 'hi') {
      switch (tab) {
        case 'dashboard':
          return 'कार्यकारी नियंत्रण केंद्र एवं रियल-टाइम पल्स';
        case 'users':
          return 'केवाईसी गेटकीपर एवं उपयोगकर्ता निर्देशिका';
        case 'orders':
          return 'लाइव हाइपरलोकल ऑर्डर फीड एवं गॉड मोड';
        case 'map':
          return 'लाइव संचालन मानचित्र एवं फ्लीट ट्रैकिंग';
        case 'financials':
          return 'निपटान, हब सीओडी एवं कॉर्पोरेट पेआउट';
        case 'catalog':
          return 'मास्टर उत्पाद कैटलॉग एवं मूल्य निर्धारण इंजन';
        case 'tickets':
          return 'ग्रामीण सहायता एवं विवाद समाधान';
        case 'refunds':
          return 'गेटवे रिफंड एवं प्रतिस्थापन ऑडिट';
        case 'audit':
          return 'अपरिवर्तनीय प्लेटफॉर्म ऑडिट ट्रेल';
        default:
          return 'गांवबाज़ार संचालन';
      }
    }
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
            {t.pilotArea}
          </span>
        </div>

        {/* Global Search Bar (Order ID, Phone, Name) */}
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder={
              lang === 'hi'
                ? 'ऑर्डर आईडी, फ़ोन (+91), या नाम से खोजें...'
                : 'Global search by Order ID, Phone (+91), or Partner name...'
            }
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

      {/* Right: Actions, Alert Center, Language Switcher, Super Admin Profile */}
      <div className="flex items-center space-x-3">
        {/* Language Switcher Pill */}
        <button
          onClick={onToggleLang}
          className="flex items-center space-x-1 px-2.5 py-1.5 text-xs font-bold text-emerald-800 bg-emerald-50 hover:bg-emerald-100 rounded-lg transition border border-emerald-300"
          title="Switch Language / भाषा बदलें"
        >
          <Languages className="w-3.5 h-3.5 text-emerald-700" />
          <span>{lang === 'en' ? 'हिंदी' : 'English'}</span>
        </button>

        {/* Sync Button */}
        <button
          onClick={onRefresh}
          disabled={isLoading}
          className="flex items-center space-x-1.5 px-3 py-1.5 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg transition border border-slate-200"
          title={lang === 'hi' ? 'रीयल-टाइम डेटा सिंक करें' : 'Sync Real-Time Data'}
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin text-emerald-600' : ''}`} />
          <span className="hidden md:inline">{isLoading ? t.syncing : t.sync}</span>
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
            title={lang === 'hi' ? 'लाइव अलर्ट केंद्र' : 'Live Alert Center'}
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
                  <span className="font-bold text-xs">
                    {lang === 'hi' ? `लाइव अपवाद अलर्ट (${alerts.length})` : `Live Exception Alerts (${alerts.length})`}
                  </span>
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
                    {lang === 'hi'
                      ? 'सभी परिचालन प्रणालियां सामान्य हैं। शून्य सक्रिय अपवाद।'
                      : 'All operational systems normal. Zero active exceptions.'}
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
                          {item.elapsed_minutes
                            ? `${item.elapsed_minutes}${lang === 'hi' ? ' मिनट पूर्व' : 'm ago'}`
                            : lang === 'hi'
                            ? 'लाइव'
                            : 'Live'}
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
                                window.alert(
                                  lang === 'hi'
                                    ? `राइडर ${item.runner_name || ''} के लिए आपातकालीन टीम भेजी गई!`
                                    : `Emergency support team dispatched for rider ${item.runner_name || ''}!`
                                );
                              }}
                              className="px-2 py-1 text-[10px] font-bold bg-rose-600 hover:bg-rose-700 text-white rounded shadow-xs"
                            >
                              {lang === 'hi' ? 'सहायता भेजें' : 'Dispatch Support'}
                            </button>
                            <button
                              onClick={() => window.alert(lang === 'hi' ? 'आपातकालीन कॉल की जा रही है...' : 'Calling rider emergency contact...')}
                              className="px-2 py-1 text-[10px] font-bold bg-slate-800 hover:bg-slate-900 text-white rounded flex items-center gap-1"
                            >
                              <PhoneCall className="w-3 h-3" /> {lang === 'hi' ? 'कॉल करें' : 'Call'}
                            </button>
                          </div>
                        ) : item.type === 'ORDER_DELAYED' ? (
                          <div className="flex items-center gap-1.5">
                            <button
                              onClick={() => {
                                onResolveAlert(item.id);
                                window.alert(
                                  lang === 'hi'
                                    ? `ऑर्डर ${item.order_id} के लिए रनर बदला गया!`
                                    : `Rerouting runner for order ${item.order_id}!`
                                );
                              }}
                              className="px-2 py-1 text-[10px] font-bold bg-amber-600 hover:bg-amber-700 text-white rounded"
                            >
                              {lang === 'hi' ? 'रनर बदलें' : 'Reroute Runner'}
                            </button>
                          </div>
                        ) : (
                          <div className="flex items-center gap-1.5">
                            <button
                              onClick={() => {
                                onResolveAlert(item.id);
                                window.alert(lang === 'hi' ? 'दुकानदार को कॉल किया गया!' : 'Store alerted via priority call!');
                              }}
                              className="px-2 py-1 text-[10px] font-bold bg-slate-800 hover:bg-slate-900 text-white rounded"
                            >
                              {lang === 'hi' ? 'दुकानदार को कॉल करें' : 'Call Store'}
                            </button>
                          </div>
                        )}

                        <button
                          onClick={() => onResolveAlert(item.id)}
                          className="text-[10px] text-slate-500 hover:text-slate-800 font-medium underline"
                        >
                          {lang === 'hi' ? 'खारिज करें' : 'Dismiss'}
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        {/* Dedicated Super Admin Role Badge (No Hub Manager Toggle) */}
        <div className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-extrabold bg-emerald-50 text-emerald-800 border border-emerald-300 shadow-xs">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
          <span>{t.superAdmin}</span>
        </div>

        {/* User Avatar & Logout */}
        <div className="flex items-center space-x-2 pl-2 border-l border-slate-200">
          <div className="w-8 h-8 rounded-full bg-slate-900 text-white flex items-center justify-center font-bold text-xs shadow-xs">
            SA
          </div>
          <button
            onClick={onLogout}
            className="px-2.5 py-1 text-xs font-semibold text-rose-700 bg-rose-50 hover:bg-rose-100 rounded-md border border-rose-200 transition"
            title={t.logout}
          >
            {t.logout}
          </button>
        </div>
      </div>
    </header>
  );
};
