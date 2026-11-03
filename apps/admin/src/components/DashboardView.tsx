import React from 'react';
import {
  ShoppingBag,
  Bike,
  IndianRupee,
  Wallet,
  AlertTriangle,
  Radio,
  ArrowUpRight,
  TrendingUp,
  Clock,
  PhoneCall,
  CheckCircle2,
  RefreshCw,
} from 'lucide-react';
import type { AdminOverview, ExceptionAlert, HourlyTrendsData } from '../types';

interface DashboardViewProps {
  overview: AdminOverview | null;
  alerts: ExceptionAlert[];
  trends: HourlyTrendsData | null;
  onNavigate: (tab: any) => void;
  onResolveAlert: (alertId: string) => void;
  onTriggerSosTest?: () => void;
}

export const DashboardView: React.FC<DashboardViewProps> = ({
  overview,
  alerts,
  trends,
  onNavigate,
  onResolveAlert,
  onTriggerSosTest,
}) => {
  const criticalAlerts = alerts.filter(
    (a) => a.severity === 'CRITICAL' || a.type === 'SOS_RIDER'
  );

  // SVG Line Chart metrics for Hourly Trends
  const trendPoints = trends?.trend_data || [];
  const maxVolume = Math.max(
    1,
    ...trendPoints.map((p) => Math.max(p.today, p.yesterday))
  );

  const chartWidth = 720;
  const chartHeight = 180;
  const paddingX = 40;
  const paddingY = 25;
  const plotWidth = chartWidth - paddingX * 2;
  const plotHeight = chartHeight - paddingY * 2;

  const getCoordinates = (val: number, idx: number) => {
    const x = paddingX + (idx / Math.max(1, trendPoints.length - 1)) * plotWidth;
    const y = chartHeight - paddingY - (val / maxVolume) * plotHeight;
    return { x, y };
  };

  const todayPolyline = trendPoints
    .map((p, i) => {
      const { x, y } = getCoordinates(p.today, i);
      return `${x},${y}`;
    })
    .join(' ');

  const yesterdayPolyline = trendPoints
    .map((p, i) => {
      const { x, y } = getCoordinates(p.yesterday, i);
      return `${x},${y}`;
    })
    .join(' ');

  return (
    <div className="space-y-6">
      {/* Critical SOS / High Urgency Alerts Banner */}
      {criticalAlerts.length > 0 && (
        <div className="bg-rose-50 border-2 border-rose-500 rounded-2xl p-5 shadow-lg animate-in fade-in duration-200">
          <div className="flex items-center justify-between pb-3 border-b border-rose-200">
            <div className="flex items-center space-x-2.5">
              <span className="p-2 bg-rose-600 text-white rounded-xl shadow-xs animate-bounce">
                <Radio className="w-5 h-5" />
              </span>
              <div>
                <h3 className="text-sm font-black text-rose-950 uppercase tracking-wide">
                  Emergency Operational Alerts ({criticalAlerts.length} Active)
                </h3>
                <p className="text-xs text-rose-700">
                  Immediate admin action required: Rider accidents, extreme delays, or unaccepted orders.
                </p>
              </div>
            </div>
            <span className="px-3 py-1 bg-rose-600 text-white text-xs font-black rounded-full animate-pulse">
              ACTION REQUIRED
            </span>
          </div>

          <div className="mt-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3.5">
            {criticalAlerts.map((alert) => (
              <div
                key={alert.id}
                className="bg-white rounded-xl p-4 border border-rose-200 shadow-sm flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-[10px] font-extrabold uppercase px-2 py-0.5 rounded bg-rose-100 text-rose-800">
                      {alert.type}
                    </span>
                    <span className="text-[11px] font-semibold text-slate-500 flex items-center gap-1">
                      <Clock className="w-3 h-3 text-slate-400" />
                      {alert.elapsed_minutes ? `${alert.elapsed_minutes}m` : 'Just now'}
                    </span>
                  </div>
                  <h4 className="text-xs font-bold text-slate-900 leading-snug">
                    {alert.title}
                  </h4>
                  <p className="text-[11px] text-slate-600 mt-1 line-clamp-2">
                    {alert.description}
                  </p>
                </div>

                <div className="mt-3.5 pt-3 border-t border-slate-100 flex items-center justify-between">
                  <button
                    onClick={() => {
                      onResolveAlert(alert.id);
                      window.alert(`Emergency response team dispatched for ${alert.title}!`);
                    }}
                    className="px-2.5 py-1 text-[11px] font-bold bg-rose-600 hover:bg-rose-700 text-white rounded-lg shadow-xs transition"
                  >
                    Take Action
                  </button>
                  <button
                    onClick={() => onResolveAlert(alert.id)}
                    className="text-[11px] text-slate-500 hover:text-slate-800 font-semibold"
                  >
                    Resolve Alert
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Live Metrics: Top 4 Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Active Orders (Total / Delayed) */}
        <div
          onClick={() => onNavigate('orders')}
          className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs hover:border-emerald-500 hover:shadow-md transition cursor-pointer group"
        >
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wide">
              Active Orders
            </span>
            <div className="p-2.5 bg-emerald-50 text-emerald-600 rounded-xl group-hover:scale-105 transition">
              <ShoppingBag className="w-5 h-5" />
            </div>
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-3xl font-black text-slate-900">
              {overview?.active_orders_count ?? 0}
            </span>
            <span className="text-xs font-semibold text-slate-400">orders in flight</span>
          </div>
          <div className="mt-3 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
            <span className="text-slate-500">Delayed (&gt;45m):</span>
            <span
              className={`font-bold px-2 py-0.5 rounded-full ${
                (overview?.delayed_orders_count || 0) > 0
                  ? 'bg-rose-100 text-rose-700'
                  : 'bg-emerald-100 text-emerald-700'
              }`}
            >
              {overview?.delayed_orders_count ?? 0} delayed
            </span>
          </div>
        </div>

        {/* Card 2: Active Riders (Online / Busy / Idle) */}
        <div
          onClick={() => onNavigate('map')}
          className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs hover:border-emerald-500 hover:shadow-md transition cursor-pointer group"
        >
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wide">
              Active Riders Fleet
            </span>
            <div className="p-2.5 bg-blue-50 text-blue-600 rounded-xl group-hover:scale-105 transition">
              <Bike className="w-5 h-5" />
            </div>
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-3xl font-black text-slate-900">
              {overview?.active_riders_online ?? overview?.online_runners ?? 0}
            </span>
            <span className="text-xs font-semibold text-slate-400">riders on duty</span>
          </div>
          <div className="mt-3 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
            <span className="text-amber-600 font-semibold">
              ● {overview?.active_riders_busy ?? 0} Busy
            </span>
            <span className="text-emerald-600 font-semibold">
              ● {overview?.active_riders_idle ?? 0} Idle
            </span>
          </div>
        </div>

        {/* Card 3: Total Revenue Today */}
        <div
          onClick={() => onNavigate('financials')}
          className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs hover:border-emerald-500 hover:shadow-md transition cursor-pointer group"
        >
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wide">
              Revenue Today
            </span>
            <div className="p-2.5 bg-emerald-50 text-emerald-600 rounded-xl group-hover:scale-105 transition">
              <IndianRupee className="w-5 h-5" />
            </div>
          </div>
          <div className="flex items-baseline space-x-1">
            <span className="text-xs font-bold text-slate-500">₹</span>
            <span className="text-3xl font-black text-slate-900">
              {(overview?.revenue_today || overview?.total_gmv || 0).toLocaleString('en-IN')}
            </span>
          </div>
          <div className="mt-3 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
            <span className="text-slate-500">Total Pilot GMV:</span>
            <span className="font-bold text-slate-800">
              ₹{(overview?.total_gmv || 0).toLocaleString('en-IN')}
            </span>
          </div>
        </div>

        {/* Card 4: Cash to Collect (COD) */}
        <div
          onClick={() => onNavigate('financials')}
          className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs hover:border-emerald-500 hover:shadow-md transition cursor-pointer group"
        >
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wide">
              Cash to Collect (COD)
            </span>
            <div className="p-2.5 bg-amber-50 text-amber-600 rounded-xl group-hover:scale-105 transition">
              <Wallet className="w-5 h-5" />
            </div>
          </div>
          <div className="flex items-baseline space-x-1">
            <span className="text-xs font-bold text-slate-500">₹</span>
            <span className="text-3xl font-black text-amber-700">
              {(overview?.cash_to_collect_cod || 0).toLocaleString('en-IN')}
            </span>
          </div>
          <div className="mt-3 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
            <span className="text-slate-500">Local Hub Status:</span>
            <span className="font-bold text-amber-600">Pending Deposit</span>
          </div>
        </div>
      </div>

      {/* Hourly Trend Graph: Today vs. Yesterday */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 mb-4 border-b border-slate-100 gap-2">
          <div>
            <div className="flex items-center space-x-2">
              <TrendingUp className="w-5 h-5 text-emerald-600" />
              <h2 className="text-sm font-black text-slate-900">
                Order Volume Trends (Hourly Comparison)
              </h2>
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              Hourly order pacing: Comparing Today (Green line) vs. Yesterday (Slate dashed line)
            </p>
          </div>

          <div className="flex items-center space-x-4 text-xs font-bold">
            <div className="flex items-center space-x-1.5">
              <span className="w-3 h-3 rounded-full bg-emerald-500" />
              <span className="text-slate-800">
                Today ({trends?.total_today_orders || 0} orders)
              </span>
            </div>
            <div className="flex items-center space-x-1.5">
              <span className="w-3 h-0.5 bg-slate-400 border border-slate-400 border-dashed" />
              <span className="text-slate-500">
                Yesterday ({trends?.total_yesterday_orders || 0} orders)
              </span>
            </div>
          </div>
        </div>

        {/* Responsive SVG Chart */}
        <div className="w-full overflow-x-auto">
          <div className="min-w-[680px]">
            <svg
              viewBox={`0 0 ${chartWidth} ${chartHeight}`}
              className="w-full h-48 select-none"
            >
              {/* Background Grid Lines */}
              {[0, 0.25, 0.5, 0.75, 1].map((ratio, i) => {
                const y = chartHeight - paddingY - ratio * plotHeight;
                const labelVal = Math.round(ratio * maxVolume);
                return (
                  <g key={i}>
                    <line
                      x1={paddingX}
                      y1={y}
                      x2={chartWidth - paddingX}
                      y2={y}
                      stroke="#f1f5f9"
                      strokeWidth="1"
                    />
                    <text
                      x={paddingX - 10}
                      y={y + 3}
                      textAnchor="end"
                      fontSize="9"
                      fill="#94a3b8"
                      fontWeight="600"
                    >
                      {labelVal}
                    </text>
                  </g>
                );
              })}

              {/* Yesterday Line (Dashed) */}
              {yesterdayPolyline && (
                <polyline
                  fill="none"
                  stroke="#94a3b8"
                  strokeWidth="2"
                  strokeDasharray="4 4"
                  points={yesterdayPolyline}
                />
              )}

              {/* Today Line (Solid Emerald) */}
              {todayPolyline && (
                <polyline
                  fill="none"
                  stroke="#10b981"
                  strokeWidth="3.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  points={todayPolyline}
                />
              )}

              {/* Data Dots for Today */}
              {trendPoints.map((p, i) => {
                const { x, y } = getCoordinates(p.today, i);
                return (
                  <g key={i}>
                    <circle
                      cx={x}
                      cy={y}
                      r="4"
                      fill="#10b981"
                      stroke="#ffffff"
                      strokeWidth="2"
                    />
                    <text
                      x={x}
                      y={chartHeight - 6}
                      textAnchor="middle"
                      fontSize="9"
                      fill="#64748b"
                      fontWeight="600"
                    >
                      {p.hour}
                    </text>
                  </g>
                );
              })}
            </svg>
          </div>
        </div>
      </div>

      {/* Operational Pulse & Quick Action Links */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Gatekeeper KYC Queue Preview */}
        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold text-amber-700 bg-amber-50 px-2 py-0.5 rounded-full uppercase tracking-wider">
                Module 2
              </span>
              <span className="text-xs text-slate-400">Strict Gatekeeper</span>
            </div>
            <h3 className="text-sm font-extrabold text-slate-900">
              Pending KYC Approvals
            </h3>
            <p className="text-xs text-slate-600 mt-1">
              {(overview?.pending_vendor_approvals || 0) + (overview?.pending_runner_approvals || 0)} partners waiting for Penny Drop and Aadhaar verification.
            </p>
          </div>
          <button
            onClick={() => onNavigate('users')}
            className="mt-4 w-full py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-xs font-bold flex items-center justify-center space-x-1.5 transition"
          >
            <span>Review Pending Approvals</span>
            <ArrowUpRight className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Live Map Dispatch Preview */}
        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold text-blue-700 bg-blue-50 px-2 py-0.5 rounded-full uppercase tracking-wider">
                Module 4
              </span>
              <span className="text-xs text-slate-400">Operations Center</span>
            </div>
            <h3 className="text-sm font-extrabold text-slate-900">
              Live Fleet Map & Heatmaps
            </h3>
            <p className="text-xs text-slate-600 mt-1">
              Real-time rider GPS pinging every 10s. Monitor demand red zones and dispatch alerts.
            </p>
          </div>
          <button
            onClick={() => onNavigate('map')}
            className="mt-4 w-full py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold flex items-center justify-center space-x-1.5 transition"
          >
            <span>Open Fleet Operations Map</span>
            <ArrowUpRight className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Hub COD Settlements Preview */}
        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full uppercase tracking-wider">
                Module 5
              </span>
              <span className="text-xs text-slate-400">Settlements</span>
            </div>
            <h3 className="text-sm font-extrabold text-slate-900">
              COD Reconciliation & Payouts
            </h3>
            <p className="text-xs text-slate-600 mt-1">
              Mark runner cash as 'Received & Deposited' at base and export NEFT/RTGS batch CSV files.
            </p>
          </div>
          <button
            onClick={() => onNavigate('financials')}
            className="mt-4 w-full py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold flex items-center justify-center space-x-1.5 transition"
          >
            <span>Open Financials Ledger</span>
            <ArrowUpRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
};
