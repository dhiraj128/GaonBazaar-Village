import React, { useState, useEffect } from 'react';
import { Headphones, CheckCircle2, AlertCircle, Clock, MessageSquare, Send, ChevronDown, ChevronUp, Tag } from 'lucide-react';
import { adminApi } from '../api';
import type { SupportTicketItem } from '../types';

interface TicketsViewProps {
  tickets?: SupportTicketItem[];
  onUpdateStatus?: (id: string, status: 'OPEN' | 'RESOLVED' | 'CLOSED') => Promise<void>;
}

export const TicketsView: React.FC<TicketsViewProps> = ({ tickets: initialTickets, onUpdateStatus }) => {
  const [tickets, setTickets] = useState<SupportTicketItem[]>(initialTickets || []);
  const [loading, setLoading] = useState(!initialTickets);
  const [expandedTicketId, setExpandedTicketId] = useState<string | null>(null);
  const [replyText, setReplyText] = useState<{ [ticketId: string]: string }>({});
  const [isSubmittingReply, setIsSubmittingReply] = useState<{ [ticketId: string]: boolean }>({});

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

  const handleSendReply = async (ticketId: string) => {
    const text = (replyText[ticketId] || '').trim();
    if (!text) return;

    setIsSubmittingReply((prev) => ({ ...prev, [ticketId]: true }));
    try {
      const res = await adminApi.replyTicket(ticketId, text);
      if (res && res.messages) {
        setTickets((prev) =>
          prev.map((t) => (t.id === ticketId ? { ...t, messages: res.messages, status: res.status || t.status } : t))
        );
      } else {
        // Optimistic append
        setTickets((prev) =>
          prev.map((t) => {
            if (t.id !== ticketId) return t;
            const msgs = t.messages || [];
            return {
              ...t,
              messages: [
                ...msgs,
                {
                  id: `msg_${Date.now()}`,
                  sender_id: 'admin_pilot',
                  sender_role: 'ADMIN',
                  message: text,
                  created_at: new Date().toISOString(),
                },
              ],
            };
          })
        );
      }
      setReplyText((prev) => ({ ...prev, [ticketId]: '' }));
    } catch {
      // Ignore
    } finally {
      setIsSubmittingReply((prev) => ({ ...prev, [ticketId]: false }));
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Support & Help Tickets</h2>
        <p className="text-slate-600 text-sm">
          Customer and village vendor inquiries, complaints, order tracking, and refund requests
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
          {tickets.map((t) => {
            const isExpanded = expandedTicketId === t.id;
            const messages = t.messages || [];

            return (
              <div
                key={t.id}
                className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 flex flex-col gap-4 hover:border-slate-300 transition"
              >
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                  <div className="space-y-2">
                    <div className="flex flex-wrap items-center gap-2">
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
                      {t.category && (
                        <span className="text-xs bg-emerald-50 text-emerald-800 border border-emerald-200 px-2 py-0.5 rounded font-medium flex items-center gap-1">
                          <Tag className="w-3 h-3" />
                          {t.category}
                        </span>
                      )}
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
                    {t.resolution_notes && (
                      <div className="bg-emerald-50 border border-emerald-200 rounded p-2 text-xs text-emerald-900">
                        <strong>Resolution Note:</strong> {t.resolution_notes}
                      </div>
                    )}
                  </div>

                  <div className="flex items-center gap-2 shrink-0">
                    <button
                      onClick={() => setExpandedTicketId(isExpanded ? null : t.id)}
                      className="px-3 py-1.5 border border-slate-300 hover:bg-slate-50 text-slate-700 rounded-lg text-xs font-semibold flex items-center gap-1 transition"
                    >
                      {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                      {messages.length > 0 ? `${messages.length} Messages` : 'Conversation'}
                    </button>

                    {t.status === 'OPEN' ? (
                      <button
                        onClick={() => handleResolve(t.id)}
                        className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-sm font-semibold transition shrink-0 flex items-center gap-1.5"
                      >
                        <CheckCircle2 className="w-4 h-4" />
                        Mark Resolved
                      </button>
                    ) : (
                      <span className="text-xs font-medium text-emerald-600 flex items-center gap-1">
                        <CheckCircle2 className="w-4 h-4" />
                        Resolved
                      </span>
                    )}
                  </div>
                </div>

                {/* Conversation Thread Dropdown */}
                {isExpanded && (
                  <div className="border-t border-slate-100 pt-4 mt-2 space-y-4">
                    <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                      Conversation Thread
                    </h4>

                    {messages.length === 0 ? (
                      <div className="text-xs text-slate-400 italic">No previous replies yet.</div>
                    ) : (
                      <div className="space-y-2 max-h-60 overflow-y-auto pr-2">
                        {messages.map((m) => {
                          const isAdmin = m.sender_role === 'ADMIN';
                          const isSystem = m.sender_role === 'SYSTEM';
                          return (
                            <div
                              key={m.id}
                              className={`p-3 rounded-lg text-xs flex flex-col gap-1 ${
                                isAdmin
                                  ? 'bg-emerald-50 border border-emerald-200 ml-8 text-emerald-950'
                                  : isSystem
                                  ? 'bg-slate-100 border border-slate-200 text-slate-600 text-center'
                                  : 'bg-slate-50 border border-slate-200 mr-8 text-slate-800'
                              }`}
                            >
                              <div className="flex items-center justify-between font-semibold text-[11px] text-slate-500">
                                <span>{isAdmin ? 'Admin (Minapur Hub)' : isSystem ? 'System Notice' : 'Customer'}</span>
                                <span>{new Date(m.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                              </div>
                              <p className="whitespace-pre-wrap">{m.message}</p>
                            </div>
                          );
                        })}
                      </div>
                    )}

                    {/* Admin Reply Composer */}
                    <div className="flex gap-2 items-center pt-2">
                      <input
                        type="text"
                        placeholder="Type official admin response to customer..."
                        value={replyText[t.id] || ''}
                        onChange={(e) => setReplyText({ ...replyText, [t.id]: e.target.value })}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') handleSendReply(t.id);
                        }}
                        className="flex-1 px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
                      />
                      <button
                        onClick={() => handleSendReply(t.id)}
                        disabled={isSubmittingReply[t.id] || !(replyText[t.id] || '').trim()}
                        className="px-4 py-2 bg-slate-900 hover:bg-black text-white rounded-lg text-sm font-semibold flex items-center gap-1.5 disabled:opacity-50 transition shrink-0"
                      >
                        <Send className="w-3.5 h-3.5" />
                        Reply
                      </button>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
