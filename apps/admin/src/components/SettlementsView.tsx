import React, { useState } from 'react';
import { CircleDollarSign, Store, Bike, CheckCircle, Download, Send, AlertTriangle, ShieldCheck } from 'lucide-react';
import type { SettlementLedger } from '../types';

interface SettlementsViewProps {
  ledger: SettlementLedger | null;
}

export const SettlementsView: React.FC<SettlementsViewProps> = ({ ledger }) => {
  const [isProcessingBatch, setIsProcessingBatch] = useState(false);
  const [batchResult, setBatchResult] = useState<{
    batch_id: string;
    settled_vendors: number;
    settled_runners: number;
    total_settled_amount: number;
    message: string;
  } | null>(null);
  const [batchError, setBatchError] = useState<string | null>(null);

  if (!ledger) {
    return <div className="p-8 text-center text-slate-500">Loading settlements ledger...</div>;
  }

  const totalVendorPayouts = ledger.vendor_settlements.reduce((sum, v) => sum + v.total_payout, 0);
  const totalRunnerPayouts = ledger.runner_settlements.reduce((sum, r) => sum + r.total_payout, 0);

  const handleTriggerWeeklyBatch = async () => {
    setIsProcessingBatch(true);
    setBatchError(null);
    setBatchResult(null);

    const token = localStorage.getItem('token') || localStorage.getItem('access_token');
    try {
      const res = await fetch('/api/v1/admin/settlements/process-weekly-batch', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': token ? `Bearer ${token}` : ''
        }
      });
      const data = await res.json();
      if (res.ok && data.success) {
        setBatchResult(data);
      } else {
        setBatchError(data.detail || data.message || 'Batch payout trigger failed');
      }
    } catch {
      setBatchError('Network error while processing batch settlement');
    } finally {
      setIsProcessingBatch(false);
    }
  };

  const downloadVendorCsv = () => {
    window.open('/api/v1/admin/settlements/payouts/vendor-csv', '_blank');
  };

  const downloadRunnerCsv = () => {
    window.open('/api/v1/admin/settlements/payouts/runner-csv', '_blank');
  };

  return (
    <div className="space-y-6">
      {/* Weekly Settlement Header & Action Controls */}
      <div className="bg-gradient-to-r from-emerald-900 via-teal-900 to-slate-900 p-6 rounded-2xl text-white shadow-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-emerald-400 text-xs font-bold uppercase tracking-wider mb-1">
            <ShieldCheck className="w-4 h-4" />
            <span>Weekly Automated Settlement Cycle</span>
          </div>
          <h2 className="text-xl font-black">Apna GaonBazaar Payout Clearinghouse</h2>
          <p className="text-xs text-slate-300 mt-1 max-w-xl leading-relaxed">
            Direct bank and UPI settlement queue. GaonBazaar operates at 0% vendor commission with 100% pass-through of product subtotals to Kirana shopkeepers and delivery fees to runners.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2.5 shrink-0">
          <button
            onClick={downloadVendorCsv}
            className="px-3.5 py-2.5 bg-white/10 hover:bg-white/20 text-white rounded-xl text-xs font-bold flex items-center space-x-1.5 transition border border-white/20 active:scale-95"
            title="Export Corporate Bulk NEFT File"
          >
            <Download className="w-4 h-4" />
            <span>Vendor CSV</span>
          </button>
          <button
            onClick={downloadRunnerCsv}
            className="px-3.5 py-2.5 bg-white/10 hover:bg-white/20 text-white rounded-xl text-xs font-bold flex items-center space-x-1.5 transition border border-white/20 active:scale-95"
            title="Export Runner Delivery Settlement File"
          >
            <Download className="w-4 h-4" />
            <span>Runner CSV</span>
          </button>
          <button
            onClick={handleTriggerWeeklyBatch}
            disabled={isProcessingBatch}
            className="px-5 py-2.5 bg-emerald-500 hover:bg-emerald-600 active:scale-95 text-slate-950 font-black rounded-xl text-xs flex items-center space-x-2 shadow-lg shadow-emerald-500/30 transition disabled:opacity-50"
          >
            {isProcessingBatch ? (
              <>
                <div className="w-3.5 h-3.5 border-2 border-slate-950 border-t-transparent rounded-full animate-spin" />
                <span>Processing...</span>
              </>
            ) : (
              <>
                <Send className="w-4 h-4" />
                <span>Process Weekly Batch Payout</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Batch Execution Results Notification */}
      {batchResult && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-2xl flex items-start space-x-3 text-emerald-900 animate-in fade-in">
          <CheckCircle className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
          <div className="text-xs space-y-1">
            <h4 className="font-extrabold text-sm text-emerald-800">Weekly Batch Payout Executed Successfully</h4>
            <p className="text-emerald-700">{batchResult.message}</p>
            <div className="flex flex-wrap gap-4 font-mono font-bold text-[11px] pt-1">
              <span>Batch ID: {batchResult.batch_id}</span>
              <span>Settled Vendors: {batchResult.settled_vendors}</span>
              <span>Settled Runners: {batchResult.settled_runners}</span>
              <span>Total Dispatched: ₹{batchResult.total_settled_amount.toFixed(2)}</span>
            </div>
          </div>
        </div>
      )}

      {batchError && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-2xl flex items-start space-x-3 text-rose-900 animate-in fade-in">
          <AlertTriangle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
          <div className="text-xs">
            <h4 className="font-bold text-rose-800">Batch Settlement Notice</h4>
            <p className="text-rose-700">{batchError}</p>
          </div>
        </div>
      )}

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
        <div className="p-5 border-b border-slate-200 flex items-center justify-between">
          <div>
            <h4 className="font-extrabold text-slate-800 text-sm">
              Kirana Store Settlements (Product Subtotals)
            </h4>
            <p className="text-xs text-slate-500">
              Zero deduction guarantee: GaonBazaar takes 0% commission from local village merchants.
            </p>
          </div>
          <span className="text-xs font-mono font-bold px-2.5 py-1 bg-emerald-50 text-emerald-800 rounded-full border border-emerald-200">
            Weekly Cycle: Tue & Fri
          </span>
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
                <th className="py-3 px-4">Bank Verification</th>
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
                      <CheckCircle className="w-3 h-3 text-emerald-600" />
                      Penny Drop Verified
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <span className="inline-flex items-center gap-1 text-[11px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                      <CheckCircle className="w-3 h-3" />
                      Ready for Weekly Batch
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
        <div className="p-5 border-b border-slate-200 flex items-center justify-between">
          <div>
            <h4 className="font-extrabold text-slate-800 text-sm">
              Runner Delivery Fee Settlements
            </h4>
            <p className="text-xs text-slate-500">
              Runners receive 100% of customer delivery fee for every verified OTP handover.
            </p>
          </div>
          <span className="text-xs font-mono font-bold px-2.5 py-1 bg-blue-50 text-blue-800 rounded-full border border-blue-200">
            Weekly Cycle: Friday
          </span>
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
                <th className="py-3 px-4">Bank Verification</th>
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
                      <CheckCircle className="w-3 h-3 text-emerald-600" />
                      Penny Drop Verified
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <span className="inline-flex items-center gap-1 text-[11px] font-bold text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
                      <CheckCircle className="w-3 h-3" />
                      Ready for Friday Batch
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
