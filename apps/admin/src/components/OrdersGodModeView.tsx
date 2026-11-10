import React, { useState } from 'react';
import {
  ShoppingBag,
  Clock,
  User,
  Store,
  Bike,
  AlertCircle,
  XCircle,
  RotateCcw,
  UserCheck,
  Package,
  CheckCircle2,
  Filter,
  Search,
  ExternalLink,
  ShieldAlert,
  X,
  CreditCard,
  MapPin,
  ArrowRight,
} from 'lucide-react';
import type { OrderItemRecord, RiderMapPin } from '../types';
import type { Language } from '../i18n';
import { translations } from '../i18n';

interface OrdersGodModeViewProps {
  orders: OrderItemRecord[];
  riders: RiderMapPin[];
  onUpdateStatus: (orderId: string, status: string, cashCollected?: boolean) => Promise<void>;
  onGodModeCancel: (orderId: string, reason?: string, autoRefund?: boolean) => Promise<void>;
  onGodModeRefund: (orderId: string, amount: number, reason?: string) => Promise<void>;
  onGodModeReassignRunner: (orderId: string, runnerId: string, notes?: string) => Promise<void>;
  onGodModeOverrideStock: (orderId: string, productId: string, isAvailable: boolean) => Promise<void>;
  lang?: Language;
}

