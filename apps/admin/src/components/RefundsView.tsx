import React, { useEffect, useState } from 'react';
import { RotateCcw, CheckCircle, Clock, IndianRupee, ShieldCheck } from 'lucide-react';
import { adminApi } from '../api';

export const RefundsView: React.FC = () => {
  const [refunds, setRefunds] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadRefunds();
  }, []);

  const loadRefunds = async () => {
    setLoading(true);
    try {
      const data = await adminApi.getRefunds();
      setRefunds(data);
    } catch {
      // Ignored
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs flex items-center justify-between">
        <div>
          <div className="flex items-center space-x-2">
            <RotateCcw className="w-5 h-5 text-emerald-600" />
            <h2 className="text-sm font-extrabold text-slate-900">
              Gateway Refunds & Replacement Audit Ledger
            </h2>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Immutable log of instant customer refunds and replacements authorized by Super Admin God Mode.
          </p>
        </div>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-50 text-slate-500 uppercase text-[10px] font-bold tracking-wider border-b border-slate-200">
            <tr>
              <th className="px-6 py-3">Refund ID</th>
              <th className="px-6 py-3">Order Ref</th>
              <th className="px-6 py-3">Gateway ID</th>
              <th className="px-6 py-3">Amount</th>
              <th className="px-6 py-3">Reason</th>
              <th className="px-6 py-3">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
            {refunds.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-6 py-12 text-center text-slate-400">
                  Zero refund disputes. All customer settlements reconciled.
                </td>
              </tr>
            ) : (
              refunds.map((r) => (
                <tr key={r.id} className="hover:bg-slate-50/80 transition">
                  <td className="px-6 py-4 font-mono font-bold text-slate-900">#{r.id.slice(0, 8)}</td>
                  <td className="px-6 py-4 font-mono text-indigo-700">#{r.order_id.slice(0, 8)}</td>
                  <td className="px-6 py-4 font-mono text-slate-500">{r.gateway_refund_id || 'RZP-DIRECT'}</td>
                  <td className="px-6 py-4 font-black text-slate-900">₹{r.amount}</td>
                  <td className="px-6 py-4 text-slate-600">{r.reason}</td>
                  <td className="px-6 py-4">
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800">
                      {r.status || 'COMPLETED'}
                    </span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
