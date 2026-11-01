import {
  MapPin,
  Clock,
  Compass,
  Layers,
  IndianRupee,
} from 'lucide-react';
import type { PlatformSettings } from '../types';

interface ZonesViewProps {
  settings: PlatformSettings | null;
}

export const ZonesView: React.FC<ZonesViewProps> = ({ settings }) => {
  if (!settings) {
    return <div className="p-8 text-center text-slate-500">Loading zones configuration...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Pilot Zone Details Card */}
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
        <div className="flex items-start justify-between">
          <div>
            <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800 mb-2">
              <Compass className="w-3.5 h-3.5" />
              Pilot Launch Geo-Fence
            </div>
            <h3 className="text-xl font-black text-slate-900">
              {settings.pilot_block}, {settings.pilot_district} ({settings.pilot_state})
            </h3>
            <p className="text-xs text-slate-500 mt-1">
              Active operating boundary for village quick delivery. Orders beyond{' '}
              <b className="text-slate-800">8.0 km</b> from fulfilling kirana GPS are blocked.
            </p>
          </div>

          <div className="text-right">
            <span className="text-xs font-semibold text-slate-400 block uppercase">Max Radius</span>
            <span className="text-2xl font-black text-emerald-600">
              {settings.max_delivery_radius_km} km
            </span>
          </div>
        </div>

        {/* Pilot Localities Table */}
        <div className="mt-6">
          <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-3">
            Verified Pilot Localities & GPS Coordinates
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {settings.pilot_localities.map((loc, idx) => (
              <div
                key={idx}
                className="bg-slate-50 p-4 rounded-xl border border-slate-200 hover:border-emerald-300 transition"
              >
                <div className="flex items-center space-x-2 text-emerald-700 font-bold text-xs">
                  <MapPin className="w-4 h-4 text-emerald-600" />
                  <span>{loc.name}</span>
                </div>
                <div className="mt-2 text-[11px] font-mono text-slate-600">
                  Lat: <span className="font-semibold">{loc.lat.toFixed(4)}</span>
                  <br />
                  Lng: <span className="font-semibold">{loc.lng.toFixed(4)}</span>
                </div>
                <div className="mt-2 text-[10px] text-slate-400">
                  Minapur Block • 30–60 Min SLA
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Pricing Matrix & Policy Rules */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center space-x-2 text-slate-800 font-bold text-sm mb-3">
            <IndianRupee className="w-4 h-4 text-emerald-600" />
            <span>Platform Convenience Fee</span>
          </div>
          <div className="text-3xl font-black text-emerald-600">
            ₹{settings.platform_fee.toFixed(2)}
          </div>
          <p className="text-xs text-slate-500 mt-2">
            Applied per completed order to maintain rural server infrastructure, AI voice processing,
            and 24/7 support.
          </p>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center space-x-2 text-slate-800 font-bold text-sm mb-3">
            <Layers className="w-4 h-4 text-emerald-600" />
            <span>Vendor Commission</span>
          </div>
          <div className="text-3xl font-black text-emerald-600">
            {settings.vendor_commission_pct}%
          </div>
          <p className="text-xs text-slate-500 mt-2">
            0% Introductory Commission for village shopkeepers to foster local rural adoption and
            kirana digitization.
          </p>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center space-x-2 text-slate-800 font-bold text-sm mb-3">
            <Clock className="w-4 h-4 text-emerald-600" />
            <span>Cancellation Grace Period</span>
          </div>
          <div className="text-3xl font-black text-emerald-600">
            {settings.cancel_window_seconds}s
          </div>
          <p className="text-xs text-slate-500 mt-2">
            Customers may cancel free of penalty within 180 seconds of placement before kirana
            initiates packaging.
          </p>
        </div>
      </div>

      {/* Delivery Fee Tier Structure */}
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
        <h4 className="text-sm font-bold text-slate-800 mb-2">
          Tiered Hyperlocal Delivery Fee Engine (Configured)
        </h4>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50 text-slate-600 border-b border-slate-200">
                <th className="py-2.5 px-4 font-bold">Distance Tier</th>
                <th className="py-2.5 px-4 font-bold">Customer Delivery Charge</th>
                <th className="py-2.5 px-4 font-bold">Runner Payout Share</th>
                <th className="py-2.5 px-4 font-bold">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              <tr>
                <td className="py-3 px-4 font-medium">0.0 km – 3.0 km (Local Village)</td>
                <td className="py-3 px-4 font-bold">₹15.00</td>
                <td className="py-3 px-4 text-emerald-700 font-bold">100% (₹15.00)</td>
                <td className="py-3 px-4 text-emerald-600 font-bold">Active</td>
              </tr>
              <tr>
                <td className="py-3 px-4 font-medium">3.1 km – 5.0 km (Neighboring Hamlet)</td>
                <td className="py-3 px-4 font-bold">₹25.00</td>
                <td className="py-3 px-4 text-emerald-700 font-bold">100% (₹25.00)</td>
                <td className="py-3 px-4 text-emerald-600 font-bold">Active</td>
              </tr>
              <tr>
                <td className="py-3 px-4 font-medium">5.1 km – 8.0 km (Maximum Radius Limit)</td>
                <td className="py-3 px-4 font-bold">₹35.00</td>
                <td className="py-3 px-4 text-emerald-700 font-bold">100% (₹35.00)</td>
                <td className="py-3 px-4 text-emerald-600 font-bold">Active</td>
              </tr>
              <tr className="bg-rose-50/50">
                <td className="py-3 px-4 font-bold text-rose-800">&gt; 8.0 km (Out of Pilot Area)</td>
                <td className="py-3 px-4 text-rose-700 font-bold">BLOCKED</td>
                <td className="py-3 px-4 text-rose-700 font-medium">N/A</td>
                <td className="py-3 px-4 text-rose-700 font-bold">Outside Service Radius</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
