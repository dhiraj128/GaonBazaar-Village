import React, { useState, useEffect } from 'react';
import { Users, Phone, MapPin, ShoppingBag, ShieldCheck, Search } from 'lucide-react';
import { adminApi } from '../api';
import type { CustomerItem } from '../types';

interface CustomersViewProps {
  customers?: CustomerItem[];
}

export const CustomersView: React.FC<CustomersViewProps> = ({ customers: initialCustomers }) => {
  const [customers, setCustomers] = useState<CustomerItem[]>(initialCustomers || []);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(!initialCustomers);

  useEffect(() => {
    if (initialCustomers) {
      setCustomers(initialCustomers);
      setLoading(false);
    } else {
      loadCustomers();
    }
  }, [initialCustomers]);

  const loadCustomers = async () => {
    setLoading(true);
    const data = await adminApi.getCustomers();
    setCustomers(data);
    setLoading(false);
  };

  const filtered = customers.filter(
    (c) =>
      c.name.toLowerCase().includes(search.toLowerCase()) ||
      c.phone.includes(search)
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">Customer Directory</h2>
          <p className="text-slate-600 text-sm">
            Registered village customers across service areas
          </p>
        </div>
        <div className="relative w-full sm:w-64">
          <Search className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
          <input
            type="text"
            placeholder="Search by name or phone..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
          />
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12 text-slate-500">Loading customers...</div>
      ) : filtered.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-xl border border-slate-200">
          <Users className="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <p className="text-slate-600 font-medium">No customers found</p>
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-50 border-b border-slate-200 text-slate-600 font-semibold">
                <tr>
                  <th className="px-6 py-4">Customer</th>
                  <th className="px-6 py-4">Contact Phone</th>
                  <th className="px-6 py-4">UI Language</th>
                  <th className="px-6 py-4">Addresses</th>
                  <th className="px-6 py-4">Orders Placed</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4">Joined Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filtered.map((c) => (
                  <tr key={c.id} className="hover:bg-slate-50/50 transition">
                    <td className="px-6 py-4 font-medium text-slate-900 flex items-center gap-2">
                      <div className="w-8 h-8 rounded-full bg-emerald-100 text-emerald-800 flex items-center justify-center font-bold text-xs">
                        {c.name.slice(0, 2).toUpperCase()}
                      </div>
                      {c.name}
                    </td>
                    <td className="px-6 py-4 text-slate-600">
                      <span className="flex items-center gap-1.5 font-mono">
                        <Phone className="w-3.5 h-3.5 text-slate-400" />
                        +91 {c.phone}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-100 text-slate-700">
                        {c.preferred_language === 'hi' ? 'हिंदी (Hindi)' : 'English'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-slate-600">
                      <span className="flex items-center gap-1">
                        <MapPin className="w-3.5 h-3.5 text-slate-400" />
                        {c.addresses_count} saved
                      </span>
                    </td>
                    <td className="px-6 py-4 font-semibold text-slate-900">
                      <span className="flex items-center gap-1">
                        <ShoppingBag className="w-3.5 h-3.5 text-emerald-600" />
                        {c.orders_count}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 flex items-center gap-1 w-fit">
                        <ShieldCheck className="w-3 h-3" />
                        Active
                      </span>
                    </td>
                    <td className="px-6 py-4 text-slate-500 text-xs">
                      {new Date(c.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
