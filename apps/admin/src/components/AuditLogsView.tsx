import React from 'react';
import { FileText, Clock } from 'lucide-react';
import type { AuditLogItem } from '../types';

interface AuditLogsViewProps {
  logs: AuditLogItem[];
}

export const AuditLogsView: React.FC<AuditLogsViewProps> = ({ logs }) => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-800">Security & Operational Audit Logs</h2>
          <p className="text-xs text-slate-500 mt-1">
            Immutable system logs tracking administrative actions, approvals, and order interventions.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold px-2.5 py-1 bg-slate-100 text-slate-700 rounded border border-slate-200">
            Total Records: {logs.length}
          </span>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-xs border border-slate-200 overflow-hidden">
        {logs.length === 0 ? (
          <div className="p-8 text-center text-slate-400 text-xs">
            No audit events recorded yet.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead className="bg-slate-50 border-b border-slate-200 text-xs font-semibold text-slate-600 uppercase tracking-wider">
                <tr>
                  <th className="py-3 px-4">Timestamp</th>
                  <th className="py-3 px-4">Action</th>
                  <th className="py-3 px-4">Actor</th>
                  <th className="py-3 px-4">Target Entity</th>
                  <th className="py-3 px-4">Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {logs.map((log) => (
                  <tr key={log.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-3.5 px-4 text-xs text-slate-500 whitespace-nowrap flex items-center gap-1.5">
                      <Clock className="w-3.5 h-3.5 text-slate-400" />
                      {log.created_at
                        ? new Date(log.created_at).toLocaleString('en-IN', {
                            timeZone: 'Asia/Kolkata',
                          })
                        : 'Recent'}
                    </td>
                    <td className="py-3.5 px-4 font-mono text-xs font-bold text-slate-800">
                      <span className="bg-slate-100 px-2 py-0.5 rounded border border-slate-300">
                        {log.action}
                      </span>
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
                        {log.actor_role || 'SYSTEM'}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-xs text-slate-600">
                      {log.target_type} ({log.target_id})
                    </td>
                    <td className="py-3.5 px-4 text-xs text-slate-700 max-w-md truncate" title={log.details}>
                      {log.details || '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
