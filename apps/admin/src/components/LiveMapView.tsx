import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import {
  MapPin,
  Bike,
  Navigation,
  Radio,
  Send,
  Battery,
  Gauge,
  Phone,
  AlertTriangle,
  RefreshCw,
  Eye,
  CheckCircle,
} from 'lucide-react';
import type { RiderMapPin, DemandHeatmapZone } from '../types';

interface LiveMapViewProps {
  riders: RiderMapPin[];
  heatmaps: DemandHeatmapZone[];
  onPingRider?: (runnerId: string, lat: number, lng: number) => Promise<void>;
  onNotifyRedZone: (zoneName: string, lat: number, lng: number, message?: string) => Promise<void>;
  onRefresh: () => void;
}

export const LiveMapView: React.FC<LiveMapViewProps> = ({
  riders,
  heatmaps,
  onPingRider,
  onNotifyRedZone,
  onRefresh,
}) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const markersRef = useRef<{ [id: string]: L.Marker }>({});
  const heatCirclesRef = useRef<L.Circle[]>([]);

  const [selectedRider, setSelectedRider] = useState<RiderMapPin | null>(null);
  const [filterState, setFilterState] = useState<'ALL' | 'IDLE' | 'BUSY' | 'OFFLINE'>('ALL');
  const [isNotifying, setIsNotifying] = useState(false);
  const [isSimulatingPing, setIsSimulatingPing] = useState(false);

  // Initialize Leaflet Map
  useEffect(() => {
    if (!mapContainerRef.current) return;
    if (mapInstanceRef.current) return;

    // Center on Muzaffarpur Operations Hub, Muzaffarpur, Bihar
    const map = L.map(mapContainerRef.current, {
      center: [26.2050, 85.3500],
      zoom: 13,
      zoomControl: true,
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '© OpenStreetMap contributors | GaonBazaar Operations',
    }).addTo(map);

    // 8km Operational Geofence Boundary Circle
    L.circle([26.2050, 85.3500], {
      color: '#059669',
      fillColor: '#10b981',
      fillOpacity: 0.05,
      radius: 8000,
      weight: 1.5,
      dashArray: '6, 6',
    })
      .addTo(map)
      .bindTooltip('8km Rural Delivery Geofence — Muzaffarpur Hub', {
        permanent: false,
        direction: 'center',
      });

    mapInstanceRef.current = map;

    return () => {
      map.remove();
      mapInstanceRef.current = null;
    };
  }, []);

  // Update Rider Markers on Map
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map) return;

    // Remove old markers not in current list
    const currentRiderIds = new Set(riders.map((r) => r.runner_id));
    Object.keys(markersRef.current).forEach((id) => {
      if (!currentRiderIds.has(id)) {
        markersRef.current[id].remove();
        delete markersRef.current[id];
      }
    });

    riders.forEach((rider) => {
      // Determine marker color
      const markerColor =
        rider.color === 'green'
          ? '#10b981'
          : rider.color === 'orange'
          ? '#f59e0b'
          : '#ef4444';

      const customIcon = L.divIcon({
        className: 'custom-rider-pin',
        html: `
          <div style="
            position: relative;
            width: 32px;
            height: 32px;
            border-radius: 50%;
            background-color: ${markerColor};
            border: 3px solid #ffffff;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
            display: flex;
            align-items: center;
            justify-content: center;
            color: #ffffff;
            font-size: 14px;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s ease;
          ">
            🚴
            <span style="
              position: absolute;
              bottom: -2px;
              right: -2px;
              width: 10px;
              height: 10px;
              border-radius: 50%;
              background-color: ${markerColor};
              border: 1.5px solid white;
            "></span>
          </div>
        `,
        iconSize: [32, 32],
        iconAnchor: [16, 16],
        popupAnchor: [0, -18],
      });

      if (markersRef.current[rider.runner_id]) {
        // Move existing marker smoothly
        markersRef.current[rider.runner_id].setLatLng([rider.latitude, rider.longitude]);
        markersRef.current[rider.runner_id].setIcon(customIcon);
      } else {
        // Create new marker
        const marker = L.marker([rider.latitude, rider.longitude], { icon: customIcon }).addTo(map);
        marker.on('click', () => {
          setSelectedRider(rider);
        });
        markersRef.current[rider.runner_id] = marker;
      }
    });
  }, [riders]);

  // Update Demand Heatmaps Overlays (Red Zones)
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map) return;

    // Clear previous circles
    heatCirclesRef.current.forEach((c) => c.remove());
    heatCirclesRef.current = [];

    heatmaps.forEach((zone) => {
      const circle = L.circle([zone.latitude, zone.longitude], {
        color: zone.is_red_zone ? '#dc2626' : '#f97316',
        fillColor: zone.is_red_zone ? '#ef4444' : '#fb923c',
        fillOpacity: zone.is_red_zone ? 0.35 : 0.18,
        radius: zone.radius_meters || 1000,
        weight: zone.is_red_zone ? 2.5 : 1.5,
      }).addTo(map);

      circle.bindTooltip(
        `<b>${zone.zone_name}</b><br/>Demand: ${zone.active_orders} orders | Idle Riders: ${zone.available_riders}`,
        { permanent: zone.is_red_zone, direction: 'top' }
      );

      heatCirclesRef.current.push(circle);
    });
  }, [heatmaps]);

  const filteredRiders = riders.filter((r) => {
    if (filterState === 'IDLE') return r.state === 'IDLE';
    if (filterState === 'BUSY') return r.state === 'BUSY';
    if (filterState === 'OFFLINE') return r.state === 'OFFLINE' || r.state === 'ISSUE';
    return true;
  });

  const handleSimulatePing = async () => {
    if (!riders.length) return;
    setIsSimulatingPing(true);
    try {
      const target = riders[0];
      const newLat = target.latitude + (Math.random() - 0.5) * 0.005;
      const newLng = target.longitude + (Math.random() - 0.5) * 0.005;
      if (onPingRider) {
        await onPingRider(target.runner_id, newLat, newLng);
      }
      onRefresh();
    } catch {
      // Ignored
    } finally {
      setIsSimulatingPing(false);
    }
  };

  const handleNotifyRedZoneClick = async (zone: DemandHeatmapZone) => {
    setIsNotifying(true);
    try {
      await onNotifyRedZone(zone.zone_name, zone.latitude, zone.longitude);
      alert(`Priority alert broadcasted to idle riders: Move to ${zone.zone_name}! (+₹20 surge bonus enabled)`);
    } catch (e: any) {
      alert(`Notify failed: ${e.message}`);
    } finally {
      setIsNotifying(false);
    }
  };

  return (
    <div className="space-y-4">
      {/* Top Map Control Bar */}
      <div className="bg-white rounded-2xl p-4 border border-slate-200 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <Radio className="w-5 h-5 text-emerald-600 animate-pulse" />
            <h2 className="text-sm font-extrabold text-slate-900">
              Live Fleet Operations Center (10s Real-Time GPS Tracking)
            </h2>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Full-screen district operations map. Green = Idle (Available), Orange = Busy (On Run), Red = Offline/SOS.
          </p>
        </div>

        {/* Legend & Filters */}
        <div className="flex items-center space-x-2 text-xs font-bold">
          <button
            onClick={() => setFilterState('ALL')}
            className={`px-3 py-1.5 rounded-lg transition ${
              filterState === 'ALL'
                ? 'bg-slate-900 text-white shadow-xs'
                : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
            }`}
          >
            All Riders ({riders.length})
          </button>
          <button
            onClick={() => setFilterState('IDLE')}
            className={`px-3 py-1.5 rounded-lg transition flex items-center space-x-1.5 ${
              filterState === 'IDLE'
                ? 'bg-emerald-600 text-white shadow-xs'
                : 'bg-emerald-50 text-emerald-800 hover:bg-emerald-100'
            }`}
          >
            <span className="w-2 h-2 rounded-full bg-emerald-500" />
            <span>Idle ({riders.filter((r) => r.state === 'IDLE').length})</span>
          </button>
          <button
            onClick={() => setFilterState('BUSY')}
            className={`px-3 py-1.5 rounded-lg transition flex items-center space-x-1.5 ${
              filterState === 'BUSY'
                ? 'bg-amber-600 text-white shadow-xs'
                : 'bg-amber-50 text-amber-800 hover:bg-amber-100'
            }`}
          >
            <span className="w-2 h-2 rounded-full bg-amber-500" />
            <span>Busy ({riders.filter((r) => r.state === 'BUSY').length})</span>
          </button>
          <button
            onClick={() => setFilterState('OFFLINE')}
            className={`px-3 py-1.5 rounded-lg transition flex items-center space-x-1.5 ${
              filterState === 'OFFLINE'
                ? 'bg-rose-600 text-white shadow-xs'
                : 'bg-rose-50 text-rose-800 hover:bg-rose-100'
            }`}
          >
            <span className="w-2 h-2 rounded-full bg-rose-500" />
            <span>Issue/Offline ({riders.filter((r) => r.state === 'OFFLINE' || r.state === 'ISSUE').length})</span>
          </button>

          <button
            onClick={handleSimulatePing}
            disabled={isSimulatingPing}
            className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-800 rounded-lg text-xs font-bold border border-slate-200 flex items-center gap-1 ml-2 transition"
            title="Simulate 10s GPS Ping for testing"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isSimulatingPing ? 'animate-spin' : ''}`} />
            <span>Test Ping</span>
          </button>
        </div>
      </div>

      {/* Main Map Container & Floating Panels */}
      <div className="relative rounded-3xl overflow-hidden border border-slate-200 shadow-md h-[580px] bg-slate-100">
        <div ref={mapContainerRef} className="w-full h-full z-0" />

        {/* Floating Demand Heatmaps Card ("Red Zones") */}
        <div className="absolute top-4 right-4 z-10 bg-white/95 backdrop-blur-md rounded-2xl p-4 border border-slate-200 shadow-xl max-w-sm w-full">
          <div className="flex items-center justify-between pb-2 mb-2 border-b border-slate-100">
            <span className="text-xs font-black text-rose-950 uppercase tracking-wide flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-rose-600 animate-ping" />
              Demand Red Zones ({heatmaps.filter((h) => h.is_red_zone).length})
            </span>
            <span className="text-[10px] text-slate-400 font-bold">Surge Pricing Ready</span>
          </div>

          <div className="space-y-2.5">
            {heatmaps.map((zone) => (
              <div
                key={zone.zone_id}
                className={`p-2.5 rounded-xl border text-xs ${
                  zone.is_red_zone
                    ? 'bg-rose-50/80 border-rose-200'
                    : 'bg-slate-50 border-slate-200'
                }`}
              >
                <div className="flex items-center justify-between font-bold">
                  <span className={zone.is_red_zone ? 'text-rose-900' : 'text-slate-800'}>
                    {zone.zone_name}
                  </span>
                  <span
                    className={`px-1.5 py-0.5 rounded text-[10px] font-black ${
                      zone.is_red_zone
                        ? 'bg-rose-600 text-white animate-pulse'
                        : 'bg-slate-200 text-slate-700'
                    }`}
                  >
                    {zone.is_red_zone ? 'RED ZONE' : 'NORMAL'}
                  </span>
                </div>
                <p className="text-[11px] text-slate-600 mt-0.5">{zone.description}</p>

                {zone.is_red_zone && (
                  <button
                    onClick={() => handleNotifyRedZoneClick(zone)}
                    disabled={isNotifying}
                    className="mt-2 w-full py-1.5 bg-rose-600 hover:bg-rose-700 text-white rounded-lg font-bold text-[11px] shadow-xs flex items-center justify-center gap-1.5 transition"
                  >
                    <Send className="w-3 h-3" />
                    <span>Notify Riders to Move to Red Zone (+₹20)</span>
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Selected Rider Detail Card (If rider clicked) */}
        {selectedRider && (
          <div className="absolute bottom-4 left-4 z-10 bg-white/95 backdrop-blur-md rounded-2xl p-4 border border-slate-200 shadow-2xl max-w-sm w-full animate-in fade-in slide-in-from-bottom-2 duration-150">
            <div className="flex items-center justify-between pb-2 mb-2 border-b border-slate-100">
              <div className="flex items-center space-x-2">
                <Bike className="w-4 h-4 text-emerald-600" />
                <span className="font-extrabold text-xs text-slate-900">
                  {selectedRider.name}
                </span>
              </div>
              <button
                onClick={() => setSelectedRider(null)}
                className="text-slate-400 hover:text-slate-800 text-xs font-bold"
              >
                ✕
              </button>
            </div>

            <div className="space-y-1.5 text-xs">
              <div className="flex items-center justify-between text-slate-600">
                <span>Vehicle:</span>
                <span className="font-bold text-slate-900">
                  {selectedRider.vehicle_type} ({selectedRider.vehicle_number})
                </span>
              </div>
              <div className="flex items-center justify-between text-slate-600">
                <span>Current Status:</span>
                <span
                  className={`font-black text-[10px] px-2 py-0.5 rounded-full ${
                    selectedRider.color === 'green'
                      ? 'bg-emerald-100 text-emerald-800'
                      : selectedRider.color === 'orange'
                      ? 'bg-amber-100 text-amber-800'
                      : 'bg-rose-100 text-rose-800'
                  }`}
                >
                  {selectedRider.state}
                </span>
              </div>
              {selectedRider.assigned_order_id && (
                <div className="flex items-center justify-between text-slate-600">
                  <span>Assigned Order:</span>
                  <span className="font-mono font-bold text-indigo-700">
                    #{selectedRider.assigned_order_id.slice(0, 8)}
                  </span>
                </div>
              )}
              <div className="flex items-center justify-between text-slate-600">
                <span>Speed / Telemetry:</span>
                <span className="font-bold text-slate-800">
                  {selectedRider.speed_kmh} km/h • Battery {selectedRider.battery_level}%
                </span>
              </div>
              <div className="pt-2 flex items-center justify-between">
                <a
                  href={`tel:${selectedRider.phone}`}
                  className="px-3 py-1 bg-slate-900 hover:bg-slate-800 text-white rounded-lg font-bold text-xs flex items-center gap-1"
                >
                  <Phone className="w-3 h-3" /> Call Rider
                </a>
                <span className="text-[10px] text-slate-400">
                  Lat: {selectedRider.latitude.toFixed(4)}, Lng: {selectedRider.longitude.toFixed(4)}
                </span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Fleet Quick Summary Bar */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {filteredRiders.map((r) => (
          <div
            key={r.runner_id}
            onClick={() => setSelectedRider(r)}
            className="bg-white p-3 rounded-xl border border-slate-200 shadow-xs hover:border-emerald-500 transition cursor-pointer flex items-center justify-between"
          >
            <div>
              <div className="font-bold text-xs text-slate-900 truncate">{r.name}</div>
              <div className="text-[10px] text-slate-400">{r.vehicle_type}</div>
            </div>
            <span
              className={`w-2.5 h-2.5 rounded-full ${
                r.color === 'green'
                  ? 'bg-emerald-500'
                  : r.color === 'orange'
                  ? 'bg-amber-500 animate-pulse'
                  : 'bg-rose-500'
              }`}
            />
          </div>
        ))}
      </div>
    </div>
  );
};
