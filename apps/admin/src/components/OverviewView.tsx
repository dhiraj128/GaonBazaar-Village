import React from 'react';
import {
  IndianRupee,
  ShoppingBag,
  Store,
  Bike,
  ShieldAlert,
  ArrowRight,
  AlertTriangle,
} from 'lucide-react';
import type { NavTab } from './Sidebar';
import type { AdminOverview, OrderItemRecord } from '../types';

interface OverviewViewProps {
  overview: AdminOverview | null;
  recentOrders: OrderItemRecord[];
  onNavigate: (tab: NavTab) => void;
}

export const OverviewView: React.FC<OverviewViewProps> = ({
  overview,
  recentOrders,
  onNavigate,
}) => {
  if (!overview) {
    return (
      <div className="p-8 text-center text-slate-500">
        Loading system analytics...
      </div>
    );
  }

  const hasPendingApprovals =
    overview.pending_vendor_approvals > 0 || overview.pending_runner_approvals > 0;

  return (
    <div className="space-y-6">
      {/* Alert Header if pending approvals exist */}
      {hasPendingApprovals && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 flex items-center justify-between shadow-xs">
          <div className="flex items-center space-x-3">
            <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0" />
            <div>
              <h4 className="text-sm font-bold text-amber-900">
                KYC Verification Action Items
              </h4>
              <p className="text-xs text-amber-700">
                You have {overview.pending_vendor_approvals} stores and{' '}
                {overview.pending_runner_approvals} delivery partners waiting for Super Admin review.
              </p>
            </div>
          </div>
          <div className="flex space-x-2">
            <button
              onClick={() => onNavigate('users')}
              className="px-3 py-1.5 text-xs font-semibold bg-amber-600 hover:bg-amber-700 text-white rounded-lg transition"
            >
              Review KYC Queue
            </button>
          </div>
        </div>
      )}

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
        {/* GMV */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Total GMV
            </span>
            <div className="w-9 h-9 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center">
              <IndianRupee className="w-5 h-5" />
            </div>
          </div>
          <div className="text-2xl font-black text-slate-800">
            ₹{overview.total_gmv.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
          </div>
          <div className="mt-2 text-xs text-slate-500 flex items-center gap-1">
            <span className="text-emerald-600 font-semibold">100% genuine</span> delivered village orders
          </div>
        </div>

        {/* Active Orders */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Active Orders
            </span>
            <div className="w-9 h-9 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center">
              <ShoppingBag className="w-5 h-5" />
            </div>
          </div>
          <div className="text-2xl font-black text-slate-800">{overview.active_orders_count}</div>
          <div className="mt-2 text-xs text-slate-500">
            Out of <span className="font-semibold text-slate-700">{overview.total_orders}</span> total lifetime orders
          </div>
        </div>

        {/* Stores */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Verified Kiranas
            </span>
            <div className="w-9 h-9 rounded-lg bg-purple-50 text-purple-600 flex items-center justify-center">
              <Store className="w-5 h-5" />
            </div>
          </div>
          <div className="text-2xl font-black text-slate-800">
            {overview.active_stores}{' '}
            <span className="text-sm font-medium text-slate-400">/ {overview.total_stores}</span>
          </div>
          <div className="mt-2 text-xs text-slate-500">
            Online and serving registered localities
          </div>
        </div>

        {/* Runners */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Delivery Runners
            </span>
            <div className="w-9 h-9 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center">
              <Bike className="w-5 h-5" />
            </div>
          </div>
          <div className="text-2xl font-black text-slate-800">
            {overview.online_runners}{' '}
            <span className="text-sm font-medium text-slate-400">/ {overview.total_runners}</span>
          </div>
          <div className="mt-2 text-xs text-slate-500">
            Online with active GPS duty
          </div>
        </div>
      </div>

      {/* Strict System Invariants Card */}
      <div className="bg-slate-900 text-white rounded-xl p-6 border border-slate-800 shadow-md">
        <div className="flex items-center space-x-2 text-emerald-400 mb-2 font-bold text-sm">
          <ShieldAlert className="w-4 h-4" />
          <span>Platform Operating Policies</span>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-4">
          <div className="bg-slate-800/80 p-3.5 rounded-lg border border-slate-700">
            <div className="text-xs text-slate-400">Delivery Boundary</div>
            <div className="text-base font-bold text-white mt-1">
              Max {overview.max_delivery_radius_km} km Radius
            </div>
            <div className="text-[11px] text-slate-400 mt-1">Enforced via Haversine geo distance</div>
          </div>
          <div className="bg-slate-800/80 p-3.5 rounded-lg border border-slate-700">
            <div className="text-xs text-slate-400">Platform Convenience Fee</div>
            <div className="text-base font-bold text-white mt-1">
              ₹{overview.platform_fee.toFixed(2)} per order
            </div>
            <div className="text-[11px] text-slate-400 mt-1">Fixed platform operating charge</div>
          </div>
          <div className="bg-slate-800/80 p-3.5 rounded-lg border border-slate-700">
            <div className="text-xs text-slate-400">Introductory Vendor Commission</div>
            <div className="text-base font-bold text-white mt-1">
              {overview.vendor_commission_pct}% Rate
            </div>
            <div className="text-[11px] text-slate-400 mt-1">100% product subtotal to village vendor</div>
          </div>
          <div className="bg-slate-800/80 p-3.5 rounded-lg border border-slate-700">
            <div className="text-xs text-slate-400">Customer Cancellation</div>
            <div className="text-base font-bold text-white mt-1">180 Seconds Window</div>
            <div className="text-[11px] text-slate-400 mt-1">Strict timer before store prep starts</div>
          </div>
        </div>
      </div>

      {/* Live Orders Overview Section */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-5 border-b border-slate-200 flex items-center justify-between">
          <div>
            <h3 className="font-bold text-slate-800 text-sm">Recent Active Orders</h3>
            <p className="text-xs text-slate-500">Live order queue from pilot localities</p>
          </div>
          <button
            onClick={() => onNavigate('orders')}
            className="text-xs font-semibold text-emerald-600 hover:text-emerald-700 flex items-center gap-1"
          >
            <span>View All Orders</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50 text-slate-500 font-semibold border-b border-slate-200">
                <th className="py-3 px-4">Order ID</th>
                <th className="py-3 px-4">Store</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Amount</th>
                <th className="py-3 px-4">Payment</th>
                <th className="py-3 px-4">OTP</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {recentOrders.slice(0, 4).map((order) => (
                <tr key={order.id} className="hover:bg-slate-50/50">
                  <td className="py-3 px-4 font-mono font-bold text-slate-800">#{order.id}</td>
                  <td className="py-3 px-4 font-medium">{order.store_name}</td>
                  <td className="py-3 px-4">
                    <span
                      className={`inline-block px-2 py-0.5 rounded text-[11px] font-bold ${
                        order.status === 'DELIVERED'
                          ? 'bg-emerald-100 text-emerald-800'
                          : order.status === 'OUT_FOR_DELIVERY'
                          ? 'bg-blue-100 text-blue-800'
                          : order.status === 'PACKED'
                          ? 'bg-amber-100 text-amber-800'
                          : 'bg-slate-100 text-slate-800'
                      }`}
                    >
                      {order.status}
                    </span>
                  </td>
                  <td className="py-3 px-4 font-bold text-slate-900">
                    ₹{order.total_amount.toFixed(2)}
                  </td>
                  <td className="py-3 px-4">
                    <span className="font-semibold text-slate-600">{order.payment_mode}</span>
                  </td>
                  <td className="py-3 px-4 font-mono font-bold text-emerald-700 bg-emerald-50/50">
                    {order.delivery_otp}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
