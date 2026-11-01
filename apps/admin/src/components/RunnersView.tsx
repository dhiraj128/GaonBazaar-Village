import { useState } from 'react';
import {
  ShieldCheck,
  Search,
  CreditCard,
  FileText,
  Star,
} from 'lucide-react';
import type { RunnerItem } from '../types';

interface RunnersViewProps {
  runners: RunnerItem[];
  onApprove: (id: string) => Promise<void>;
  onReject: (id: string) => Promise<void>;
}

export const RunnersView: React.FC<RunnersViewProps> = ({ runners, onApprove, onReject }) => {
  const [filter, setFilter] = useState<'all' | 'pending' | 'approved'>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [loadingId, setLoadingId] = useState<string | null>(null);

  const filteredRunners = runners.filter((r) => {
    if (filter === 'pending' && r.is_approved) return false;
    if (filter === 'approved' && !r.is_approved) return false;
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      return (
        r.full_name.toLowerCase().includes(term) ||
        r.vehicle_type.toLowerCase().includes(term) ||
        r.vehicle_number.toLowerCase().includes(term) ||
        r.driving_license_number.toLowerCase().includes(term)
      );
    }
    return true;
  });

  const handleAction = async (id: string, action: 'approve' | 'reject') => {
    setLoadingId(id);
    try {
      if (action === 'approve') await onApprove(id);
      else await onReject(id);
    } finally {
      setLoadingId(null);
    }
  };

  const pendingCount = runners.filter((r) => !r.is_approved).length;

  return (
    <div className="space-y-6">
      {/* Search & Tabs Header */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 rounded-lg text-xs font-bold transition ${
              filter === 'all'
                ? 'bg-slate-900 text-white'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            All Runners ({runners.length})
          </button>
          <button
            onClick={() => setFilter('pending')}
            className={`px-4 py-2 rounded-lg text-xs font-bold transition flex items-center gap-1.5 ${
              filter === 'pending'
                ? 'bg-amber-600 text-white'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            <span>Pending DL & Vehicle KYC</span>
            {pendingCount > 0 && (
              <span className="px-1.5 py-0.2 rounded-full text-[10px] bg-amber-200 text-amber-900 font-extrabold">
                {pendingCount}
              </span>
            )}
          </button>
          <button
            onClick={() => setFilter('approved')}
            className={`px-4 py-2 rounded-lg text-xs font-bold transition ${
              filter === 'approved'
                ? 'bg-emerald-600 text-white'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            Verified Fleet ({runners.filter((r) => r.is_approved).length})
          </button>
        </div>

        <div className="relative w-full md:w-72">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search runner, DL, vehicle no..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-3 py-2 text-xs border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
          />
        </div>
      </div>

      {/* Runners Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {filteredRunners.map((runner) => (
          <div
            key={runner.id}
            className={`bg-white rounded-xl border p-5 shadow-sm transition hover:shadow-md ${
              !runner.is_approved ? 'border-amber-300 ring-1 ring-amber-200' : 'border-slate-200'
            }`}
          >
            <div className="flex items-start justify-between">
              <div>
                <div className="flex items-center gap-2">
                  <h4 className="font-extrabold text-slate-800 text-base">{runner.full_name}</h4>
                  <span
                    className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                      runner.is_approved
                        ? 'bg-emerald-100 text-emerald-800'
                        : 'bg-amber-100 text-amber-800'
                    }`}
                  >
                    {runner.is_approved ? 'VERIFIED' : 'PENDING APPROVAL'}
                  </span>
                </div>
                <div className="text-xs text-slate-500 mt-0.5 flex items-center gap-2">
                  <span>{runner.vehicle_type}</span>
                  {runner.rating > 0 && (
                    <span className="flex items-center gap-0.5 text-amber-600 font-bold">
                      <Star className="w-3 h-3 fill-amber-500 text-amber-500" />
                      {runner.rating}
                    </span>
                  )}
                </div>
              </div>

              <span
                className={`text-[11px] font-bold px-2 py-0.5 rounded ${
                  runner.is_online
                    ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                    : 'bg-slate-100 text-slate-600'
                }`}
              >
                {runner.is_online ? 'ON DUTY (ONLINE)' : 'OFF DUTY'}
              </span>
            </div>

            {/* Document Details */}
            <div className="mt-4 pt-3 border-t border-slate-100 grid grid-cols-2 gap-3 text-xs">
              <div className="flex items-start space-x-2">
                <FileText className="w-4 h-4 text-slate-400 mt-0.5 flex-shrink-0" />
                <div>
                  <div className="font-bold text-slate-700">Vehicle & License</div>
                  <div className="text-[11px] text-slate-600 font-mono">
                    Reg: {runner.vehicle_number}
                  </div>
                  <div className="text-[10px] text-slate-500 font-mono">
                    DL: {runner.driving_license_number}
                  </div>
                </div>
              </div>

              <div className="flex items-start space-x-2">
                <CreditCard className="w-4 h-4 text-slate-400 mt-0.5 flex-shrink-0" />
                <div>
                  <div className="font-bold text-slate-700">UPI Payout</div>
                  <div className="text-[11px] text-slate-600 font-mono">
                    {runner.payout_upi_id || 'Not registered'}
                  </div>
                  <div className="text-[10px] text-emerald-600 font-semibold flex items-center gap-1 mt-0.5">
                    <ShieldCheck className="w-3 h-3" />
                    DigiLocker Consent
                  </div>
                </div>
              </div>
            </div>

            {/* Action Bar */}
            <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between">
              <div className="text-xs text-slate-400">
                Delivery Payout: <b className="text-slate-700">100% of delivery fee</b>
              </div>
              <div className="flex items-center space-x-2">
                {!runner.is_approved ? (
                  <>
                    <button
                      onClick={() => handleAction(runner.id, 'reject')}
                      disabled={loadingId === runner.id}
                      className="px-3 py-1.5 text-xs font-bold text-rose-700 bg-rose-50 hover:bg-rose-100 rounded-lg transition border border-rose-200"
                    >
                      Reject
                    </button>
                    <button
                      onClick={() => handleAction(runner.id, 'approve')}
                      disabled={loadingId === runner.id}
                      className="px-4 py-1.5 text-xs font-bold text-white bg-emerald-600 hover:bg-emerald-700 rounded-lg transition shadow-sm"
                    >
                      Approve Runner
                    </button>
                  </>
                ) : (
                  <button
                    onClick={() => handleAction(runner.id, 'reject')}
                    disabled={loadingId === runner.id}
                    className="px-3 py-1.5 text-xs font-semibold text-slate-600 bg-slate-100 hover:bg-slate-200 rounded-lg transition"
                  >
                    Revoke Approval
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}

        {filteredRunners.length === 0 && (
          <div className="col-span-2 p-12 text-center text-slate-400 bg-white rounded-xl border border-slate-200">
            No runners match the current filters.
          </div>
        )}
      </div>
    </div>
  );
};