export const OrdersGodModeView: React.FC<OrdersGodModeViewProps> = ({
  orders,
  riders,
  onUpdateStatus,
  onGodModeCancel,
  onGodModeRefund,
  onGodModeReassignRunner,
  onGodModeOverrideStock,
  lang = 'en',
}) => {
  const t = translations[lang];
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedOrder, setSelectedOrder] = useState<OrderItemRecord | null>(null);

  // God Mode Action States
  const [isGodActionLoading, setIsGodActionLoading] = useState<boolean>(false);
  const [refundAmountInput, setRefundAmountInput] = useState<number>(0);
  const [refundReasonInput, setRefundReasonInput] = useState<string>('God Mode Instant Settlement');
  const [selectedReassignRunnerId, setSelectedReassignRunnerId] = useState<string>('');
  const [reassignNotes, setReassignNotes] = useState<string>('Reassigned by Super Admin');

  const filteredOrders = orders.filter((order) => {
    const matchesFilter = statusFilter === 'ALL' || order.status === statusFilter;
    const matchesQuery =
      order.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      order.customer_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      order.store_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      order.customer_phone?.includes(searchQuery);
    return matchesFilter && matchesQuery;
  });

  const getStatusBadge = (status: OrderItemRecord['status']) => {
    switch (status) {
      case 'PLACED':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'ACCEPTED':
        return 'bg-amber-100 text-amber-800 border-amber-200';
      case 'PACKED':
        return 'bg-indigo-100 text-indigo-800 border-indigo-200';
      case 'RUNNER_ASSIGNED':
        return 'bg-purple-100 text-purple-800 border-purple-200';
      case 'PICKED_UP':
        return 'bg-cyan-100 text-cyan-800 border-cyan-200';
      case 'OUT_FOR_DELIVERY':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'DELIVERED':
        return 'bg-emerald-100 text-emerald-800 border-emerald-200';
      case 'CANCELLED':
        return 'bg-rose-100 text-rose-800 border-rose-200';
      default:
        return 'bg-slate-100 text-slate-800 border-slate-200';
    }
  };

  const handleOpenOrder = (order: OrderItemRecord) => {
    setSelectedOrder(order);
    setRefundAmountInput(order.total_amount);
  };

  const handleExecuteCancel = async () => {
    if (!selectedOrder) return;
    if (!window.confirm(`${t.forceCancelConfirm} (#${selectedOrder.id.slice(0, 8)})`)) return;
    setIsGodActionLoading(true);
    try {
      await onGodModeCancel(selectedOrder.id, 'Cancelled via God Mode', true);
      alert(lang === 'hi' ? `ऑर्डर #${selectedOrder.id.slice(0, 8)} रद्द कर दिया गया।` : `Order #${selectedOrder.id.slice(0, 8)} cancelled successfully.`);
      setSelectedOrder(null);
    } catch (e: any) {
      alert(`${lang === 'hi' ? 'रद्दीकरण विफल' : 'Cancellation failed'}: ${e.message}`);
    } finally {
      setIsGodActionLoading(false);
    }
  };

  const handleExecuteRefund = async () => {
    if (!selectedOrder) return;
    if (refundAmountInput <= 0) {
      alert(lang === 'hi' ? 'कृपया मान्य रिफंड राशि दर्ज करें।' : 'Please enter a valid refund amount.');
      return;
    }
    setIsGodActionLoading(true);
    try {
      await onGodModeRefund(selectedOrder.id, refundAmountInput, refundReasonInput);
      alert(lang === 'hi' ? `₹${refundAmountInput} का त्वरित रिफंड जारी किया गया।` : `Instant refund of ₹${refundAmountInput} issued.`);
      setSelectedOrder(null);
    } catch (e: any) {
      alert(`${lang === 'hi' ? 'रिफंड त्रुटि' : 'Refund error'}: ${e.message}`);
    } finally {
      setIsGodActionLoading(false);
    }
  };

  const handleExecuteReassign = async () => {
    if (!selectedOrder || !selectedReassignRunnerId) {
      alert(lang === 'hi' ? 'कृपया स्थानापन्न रनर चुनें।' : 'Please select a runner to reassign.');
      return;
    }
    setIsGodActionLoading(true);
    try {
      await onGodModeReassignRunner(selectedOrder.id, selectedReassignRunnerId, reassignNotes);
      alert(lang === 'hi' ? 'रनर सफलतापूर्वक पुनः सौंपा गया।' : 'Runner reassigned successfully.');
      setSelectedOrder(null);
    } catch (e: any) {
      alert(`${lang === 'hi' ? 'रनर पुनः सौंपने में त्रुटि' : 'Reassign error'}: ${e.message}`);
    } finally {
      setIsGodActionLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header & Filters */}
      <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <ShoppingBag className="w-5 h-5 text-emerald-600" />
            <h2 className="text-sm font-extrabold text-slate-900">
              {t.liveOrdersHeader}
            </h2>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            {t.liveOrdersSub}
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder={lang === 'hi' ? 'आईडी, ग्राहक या दुकान से खोजें...' : 'Search by ID, customer, store...'}
              className="text-xs pl-9 pr-3 py-2 bg-slate-50 border border-slate-200 rounded-lg outline-none focus:bg-white focus:border-emerald-500"
            />
          </div>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="text-xs bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 font-bold outline-none"
          >
            <option value="ALL">{lang === 'hi' ? `सभी स्थितियां (${orders.length})` : `All Statuses (${orders.length})`}</option>
            <option value="PLACED">Placed</option>
            <option value="ACCEPTED">Accepted</option>
            <option value="PACKED">Packed</option>
            <option value="RUNNER_ASSIGNED">Runner Assigned</option>
            <option value="PICKED_UP">Picked Up</option>
            <option value="OUT_FOR_DELIVERY">Out for Delivery</option>
            <option value="DELIVERED">Delivered</option>
            <option value="CANCELLED">Cancelled</option>
          </select>
        </div>
      </div>

      {/* Real-Time Live Order Feed Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-500 uppercase text-[10px] font-bold tracking-wider border-b border-slate-200">
              <tr>
                <th className="px-5 py-3">{t.orderId}</th>
                <th className="px-5 py-3">{t.lifecycle}</th>
                <th className="px-5 py-3">{t.customer}</th>
                <th className="px-5 py-3">{t.vendor}</th>
                <th className="px-5 py-3">{t.runner}</th>
                <th className="px-5 py-3">{t.status}</th>
                <th className="px-5 py-3">{lang === 'hi' ? 'राशि' : 'Amount'}</th>
                <th className="px-5 py-3 text-right">{t.godModeBtn}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
              {filteredOrders.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-6 py-12 text-center text-slate-400">
                    {lang === 'hi' ? 'वर्तमान फ़िल्टर मानदंडों से कोई ऑर्डर मेल नहीं खाता।' : 'No orders match current filter criteria.'}
                  </td>
                </tr>
              ) : (
                filteredOrders.map((order) => (
                  <tr
                    key={order.id}
                    onClick={() => handleOpenOrder(order)}
                    className="hover:bg-slate-50/80 transition cursor-pointer"
                  >
                    <td className="px-5 py-3.5">
                      <span className="font-mono font-bold text-slate-900 block">
                        #{order.id.slice(0, 8)}
                      </span>
                      <span className="text-[10px] text-slate-400">
                        {order.items_count} {lang === 'hi' ? 'आइटम' : 'items'} ({order.payment_mode})
                      </span>
                    </td>
                    <td className="px-5 py-3.5">
                      {/* Explicit 3-Way Lifecycle display: Customer ID -> Vendor ID -> Runner ID */}
                      <div className="flex items-center space-x-1 font-mono text-[10px] font-bold text-slate-700 bg-slate-100 px-2 py-1 rounded-md">
                        <span className="text-blue-700" title={`Customer: ${order.customer_id}`}>
                          C:{order.customer_id ? order.customer_id.slice(0, 4) : 'Cust'}
                        </span>
                        <ArrowRight className="w-3 h-3 text-slate-400" />
                        <span className="text-amber-700" title={`Vendor: ${order.store_id}`}>
                          V:{order.store_id ? order.store_id.slice(0, 4) : 'Vend'}
                        </span>
                        <ArrowRight className="w-3 h-3 text-slate-400" />
                        <span className="text-emerald-700" title={`Runner: ${order.runner_id || 'None'}`}>
                          R:{order.runner_id ? order.runner_id.slice(0, 4) : 'None'}
                        </span>
                      </div>
                    </td>
                    <td className="px-5 py-3.5">
                      <div className="font-bold text-slate-900">{order.customer_name || 'Customer'}</div>
                      <div className="text-[11px] text-slate-500">{order.delivery_village || 'Muzaffarpur'}</div>
                    </td>
                    <td className="px-5 py-3.5">
                      <div className="font-bold text-slate-800">{order.store_name}</div>
                    </td>
                    <td className="px-5 py-3.5">
                      <div className="font-semibold text-slate-800">
                        {order.runner_name || (lang === 'hi' ? 'असाइन नहीं' : 'Unassigned')}
                      </div>
                    </td>
                    <td className="px-5 py-3.5">
                      <span
                        className={`inline-block px-2 py-0.5 rounded-full text-[10px] font-bold border ${getStatusBadge(
                          order.status
                        )}`}
                      >
                        {order.status}
                      </span>
                    </td>
                    <td className="px-5 py-3.5">
                      <span className="font-bold text-slate-900">₹{order.total_amount}</span>
                    </td>
                    <td className="px-5 py-3.5 text-right">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleOpenOrder(order);
                        }}
                        className="px-2.5 py-1 text-[11px] font-extrabold bg-slate-900 hover:bg-slate-800 text-white rounded-lg shadow-xs transition"
                      >
                        {t.godModeBtn}
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* MODAL: Super Admin God Mode Powers */}
      {selectedOrder && (
        <div className="fixed inset-0 bg-slate-950/75 z-50 flex items-center justify-center p-4 backdrop-blur-xs animate-in fade-in duration-150">
          <div className="bg-white rounded-3xl max-w-3xl w-full max-h-[92vh] overflow-y-auto shadow-2xl border border-slate-200">
            {/* Header */}
            <div className="px-6 py-4 bg-slate-900 text-white flex items-center justify-between sticky top-0 z-10">
              <div className="flex items-center space-x-2.5">
                <ShieldAlert className="w-5 h-5 text-amber-400" />
                <div>
                  <h3 className="text-sm font-black uppercase tracking-wide">
                    {lang === 'hi' ? 'सुपर एडमिन गॉड मोड — ऑर्डर' : 'Super Admin God Mode — Order'} #{selectedOrder.id.slice(0, 8)}
                  </h3>
                  <span className="text-[11px] text-slate-300">
                    {lang === 'hi'
                      ? 'गहन लेन-देन नियंत्रण: ऑर्डर रद्द करें, तत्काल रिफंड दें एवं स्थानापन्न रनर सौंपें।'
                      : 'Transactional override: Force cancel, issue refund & reassign runner.'}
                  </span>
                </div>
              </div>
              <button
                onClick={() => setSelectedOrder(null)}
                className="text-slate-400 hover:text-white p-1"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Order Details Body */}
            <div className="p-6 space-y-6">
              {/* Order Full Lifecycle Chain Card */}
              <div className="p-4 bg-slate-950 rounded-2xl text-white space-y-2">
                <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-400 block">
                  {lang === 'hi' ? '3-मार्गी ऑर्डर रूटिंग जीवनचक्र' : '3-Way Order Routing Lifecycle (Customer ➔ Vendor ➔ Runner)'}
                </span>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
                  <div className="bg-slate-900 p-2.5 rounded-xl border border-slate-800">
                    <span className="text-[10px] text-slate-400 block">Customer ID:</span>
                    <span className="font-mono font-bold text-blue-400 break-all">{selectedOrder.customer_id}</span>
                    <div className="text-[11px] text-slate-300 mt-1">{selectedOrder.customer_name} ({selectedOrder.delivery_village})</div>
                  </div>
                  <div className="bg-slate-900 p-2.5 rounded-xl border border-slate-800">
                    <span className="text-[10px] text-slate-400 block">Vendor ID:</span>
                    <span className="font-mono font-bold text-amber-400 break-all">{selectedOrder.store_id}</span>
                    <div className="text-[11px] text-slate-300 mt-1">{selectedOrder.store_name}</div>
                  </div>
                  <div className="bg-slate-900 p-2.5 rounded-xl border border-slate-800">
                    <span className="text-[10px] text-slate-400 block">Runner ID:</span>
                    <span className="font-mono font-bold text-emerald-400 break-all">
                      {selectedOrder.runner_id || 'UNASSIGNED'}
                    </span>
                    <div className="text-[11px] text-slate-300 mt-1">{selectedOrder.runner_name || 'Awaiting runner dispatch'}</div>
                  </div>
                </div>
              </div>

              {/* Order Overview Card */}
              <div className="bg-slate-50 p-4 rounded-2xl border border-slate-200 grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
                <div>
                  <span className="text-[10px] text-slate-400 uppercase font-bold block">{t.status}</span>
                  <span className="font-extrabold text-slate-900">{selectedOrder.status}</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 uppercase font-bold block">{lang === 'hi' ? 'भुगतान' : 'Payment'}</span>
                  <span className="font-bold text-slate-900">
                    {selectedOrder.payment_mode} ({selectedOrder.payment_status})
                  </span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 uppercase font-bold block">{lang === 'hi' ? 'कुल राशि' : 'Total Amount'}</span>
                  <span className="font-black text-slate-900 text-sm">₹{selectedOrder.total_amount}</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 uppercase font-bold block">Delivery OTP</span>
                  <span className="font-mono font-extrabold text-emerald-700 text-sm">
                    {selectedOrder.delivery_otp}
                  </span>
                </div>
              </div>

              {/* Items List with Stock Override Button */}
              <div>
                <h4 className="text-xs font-black text-slate-800 uppercase tracking-wider mb-2">
                  {lang === 'hi' ? 'ऑर्डर आइटम एवं स्टॉक ओवरराइड' : 'Order Items & Stock Override'}
                </h4>
                <div className="bg-white rounded-xl border border-slate-200 divide-y divide-slate-100 text-xs">
                  {(selectedOrder.items || []).map((item) => (
                    <div key={item.id} className="p-3 flex items-center justify-between">
                      <div>
                        <span className="font-bold text-slate-900">{item.name}</span>
                        <span className="text-slate-400 ml-2">x{item.quantity}</span>
                      </div>
                      <div className="flex items-center space-x-3">
                        <span className="font-bold text-slate-800">₹{item.total_price}</span>
                        <button
                          onClick={() => {
                            if (window.confirm(lang === 'hi' ? `क्या '${item.name}' को आउट ऑफ स्टॉक चिह्नित करना चाहते हैं?` : `Mark '${item.name}' OUT OF STOCK at ${selectedOrder.store_name}?`)) {
                              onGodModeOverrideStock(selectedOrder.id, item.product_id, false);
                              alert(lang === 'hi' ? 'उत्पाद स्टॉक समाप्त चिह्नित किया गया!' : `Product marked out of stock!`);
                            }
                          }}
                          className="px-2 py-1 text-[10px] font-bold text-rose-700 bg-rose-50 hover:bg-rose-100 rounded border border-rose-200"
                        >
                          {t.markOutOfStock}
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* God Mode Super Powers Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Power 1: Manually Re-assign Runner */}
                <div className="bg-purple-50/70 border border-purple-200 p-4 rounded-2xl space-y-3">
                  <div className="flex items-center space-x-2 text-purple-950 font-bold text-xs">
                    <Bike className="w-4 h-4 text-purple-600" />
                    <span>{t.reassignRunner}</span>
                  </div>
                  <p className="text-[11px] text-purple-800 leading-tight">
                    {lang === 'hi'
                      ? 'यदि वर्तमान रनर दुर्घटनाग्रस्त या ऑफ़लाइन है, तो तत्काल सक्रिय राइडर को सौंपें।'
                      : 'If current runner is stuck or facing an emergency, re-route to an active idle rider.'}
                  </p>
                  <select
                    value={selectedReassignRunnerId}
                    onChange={(e) => setSelectedReassignRunnerId(e.target.value)}
                    className="w-full text-xs p-2.5 bg-white border border-purple-300 rounded-xl outline-none"
                  >
                    <option value="">{t.selectReplacementRunner}</option>
                    {riders.map((r) => (
                      <option key={r.runner_id} value={r.runner_id}>
                        {r.name} ({r.state} — {r.vehicle_type})
                      </option>
                    ))}
                  </select>
                  <button
                    onClick={handleExecuteReassign}
                    disabled={isGodActionLoading || !selectedReassignRunnerId}
                    className="w-full py-2 bg-purple-600 hover:bg-purple-700 text-white font-bold text-xs rounded-xl shadow-xs transition"
                  >
                    {t.reassignBtn}
                  </button>
                </div>

                {/* Power 2: Issue Instant Refund */}
                <div className="bg-emerald-50/70 border border-emerald-200 p-4 rounded-2xl space-y-3">
                  <div className="flex items-center space-x-2 text-emerald-950 font-bold text-xs">
                    <RotateCcw className="w-4 h-4 text-emerald-600" />
                    <span>{t.issueRefund}</span>
                  </div>
                  <p className="text-[11px] text-emerald-800 leading-tight">
                    {lang === 'hi'
                      ? 'गेटवे एकीकरण के माध्यम से ग्राहक को तत्काल रिफंड जारी करें।'
                      : 'Instantly credit customer account via payment gateway integration.'}
                  </p>
                  <div className="flex items-center space-x-2">
                    <span className="text-xs font-bold text-slate-500">₹</span>
                    <input
                      type="number"
                      value={refundAmountInput}
                      onChange={(e) => setRefundAmountInput(parseFloat(e.target.value) || 0)}
                      className="w-full text-xs p-2 bg-white border border-emerald-300 rounded-xl outline-none font-bold"
                    />
                  </div>
                  <button
                    onClick={handleExecuteRefund}
                    disabled={isGodActionLoading}
                    className="w-full py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs rounded-xl shadow-xs transition"
                  >
                    {t.issueRefund}
                  </button>
                </div>
              </div>

              {/* Power 3: Force Cancel Order */}
              <div className="p-4 bg-rose-50 border border-rose-200 rounded-2xl flex items-center justify-between">
                <div>
                  <h5 className="text-xs font-extrabold text-rose-950">
                    {t.forceCancel}
                  </h5>
                  <p className="text-[11px] text-rose-700">
                    {lang === 'hi'
                      ? 'स्थिति को CANCELLED में बदलता है और स्वचालित रूप से पूर्ण रिफंड जारी करता है।'
                      : 'Changes status to CANCELLED and triggers instant automated refund logic.'}
                  </p>
                </div>
                <button
                  onClick={handleExecuteCancel}
                  disabled={isGodActionLoading}
                  className="px-4 py-2 bg-rose-600 hover:bg-rose-700 text-white font-bold text-xs rounded-xl shadow-xs transition"
                >
                  {t.forceCancel}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
