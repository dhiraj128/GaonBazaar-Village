import { CircleDollarSign, Store, Bike, CheckCircle } from 'lucide-react';
import type { SettlementLedger } from '../types';

interface SettlementsViewProps {
  ledger: SettlementLedger | null;
}

export const SettlementsView: React.FC<SettlementsViewProps> = ({ ledger }) => {
  if (!ledger) {
    return <div className="p-8 text-center text-slate-500">Loading settlements ledger...</div>;
  }

  const totalVendorPayouts = ledger.vendor_settlements.reduce((sum, v) => sum + v.total_payout, 0);
  const totalRunnerPayouts = ledger.runner_settlements.reduce((sum, r) => sum + r.total_payout, 0);

  return (
    <div className="space-y-6">
      {/* Financial Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Vendor Settlements (0% Commission)
            </span>
            <div className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center">
              <Store className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-black text-slate-800">
            ₹{totalVendorPayouts.toFixed(2)}
          </div>
          <div className="text-xs text-slate-500 mt-1">
            100% of product subtotal directly to kirana shopkeepers
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Runner Delivery Payouts
            </span>
            <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center">
              <Bike className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-black text-slate-800">
            ₹{totalRunnerPayouts.toFixed(2)}
          </div>
          <div className="text-xs text-slate-500 mt-1">
            100% of delivery fee passed through to delivery runners
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Platform Convenience Revenue
            </span>
            <div className="w-8 h-8 rounded-lg bg-purple-50 text-purple-600 flex items-center justify-center">
              <CircleDollarSign className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-black text-emerald-600">
            ₹{ledger.platform_fee_collected.toFixed(2)}
          </div>
          <div className="text-xs text-slate-500 mt-1">
            ₹3.00 collected across {ledger.total_delivered_orders} delivered order(s)
          </div>
        </div>
      </div>

      {/* Vendor Payouts Breakdown */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-5 border-b border-slate-200">
          <h4 className="font-extrabold text-slate-800 text-sm">
            Kirana Store Settlements (Product Subtotals)
          </h4>
          <p className="text-xs text-slate-500">
            Zero deduction guarantee: GaonBazaar takes 0% commission from local village merchants.
          </p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50 text-slate-600 font-bold border-b border-slate-200">
                <th className="py-3 px-4">Store Name</th>
                <th className="py-3 px-4">Orders Fulfilled</th>
                <th className="py-3 px-4">Subtotal Sales</th>
                <th className="py-3 px-4">Commission</th>
                <th className="py-3 px-4">Net Payout Due</th>
                <th className="py-3 px-4">Settlement Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {ledger.vendor_settlements.map((v, idx) => (
                <tr key={idx} className="hover:bg-slate-50/50">
                  <td className="py-3 px-4 font-semibold text-slate-800">{v.store_name}</td>
                  <td className="py-3 px-4">{v.order_count}</td>
                  <td className="py-3 px-4 font-bold text-slate-900">₹{v.total_payout.toFixed(2)}</td>
                  <td className="py-3 px-4 text-emerald-600 font-bold">0.0% (₹0.00)</td>
                  <td className="py-3 px-4 font-extrabold text-emerald-700">
                    ₹{v.total_payout.toFixed(2)}
                  </td>
                  <td className="py-3 px-4">
                    <span className="inline-flex items-center gap-1 text-[11px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                      <CheckCircle className="w-3 h-3" />
                      Ready for UPI Transfer
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Runner Payouts Breakdown */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-5 border-b border-slate-200">
          <h4 className="font-extrabold text-slate-800 text-sm">
            Runner Delivery Fee Settlements
          </h4>
          <p className="text-xs text-slate-500">
            Runners receive 100% of customer delivery fee for every verified OTP handover.
          </p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50 text-slate-600 font-bold border-b border-slate-200">
                <th className="py-3 px-4">Runner ID</th>
                <th className="py-3 px-4">Delivered Orders</th>
                <th className="py-3 px-4">Delivery Fees Earned</th>
                <th className="py-3 px-4">Platform Share</th>
                <th className="py-3 px-4">Net Payout Due</th>
                <th className="py-3 px-4">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {ledger.runner_settlements.map((r, idx) => (
                <tr key={idx} className="hover:bg-slate-50/50">
                  <td className="py-3 px-4 font-mono font-bold text-slate-800">{r.runner_id}</td>
                  <td className="py-3 px-4">{r.order_count}</td>
                  <td className="py-3 px-4 font-bold text-slate-900">₹{r.total_payout.toFixed(2)}</td>
                  <td className="py-3 px-4 text-slate-400">0% (₹0.00)</td>
                  <td className="py-3 px-4 font-extrabold text-blue-700">
                    ₹{r.total_payout.toFixed(2)}
                  </td>
                  <td className="py-3 px-4">
                    <span className="inline-flex items-center gap-1 text-[11px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                      <CheckCircle className="w-3 h-3" />
                      Ready for UPI Transfer
                    </span>
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
