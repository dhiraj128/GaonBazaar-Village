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
import type { Language } from '../i18n';
import { translations } from '../i18n';

interface FinancialsLedgerViewProps {
  ledger: SettlementLedger | null;
  codItems: CodReconciliationItem[];
  onRecordCodDeposit: (runnerId: string, amount: number, receiptReference?: string, notes?: string) => Promise<void>;
  onDownloadVendorCsv: () => Promise<void>;
  onDownloadRunnerCsv: () => Promise<void>;
  lang?: Language;
}

export const FinancialsLedgerView: React.FC<FinancialsLedgerViewProps> = ({
  ledger,
  codItems,
  onRecordCodDeposit,
  onDownloadVendorCsv,
  onDownloadRunnerCsv,
  lang = 'en',
}) => {
  const t = translations[lang];
  const [activeTab, setActiveTab] = useState<'cod' | 'vendors' | 'runners'>('cod');

  // COD Deposit Modal State
  const [selectedCodRunner, setSelectedCodRunner] = useState<CodReconciliationItem | null>(null);
  const [depositAmountInput, setDepositAmountInput] = useState<number>(0);
  const [receiptRefInput, setReceiptRefInput] = useState<string>('');
  const [depositNotes, setDepositNotes] = useState<string>('Cash received and reconciled at Muzaffarpur Operations Hub');
  const [isDepositSubmitting, setIsDepositSubmitting] = useState<boolean>(false);

  const handleOpenDepositModal = (item: CodReconciliationItem) => {
    setSelectedCodRunner(item);
    setDepositAmountInput(item.cash_held_inr);
    setReceiptRefInput(`HUB-REC-${Date.now().toString().slice(-6)}`);
  };

  const handleConfirmDeposit = async () => {
    if (!selectedCodRunner) return;
    if (depositAmountInput <= 0) {
      alert(lang === 'hi' ? 'कृपया मान्य जमा राशि दर्ज करें।' : 'Please enter a valid deposit amount.');
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
      alert(lang === 'hi' ? `₹${depositAmountInput} नकद सफलतापूर्वक प्राप्त एवं जमा दर्ज किया गया!` : `Successfully marked ₹${depositAmountInput} cash as Received & Deposited!`);
      setSelectedCodRunner(null);
    } catch (e: any) {
      alert(`${lang === 'hi' ? 'सीओडी जमा त्रुटि' : 'Deposit reconciliation error'}: ${e.message}`);
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
              {t.financialsHeader}
            </h2>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            {t.financialsSub}
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
            {t.codTab} ({codItems.length})
          </button>
          <button
            onClick={() => setActiveTab('vendors')}
            className={`px-3 py-1.5 rounded-lg transition ${
              activeTab === 'vendors'
                ? 'bg-white text-slate-900 shadow-xs'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            {t.vendorPayoutsTab}
          </button>
          <button
            onClick={() => setActiveTab('runners')}
            className={`px-3 py-1.5 rounded-lg transition ${
              activeTab === 'runners'
                ? 'bg-white text-slate-900 shadow-xs'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            {t.runnerPayoutsTab}
          </button>
        </div>
      </div>

      {/* Top Financial Pulse Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1">
            {t.undepositedCod}
          </span>
          <div className="text-2xl font-black text-amber-700">
            ₹{codItems.reduce((acc, c) => acc + c.cash_held_inr, 0).toLocaleString('en-IN')}
          </div>
          <span className="text-[11px] text-amber-600 font-semibold mt-1 block">
            {lang === 'hi'
              ? `${codItems.length} सक्रिय डिलीवरी रनर्स द्वारा धारित`
              : `Across ${codItems.length} active delivery runners`}
          </span>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1">
            {t.vendorSettlementsDue}
          </span>
          <div className="text-2xl font-black text-slate-900">
            ₹{(ledger?.vendor_payouts_due || 0).toLocaleString('en-IN')}
          </div>
          <span className="text-[11px] text-slate-500 font-semibold mt-1 block">
            {lang === 'hi'
              ? 'बिक्री मूल्य घटाव प्लेटफॉर्म कमीशन (शुद्ध देय)'
              : 'Net payout (Order Value minus Platform Commission)'}
          </span>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1">
            {t.runnerFeesDue}
          </span>
          <div className="text-2xl font-black text-slate-900">
            ₹{(ledger?.runner_payouts_due || 0).toLocaleString('en-IN')}
          </div>
          <span className="text-[11px] text-slate-500 font-semibold mt-1 block">
            {lang === 'hi' ? 'पूर्ण की गई ग्रामीण डिलीवरी पर आधारित' : 'Based on completed rural deliveries'}
          </span>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1">
            {t.platformFeesCollected}
          </span>
          <div className="text-2xl font-black text-emerald-700">
            ₹{(ledger?.platform_fee_collected || 0).toLocaleString('en-IN')}
          </div>
          <span className="text-[11px] text-emerald-600 font-semibold mt-1 block">
            {ledger?.total_delivered_orders || 0} {lang === 'hi' ? 'ऑर्डर डिलीवर हुए' : 'orders delivered'}
          </span>
        </div>
      </div>

      {/* SECTION 1: COD Reconciliation */}
      {activeTab === 'cod' && (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
            <div>
              <h3 className="text-sm font-extrabold text-slate-900">
                {lang === 'hi'
                  ? 'रनर सीओडी नकद समाधान (हब वापसी बहीखाता)'
                  : 'Runner COD Cash In Hand (Base Return Reconciliation)'}
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                {lang === 'hi'
                  ? 'जब रनर शिफ्ट पूरी करके लौटते हैं, हब प्रबंधक सटीक नकद दर्ज करते हैं।'
                  : 'Track and reconcile cash held by each specific runner when returning to hub.'}
              </p>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 uppercase text-[10px] font-bold tracking-wider border-b border-slate-200">
                <tr>
                  <th className="px-6 py-3">{lang === 'hi' ? 'डिलीवरी रनर' : 'Runner Partner'}</th>
                  <th className="px-6 py-3">{lang === 'hi' ? 'फ़ोन' : 'Phone'}</th>
                  <th className="px-6 py-3">{lang === 'hi' ? 'डिलीवर सीओडी ऑर्डर' : 'Delivered COD Orders'}</th>
                  <th className="px-6 py-3">{t.exactCashHeld}</th>
                  <th className="px-6 py-3">{t.status}</th>
                  <th className="px-6 py-3 text-right">{t.actions}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
                {codItems.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-12 text-center text-slate-400">
                      <CheckCircle className="w-8 h-8 text-emerald-500 mx-auto mb-2 opacity-60" />
                      {lang === 'hi'
                        ? 'सभी रनर सीओडी नकद स्थानीय हब बहीखाते में जमा हो चुका है।'
                        : 'All runner COD cash has been received & deposited to local hub ledger.'}
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
                        <span className="text-[11px] text-slate-400">{lang === 'hi' ? 'ऑर्डर' : 'orders'}</span>
                      </td>
                      <td className="px-6 py-4">
                        <span className="text-sm font-black text-amber-700">
                          ₹{item.cash_held_inr.toLocaleString('en-IN')}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-800">
                          {lang === 'hi' ? 'नकद धारित' : 'Holding Cash'}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <button
                          onClick={() => handleOpenDepositModal(item)}
                          className="px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg font-bold text-xs shadow-xs transition"
                        >
                          {t.receivedAndDeposited}
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
                {lang === 'hi'
                  ? 'विक्रेता निपटान सारांश (बिक्री मूल्य घटाव ऑनलाइन बैंक सेटलमेंट शुल्क)'
                  : 'Vendor Weekly Settlement Summary (Sales minus Online Bank Settlement Fee)'}
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                {lang === 'hi'
                  ? 'कॉर्पोरेट नेट बैंकिंग (NEFT/RTGS) के लिए थोक बैच फ़ाइल।'
                  : 'Corporate batch file formatted for direct upload to corporate net banking (NEFT/RTGS).'}
              </p>
            </div>

            <button
              onClick={onDownloadVendorCsv}
              className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-xl font-bold text-xs shadow-sm flex items-center space-x-2 transition"
            >
              <Download className="w-4 h-4" />
              <span>{t.exportVendorCsv}</span>
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 uppercase text-[10px] font-bold tracking-wider border-b border-slate-200">
                <tr>
                  <th className="px-6 py-3">{lang === 'hi' ? 'दुकान का नाम' : 'Store Name'}</th>
                  <th className="px-6 py-3">{t.grossSales}</th>
                  <th className="px-6 py-3">{t.platformCommission}</th>
                  <th className="px-6 py-3">{t.netPayoutDue}</th>
                  <th className="px-6 py-3">{lang === 'hi' ? 'पूर्ण ऑर्डर' : 'Delivered Orders'}</th>
                  <th className="px-6 py-3">{lang === 'hi' ? 'लाभार्थी बैंक खाता' : 'Beneficiary A/C'}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
                {(ledger?.vendor_settlements || []).map((v) => (
                  <tr key={v.store_id} className="hover:bg-slate-50/80 transition">
                    <td className="px-6 py-4 font-bold text-slate-900">{v.store_name}</td>
                    <td className="px-6 py-4 text-slate-700">₹{(v.gross_sales || v.total_payout).toFixed(2)}</td>
                    <td className="px-6 py-4 text-slate-500">₹{(v.platform_commission || 0).toFixed(2)}</td>
                    <td className="px-6 py-4 font-black text-emerald-700">₹{v.total_payout.toFixed(2)}</td>
                    <td className="px-6 py-4">{v.order_count} {lang === 'hi' ? 'ऑर्डर' : 'orders'}</td>
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
                {lang === 'hi'
                  ? 'रनर डिलीवरी शुल्क एवं शिफ्ट प्रोत्साहन'
                  : 'Runner Delivery Fees & Shift Bonuses'}
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                {lang === 'hi'
                  ? 'कॉर्पोरेट बैंक खातों में सीधे अपलोड के लिए थोक भुगतान फ़ाइल।'
                  : 'Bulk payout file for direct upload to corporate bank accounts (NEFT/RTGS).'}
              </p>
            </div>

            <button
              onClick={onDownloadRunnerCsv}
              className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-xl font-bold text-xs shadow-sm flex items-center space-x-2 transition"
            >
              <Download className="w-4 h-4" />
              <span>{t.exportRunnerCsv}</span>
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 uppercase text-[10px] font-bold tracking-wider border-b border-slate-200">
                <tr>
                  <th className="px-6 py-3">{lang === 'hi' ? 'डिलीवरी रनर' : 'Runner Partner'}</th>
                  <th className="px-6 py-3">{lang === 'hi' ? 'पूर्ण डिलीवरी' : 'Completed Deliveries'}</th>
                  <th className="px-6 py-3">{lang === 'hi' ? 'अर्जित डिलीवरी शुल्क' : 'Delivery Fees Earned'}</th>
                  <th className="px-6 py-3">{lang === 'hi' ? 'कुल देय राशि' : 'Total Payout Due'}</th>
                  <th className="px-6 py-3">{lang === 'hi' ? 'लाभार्थी खाता' : 'Beneficiary Account'}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
                {(ledger?.runner_settlements || []).map((r) => (
                  <tr key={r.runner_id} className="hover:bg-slate-50/80 transition">
                    <td className="px-6 py-4 font-bold text-slate-900">
                      {r.runner_name || `Runner #${r.runner_id.slice(0, 8)}`}
                    </td>
                    <td className="px-6 py-4">{r.order_count} {lang === 'hi' ? 'डिलीवरी' : 'deliveries'}</td>
                    <td className="px-6 py-4 text-slate-700">₹{(r.delivery_fees || r.total_payout).toFixed(2)}</td>
                    <td className="px-6 py-4 font-black text-emerald-700">₹{r.total_payout.toFixed(2)}</td>
                    <td className="px-6 py-4 font-mono text-[11px] text-slate-500">
                      {r.bank_account || '919876543210'} ({r.ifsc || 'PUNB0004321'})
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* COD Deposit Confirmation Modal */}
      {selectedCodRunner && (
        <div className="fixed inset-0 bg-slate-950/75 z-50 flex items-center justify-center p-4 backdrop-blur-xs">
          <div className="bg-white rounded-3xl max-w-md w-full p-6 space-y-4 shadow-2xl border border-slate-200">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div className="flex items-center space-x-2">
                <Receipt className="w-5 h-5 text-emerald-600" />
                <h4 className="text-sm font-extrabold text-slate-900">
                  {lang === 'hi' ? 'हब नकद जमा समाधान' : 'Record Base Cash Deposit'}
                </h4>
              </div>
              <button
                onClick={() => setSelectedCodRunner(null)}
                className="text-slate-400 hover:text-slate-600"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div className="bg-slate-50 p-3 rounded-xl border border-slate-200">
                <div className="text-slate-500 text-[10px] uppercase font-bold">
                  {lang === 'hi' ? 'रनर विवरण' : 'Runner Information'}
                </div>
                <div className="font-bold text-slate-900 text-sm mt-0.5">
                  {selectedCodRunner.runner_name}
                </div>
                <div className="text-slate-500 text-[11px]">{selectedCodRunner.phone}</div>
              </div>

              <div>
                <label className="text-[10px] font-bold uppercase text-slate-500 block mb-1">
                  {lang === 'hi' ? 'प्राप्त नकद राशि (रुपये)' : 'Exact Cash Received (INR)'}
                </label>
                <input
                  type="number"
                  value={depositAmountInput}
                  onChange={(e) => setDepositAmountInput(parseFloat(e.target.value) || 0)}
                  className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-xl outline-none font-black text-emerald-700 text-base"
                />
              </div>

              <div>
                <label className="text-[10px] font-bold uppercase text-slate-500 block mb-1">
                  {lang === 'hi' ? 'हब रसीद संख्या / संदर्भ' : 'Hub Deposit Receipt / Reference'}
                </label>
                <input
                  type="text"
                  value={receiptRefInput}
                  onChange={(e) => setReceiptRefInput(e.target.value)}
                  className="w-full p-2 bg-slate-50 border border-slate-200 rounded-xl outline-none font-mono text-xs"
                />
              </div>

              <div>
                <label className="text-[10px] font-bold uppercase text-slate-500 block mb-1">
                  {lang === 'hi' ? 'समाधान नोट' : 'Reconciliation Notes'}
                </label>
                <input
                  type="text"
                  value={depositNotes}
                  onChange={(e) => setDepositNotes(e.target.value)}
                  className="w-full p-2 bg-slate-50 border border-slate-200 rounded-xl outline-none text-xs"
                />
              </div>
            </div>

            <div className="pt-2 flex items-center justify-end space-x-2">
              <button
                onClick={() => setSelectedCodRunner(null)}
                className="px-4 py-2 text-xs font-semibold text-slate-600 hover:text-slate-900"
              >
                {t.cancel}
              </button>
              <button
                onClick={handleConfirmDeposit}
                disabled={isDepositSubmitting}
                className="px-5 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-extrabold text-xs rounded-xl shadow-sm transition"
              >
                {t.receivedAndDeposited}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
