import React, { useState, useEffect } from 'react';
import { Headphones, CheckCircle2, AlertCircle, Clock, MessageSquare } from 'lucide-react';
import { adminApi } from '../api';
import type { SupportTicketItem } from '../types';

interface TicketsViewProps {
  tickets?: SupportTicketItem[];
  onUpdateStatus?: (id: string, status: 'OPEN' | 'RESOLVED' | 'CLOSED') => Promise<void>;
}

export const TicketsView: React.FC<TicketsViewProps> = ({ tickets: initialTickets, onUpdateStatus }) => {
  const [tickets, setTickets] = useState<SupportTicketItem[]>(initialTickets || []);
  const [loading, setLoading] = useState(!initialTickets);

  useEffect(() => {
    if (initialTickets) {
      setTickets(initialTickets);
      setLoading(false);
    } else {
      loadTickets();
    }
  }, [initialTickets]);

  const loadTickets = async () => {
    setLoading(true);
    const data = await adminApi.getTickets();
    setTickets(data);
    setLoading(false);
  };

  const handleResolve = async (id: string) => {
    if (onUpdateStatus) {
      await onUpdateStatus(id, 'RESOLVED');
    } else {
      await adminApi.updateTicketStatus(id, 'RESOLVED');
    }
    setTickets((prev) =>
      prev.map((t) => (t.id === id ? { ...t, status: 'RESOLVED' } : t))
    );
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Support & Help Tickets</h2>
        <p className="text-slate-600 text-sm">
          Customer and village vendor inquiries, complaints, and delivery issues
        </p>
      </div>

      {loading ? (
        <div className="text-center py-12 text-slate-500">Loading support tickets...</div>
      ) : tickets.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-xl border border-slate-200">
          <Headphones className="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <p className="text-slate-600 font-medium">No open tickets</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {tickets.map((t) => (
            <div
              key={t.id}
              className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 flex flex-col md:flex-row justify-between items-start md:items-center gap-4 hover:border-slate-300 transition"
            >
              <div className="space-y-2">
                <div className="flex items-center gap-3">
                  <span
                    className={`px-2.5 py-0.5 rounded-full text-xs font-bold flex items-center gap-1 ${
                      t.status === 'OPEN'
                        ? 'bg-amber-100 text-amber-800'
                        : 'bg-emerald-100 text-emerald-800'
                    }`}
                  >
                    {t.status === 'OPEN' ? (
                      <AlertCircle className="w-3.5 h-3.5" />
                    ) : (
                      <CheckCircle2 className="w-3.5 h-3.5" />
                    )}
                    {t.status}
                  </span>
                  <span className="text-xs text-slate-400 font-mono">#{t.id}</span>
                  {t.order_id && (
                    <span className="text-xs bg-slate-100 text-slate-700 px-2 py-0.5 rounded font-mono">
                      Order: {t.order_id}
                    </span>
                  )}
                  <span className="text-xs text-slate-400 flex items-center gap-1">
                    <Clock className="w-3.5 h-3.5" />
                    {new Date(t.created_at).toLocaleString()}
                  </span>
                </div>
                <h3 className="text-lg font-semibold text-slate-900">{t.subject}</h3>
                <p className="text-sm text-slate-600 flex items-start gap-2">
                  <MessageSquare className="w-4 h-4 text-slate-400 shrink-0 mt-0.5" />
                  {t.message}
                </p>
              </div>

              {t.status === 'OPEN' && (
                <button
                  onClick={() => handleResolve(t.id)}
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-sm font-semibold transition shrink-0 flex items-center gap-1.5"
                >
                  <CheckCircle2 className="w-4 h-4" />
                  Mark as Resolved
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
