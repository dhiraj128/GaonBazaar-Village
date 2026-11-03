import React, { useState } from 'react';
import {
  CircleDollarSign,
  Wallet,
  Download,
  CheckCircle,
  FileSpreadsheet,
  Building,
  CreditCard,
  ShieldAlert,
  ArrowDownToLine,
  Receipt,
  X,
  IndianRupee,
  Lock,
} from 'lucide-react';
import type { SettlementLedger, CodReconciliationItem, AdminRole } from '../types';

interface FinancialsLedgerViewProps {
  ledger: SettlementLedger | null;
  codItems: CodReconciliationItem[];
  userRole?: AdminRole;
  onRecordCodDeposit: (runnerId: string, amount: number, receiptReference?: string, notes?: string) => Promise<void>;
  onDownloadVendorCsv: () => Promise<void>;
  onDownloadRunnerCsv: () => Promise<void>;
}

export const FinancialsLedgerView: React.FC<FinancialsLedgerViewProps> = ({
  ledger,
  codItems,
  userRole = 'super_admin',
  onRecordCodDeposit,
  onDownloadVendorCsv,
  onDownloadRunnerCsv,
}) => {
  const isHubManager = userRole === 'hub_manager';
  const [activeTab, setActiveTab] = useState<'cod' | 'vendors' | 'runners'>('cod');

  // COD Deposit Modal State
  const [selectedCodRunner, setSelectedCodRunner] = useState<CodReconciliationItem | null>(null);
  const [depositAmountInput, setDepositAmountInput] = useState<number>(0);
  const [receiptRefInput, setReceiptRefInput] = useState<string>('');
  const [depositNotes, setDepositNotes] = useState<string>('Cash received and reconciled at Minapur Hub');
  const [isDepositSubmitting, setIsDepositSubmitting] = useState<boolean>(false);

  const handleOpenDepositModal = (item: CodReconciliationItem) => {
    setSelectedCodRunner(item);
    setDepositAmountInput(item.cash_held_inr);
    setReceiptRefInput(`HUB-REC-${Date.now().toString().slice(-6)}`);
  };

  const handleConfirmDeposit = async () => {
    if (!selectedCodRunner) return;
    if (depositAmountInput <= 0) {
      alert('Please enter a valid deposit amount.');
      return;
    }
    setIsDepositSubmitting(true);
    try {
      await onRecordCodDeposit(
        selectedCodRunner.runner_id,
        depositAmountInput,
        receiptRefInput,
        depositNotes
      );
      alert(`Successfully marked ₹${depositAmountInput} cash as Received & Deposited!`);
      setSelectedCodRunner(null);
    } catch (e: any) {
      alert(`Deposit reconciliation error: ${e.message}`);
    } finally {
      setIsDepositSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Module Navigation Header */}
      <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <CircleDollarSign className="w-5 h-5 text-emerald-600" />
            <h2 className="text-sm font-extrabold text-slate-900">
              Financials, Cash Ledger & Corporate Bulk Payouts
            </h2>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Local Hub COD cash deposit workflows & direct NEFT/RTGS corporate bank settlement batches.
          </p>
        </div>

        {/* Tab Switcher */}
        <div className="flex items-center space-x-1 bg-slate-100 p-1 rounded-xl text-xs font-bold">
          <button
            onClick={() => setActiveTab('cod')}
            className={`px-3 py-1.5 rounded-lg transition ${
              activeTab === 'cod'
                ? 'bg-white text-slate-900 shadow-xs'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            COD Reconciliation ({codItems.length})
          </button>
          <button
            onClick={() => setActiveTab('vendors')}
            className={`px-3 py-1.5 rounded-lg transition ${
              activeTab === 'vendors'
                ? 'bg-white text-slate-900 shadow-xs'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Vendor Payouts
          </button>
          <button
            onClick={() => setActiveTab('runners')}
            className={`px-3 py-1.5 rounded-lg transition ${
              activeTab === 'runners'
                ? 'bg-white text-slate-900 shadow-xs'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Runner Payouts
          </button>
        </div>
      </div>

      {/* Top Financial Pulse Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1">
            Undeposited Cash (COD)
          </span>
          <div className="text-2xl font-black text-amber-700">
            ₹{codItems.reduce((acc, c) => acc + c.cash_held_inr, 0).toLocaleString('en-IN')}
          </div>
          <span className="text-[11px] text-amber-600 font-semibold mt-1 block">
            Across {codItems.length} active delivery runners
          </span>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1">
            Vendor Settlements Due
          </span>
          <div className="text-2xl font-black text-slate-900">
            ₹{(ledger?.vendor_payouts_due || 0).toLocaleString('en-IN')}
          </div>
          <span className="text-[11px] text-slate-500 font-semibold mt-1 block">
            Net after 0% platform commission
          </span>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1">
            Runner Delivery Fees Due
          </span>
          <div className="text-2xl font-black text-slate-900">
            ₹{(ledger?.runner_payouts_due || 0).toLocaleString('en-IN')}
          </div>
          <span className="text-[11px] text-slate-500 font-semibold mt-1 block">
            Based on completed rural deliveries
          </span>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1">
            Platform Fees Collected
          </span>
          <div className="text-2xl font-black text-emerald-700">
            ₹{(ledger?.platform_fee_collected || 0).toLocaleString('en-IN')}
          </div>
          <span className="text-[11px] text-emerald-600 font-semibold mt-1 block">
            {ledger?.total_delivered_orders || 0} orders delivered
          </span>
        </div>
      </div>

      {/* SECTION 1: COD Reconciliation (Available to Hub Managers & Super Admins) */}
      {activeTab === 'cod' && (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
            <div>
              <h3 className="text-sm font-extrabold text-slate-900">
                Runner COD Cash In Hand (Base Return Reconciliation)
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                When runners return to base at end of shift, Hub Managers record exact cash received and mark status as 'Received & Deposited'.
              </p>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 uppercase text-[10px] font-bold tracking-wider border-b border-slate-200">
                <tr>
                  <th className="px-6 py-3">Runner Partner</th>
                  <th className="px-6 py-3">Phone</th>
                  <th className="px-6 py-3">Delivered COD Orders</th>
                  <th className="px-6 py-3">Exact Cash Held (INR)</th>
                  <th className="px-6 py-3">Ledger Status</th>
                  <th className="px-6 py-3 text-right">Hub Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
                {codItems.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-12 text-center text-slate-400">
                      <CheckCircle className="w-8 h-8 text-emerald-500 mx-auto mb-2 opacity-60" />
                      All runner COD cash has been received & deposited to local hub ledger.
                    </td>
                  </tr>
                ) : (
                  codItems.map((item) => (
                    <tr key={item.runner_id} className="hover:bg-slate-50/80 transition">
                      <td className="px-6 py-4">
                        <div className="font-bold text-slate-900">{item.runner_name}</div>
                        <div className="text-[10px] font-mono text-slate-400">
                          ID: {item.runner_id.slice(0, 8)}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-slate-800 font-semibold">{item.phone}</td>
                      <td className="px-6 py-4">
                        <span className="font-bold text-slate-900">
                          {item.undeposited_orders_count}
                        </span>{' '}
                        <span className="text-[11px] text-slate-400">orders</span>
                      </td>
                      <td className="px-6 py-4">
                        <span className="text-sm font-black text-amber-700">
                          ₹{item.cash_held_inr.toLocaleString('en-IN')}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-800">
                          Holding Cash
                        </span>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <button
                          onClick={() => handleOpenDepositModal(item)}
                          className="px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg font-bold text-xs shadow-xs transition"
                        >
                          Received & Deposited
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* SECTION 2: Vendor Payouts & Batch CSV Export */}
      {activeTab === 'vendors' && (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-100 flex flex-col md:flex-row md:items-center justify-between gap-3">
            <div>
              <h3 className="text-sm font-extrabold text-slate-900">
                Vendor Weekly Settlement Summary (Sales minus Commission)
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Corporate batch file formatted for direct upload to corporate net banking (NEFT/RTGS).
              </p>
            </div>

            {isHubManager ? (
              <div className="flex items-center gap-1.5 text-xs text-amber-800 bg-amber-50 px-3 py-1.5 rounded-xl border border-amber-200">
                <Lock className="w-4 h-4 text-amber-600" />
                <span>Super Admin privilege required to export bulk payouts</span>
              </div>
            ) : (
              <button
                onClick={onDownloadVendorCsv}
                className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-xl font-bold text-xs shadow-sm flex items-center space-x-2 transition"
              >
                <Download className="w-4 h-4" />
                <span>Export Batch CSV (NEFT/RTGS)</span>
              </button>
            )}
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 uppercase text-[10px] font-bold tracking-wider border-b border-slate-200">
                <tr>
                  <th className="px-6 py-3">Store Name</th>
                  <th className="px-6 py-3">Gross Sales</th>
                  <th className="px-6 py-3">Platform Commission</th>
                  <th className="px-6 py-3">Net Payout Due</th>
                  <th className="px-6 py-3">Delivered Orders</th>
                  <th className="px-6 py-3">Beneficiary A/C</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
                {(ledger?.vendor_settlements || []).map((v) => (
                  <tr key={v.store_id} className="hover:bg-slate-50/80 transition">
                    <td className="px-6 py-4 font-bold text-slate-900">{v.store_name}</td>
                    <td className="px-6 py-4 text-slate-700">₹{(v.gross_sales || v.total_payout).toFixed(2)}</td>
                    <td className="px-6 py-4 text-slate-500">₹{(v.platform_commission || 0).toFixed(2)}</td>
                    <td className="px-6 py-4 font-black text-emerald-700">₹{v.total_payout.toFixed(2)}</td>
                    <td className="px-6 py-4">{v.order_count} orders</td>
                    <td className="px-6 py-4 font-mono text-[11px] text-slate-500">
                      {v.bank_account || '918237465019'} ({v.ifsc || 'SBIN0001234'})
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* SECTION 3: Runner Payouts & Batch CSV Export */}
      {activeTab === 'runners' && (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-100 flex flex-col md:flex-row md:items-center justify-between gap-3">
            <div>
              <h3 className="text-sm font-extrabold text-slate-900">
                Runner Delivery Fees & Shift Bonuses
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Bulk payout file for direct upload to corporate bank accounts (NEFT/RTGS).
              </p>
            </div>

            {isHubManager ? (
              <div className="flex items-center gap-1.5 text-xs text-amber-800 bg-amber-50 px-3 py-1.5 rounded-xl border border-amber-200">
                <Lock className="w-4 h-4 text-amber-600" />
                <span>Super Admin privilege required to export bulk payouts</span>
              </div>
            ) : (
              <button
                onClick={onDownloadRunnerCsv}
                className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-xl font-bold text-xs shadow-sm flex items-center space-x-2 transition"
              >
                <Download className="w-4 h-4" />
                <span>Export Runner Batch CSV</span>
              </button>
            )}
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 uppercase text-[10px] font-bold tracking-wider border-b border-slate-200">
                <tr>
                  <th className="px-6 py-3">Runner Partner</th>
                  <th className="px-6 py-3">Completed Deliveries</th>
                  <th className="px-6 py-3">Delivery Fees Earned</th>
                  <th className="px-6 py-3">Total Payout Due</th>
                  <th className="px-6 py-3">Beneficiary Account</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
                {(ledger?.runner_settlements || []).map((r) => (
                  <tr key={r.runner_id} className="hover:bg-slate-50/80 transition">
                    <td className="px-6 py-4 font-bold text-slate-900">
                      {r.runner_name || `Runner #${r.runner_id.slice(0, 8)}`}
                    </td>
                    <td className="px-6 py-4">{r.order_count} deliveries</td>
                    <td className="px-6 py-4 text-slate-700">₹{(r.delivery_fees || r.total_payout).toFixed(2)}</td>
                    <td className="px-6 py-4 font-black text-emerald-700">₹{r.total_payout.toFixed(2)}</td>
                    <td className="px-6 py-4 font-mono text-[11px] text-slate-500">
                      {r.bank_account || '50100492817291'} ({r.ifsc || 'PUNB0182300'})
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* MODAL: "Received & Deposited" COD Cash Reconciliation */}
      {selectedCodRunner && (
        <div className="fixed inset-0 bg-slate-950/75 z-50 flex items-center justify-center p-4 backdrop-blur-xs animate-in fade-in duration-150">
          <div className="bg-white rounded-3xl max-w-md w-full p-6 space-y-5 shadow-2xl border border-slate-200">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div className="flex items-center space-x-2">
                <Receipt className="w-5 h-5 text-emerald-600" />
                <h3 className="text-sm font-black text-slate-900 uppercase tracking-wide">
                  Record Hub COD Cash Deposit
                </h3>
              </div>
              <button
                onClick={() => setSelectedCodRunner(null)}
                className="text-slate-400 hover:text-slate-700"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-200">
                <div className="text-slate-500 font-semibold">Runner Name:</div>
                <div className="text-sm font-extrabold text-slate-900">
                  {selectedCodRunner.runner_name}
                </div>
                <div className="text-slate-500 mt-1">
                  Cash Held: <strong className="text-amber-700">₹{selectedCodRunner.cash_held_inr}</strong> ({selectedCodRunner.undeposited_orders_count} orders)
                </div>
              </div>

              <div>
                <label className="text-[11px] font-bold text-slate-600 block mb-1">
                  Amount Received & Deposited (INR):
                </label>
                <div className="flex items-center space-x-2">
                  <span className="text-xs font-bold text-slate-500">₹</span>
                  <input
                    type="number"
                    value={depositAmountInput}
                    onChange={(e) => setDepositAmountInput(parseFloat(e.target.value) || 0)}
                    className="w-full text-xs p-2.5 bg-slate-50 border border-slate-200 rounded-xl outline-none font-bold"
                  />
                </div>
              </div>

              <div>
                <label className="text-[11px] font-bold text-slate-600 block mb-1">
                  Hub Receipt Reference:
                </label>
                <input
                  type="text"
                  value={receiptRefInput}
                  onChange={(e) => setReceiptRefInput(e.target.value)}
                  className="w-full text-xs p-2.5 bg-slate-50 border border-slate-200 rounded-xl outline-none font-mono"
                />
              </div>

              <div>
                <label className="text-[11px] font-bold text-slate-600 block mb-1">
                  Reconciliation Notes:
                </label>
                <textarea
                  value={depositNotes}
                  onChange={(e) => setDepositNotes(e.target.value)}
                  rows={2}
                  className="w-full text-xs p-2.5 bg-slate-50 border border-slate-200 rounded-xl outline-none"
                />
              </div>
            </div>

            <div className="flex items-center justify-end space-x-2 pt-2 border-t border-slate-100">
              <button
                onClick={() => setSelectedCodRunner(null)}
                className="px-3.5 py-2 text-xs font-semibold text-slate-600 hover:text-slate-800"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirmDeposit}
                disabled={isDepositSubmitting}
                className="px-5 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-black text-xs rounded-xl shadow-xs transition"
              >
                Confirm Deposit & Clear Cash
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
