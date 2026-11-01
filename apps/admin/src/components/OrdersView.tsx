import { useState } from 'react';
import { Search } from 'lucide-react';
import type { OrderItemRecord } from '../types';

interface OrdersViewProps {
  orders: OrderItemRecord[];
  onUpdateStatus: (id: string, status: OrderItemRecord['status']) => Promise<void>;
}

export const OrdersView: React.FC<OrdersViewProps> = ({ orders, onUpdateStatus }) => {
  const [filter, setFilter] = useState<'all' | 'active' | 'DELIVERED' | 'CANCELLED'>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [updatingId, setUpdatingId] = useState<string | null>(null);

  const filteredOrders = orders.filter((o) => {
    if (filter === 'active' && (o.status === 'DELIVERED' || o.status === 'CANCELLED')) return false;
    if (filter === 'DELIVERED' && o.status !== 'DELIVERED') return false;
    if (filter === 'CANCELLED' && o.status !== 'CANCELLED') return false;
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      return (
        o.id.toLowerCase().includes(term) ||
        o.store_name.toLowerCase().includes(term) ||
        o.delivery_otp.includes(term)
      );
    }
    return true;
  });

  const handleNextStatus = async (order: OrderItemRecord) => {
    const sequence: OrderItemRecord['status'][] = [
      'PLACED',
      'ACCEPTED',
      'PACKED',
      'RUNNER_ASSIGNED',
      'PICKED_UP',
      'OUT_FOR_DELIVERY',
      'DELIVERED',
    ];
    const currentIndex = sequence.indexOf(order.status);
    if (currentIndex >= 0 && currentIndex < sequence.length - 1) {
      const nextStatus = sequence[currentIndex + 1];
      setUpdatingId(order.id);
      try {
        await onUpdateStatus(order.id, nextStatus);
      } finally {
        setUpdatingId(null);
      }
    }
  };

  const getStatusBadge = (status: OrderItemRecord['status']) => {
    switch (status) {
      case 'DELIVERED':
        return 'bg-emerald-100 text-emerald-800 border-emerald-300';
      case 'OUT_FOR_DELIVERY':
        return 'bg-blue-100 text-blue-800 border-blue-300';
      case 'PICKED_UP':
      case 'RUNNER_ASSIGNED':
        return 'bg-indigo-100 text-indigo-800 border-indigo-300';
      case 'PACKED':
      case 'ACCEPTED':
        return 'bg-amber-100 text-amber-800 border-amber-300';
      case 'PLACED':
        return 'bg-purple-100 text-purple-800 border-purple-300';
      case 'CANCELLED':
        return 'bg-rose-100 text-rose-800 border-rose-300';
      default:
        return 'bg-slate-100 text-slate-800 border-slate-300';
    }
  };

  return (
    <div className="space-y-6">
      {/* Search & Tabs */}
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
            All Orders ({orders.length})
          </button>
          <button
            onClick={() => setFilter('active')}
            className={`px-4 py-2 rounded-lg text-xs font-bold transition ${
              filter === 'active'
                ? 'bg-blue-600 text-white'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            Active Pipeline ({orders.filter((o) => o.status !== 'DELIVERED' && o.status !== 'CANCELLED').length})
          </button>
          <button
            onClick={() => setFilter('DELIVERED')}
            className={`px-4 py-2 rounded-lg text-xs font-bold transition ${
              filter === 'DELIVERED'
                ? 'bg-emerald-600 text-white'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            Delivered ({orders.filter((o) => o.status === 'DELIVERED').length})
          </button>
        </div>

        <div className="relative w-full md:w-72">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search order ID, store, OTP..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-3 py-2 text-xs border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
          />
        </div>
      </div>

      {/* Orders Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50 text-slate-600 font-bold border-b border-slate-200">
                <th className="py-3 px-4">Order ID & Time</th>
                <th className="py-3 px-4">Fulfilling Kirana</th>
                <th className="py-3 px-4">Lifecycle State</th>
                <th className="py-3 px-4">Price Breakdown</th>
                <th className="py-3 px-4">Payment</th>
                <th className="py-3 px-4">Delivery OTP</th>
                <th className="py-3 px-4 text-right">Admin Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {filteredOrders.map((order) => (
                <tr key={order.id} className="hover:bg-slate-50/50">
                  <td className="py-3.5 px-4">
                    <div className="font-mono font-bold text-slate-900">#{order.id}</div>
                    <div className="text-[10px] text-slate-400">
                      {new Date(order.created_at).toLocaleTimeString([], {
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </div>
                  </td>

                  <td className="py-3.5 px-4">
                    <div className="font-semibold text-slate-800">{order.store_name}</div>
                    <div className="text-[11px] text-slate-500">{order.items_count} items</div>
                  </td>

                  <td className="py-3.5 px-4">
                    <span
                      className={`inline-block px-2.5 py-1 rounded-full text-[10px] font-extrabold border ${getStatusBadge(
                        order.status
                      )}`}
                    >
                      {order.status}
                    </span>
                  </td>

                  <td className="py-3.5 px-4">
                    <div className="font-bold text-slate-900">
                      ₹{order.total_amount.toFixed(2)}
                    </div>
                    <div className="text-[10px] text-slate-400">
                      ₹{order.subtotal} + ₹{order.delivery_fee} del + ₹{order.platform_fee} fee
                    </div>
                  </td>

                  <td className="py-3.5 px-4">
                    <div className="font-bold text-slate-700">{order.payment_mode}</div>
                    <div
                      className={`text-[10px] font-semibold ${
                        order.payment_status === 'PAID' ? 'text-emerald-600' : 'text-amber-600'
                      }`}
                    >
                      {order.payment_status}
                    </div>
                  </td>

                  <td className="py-3.5 px-4">
                    <div className="font-mono font-bold text-emerald-700 bg-emerald-50 px-2 py-1 rounded border border-emerald-200 inline-block">
                      {order.delivery_otp}
                    </div>
                  </td>

                  <td className="py-3.5 px-4 text-right">
                    {order.status !== 'DELIVERED' && order.status !== 'CANCELLED' ? (
                      <button
                        onClick={() => handleNextStatus(order)}
                        disabled={updatingId === order.id}
                        className="px-3 py-1.5 text-xs font-bold text-white bg-slate-800 hover:bg-slate-900 rounded-lg transition"
                      >
                        Advance State
                      </button>
                    ) : (
                      <span className="text-slate-400 text-xs italic">Finalized</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {filteredOrders.length === 0 && (
          <div className="p-12 text-center text-slate-400">No orders match the filter.</div>
        )}
      </div>
    </div>
  );
};
