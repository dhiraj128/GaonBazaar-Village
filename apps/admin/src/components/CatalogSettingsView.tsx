import React, { useState } from 'react';
import {
  Package,
  Plus,
  Settings,
  Tag,
  MapPin,
  IndianRupee,
  Save,
  CheckCircle,
  Percent,
  Sliders,
  Lock,
  Trash2,
  Edit,
  X,
  Sparkles,
} from 'lucide-react';
import type { CatalogItem, PlatformSettings, PromoCodeItem, AdminRole } from '../types';

interface CatalogSettingsViewProps {
  catalog: CatalogItem[];
  settings: PlatformSettings | null;
  promos: PromoCodeItem[];
  userRole?: AdminRole;
  onAddCatalogItem: (item: CatalogItem) => Promise<void>;
  onUpdateCatalogItem?: (id: string, item: Partial<CatalogItem>) => Promise<void>;
  onDeleteCatalogItem?: (id: string) => Promise<void>;
  onUpdateSettings: (settings: Partial<PlatformSettings>) => Promise<void>;
  onCreatePromo: (code: string, discountPct: number, minOrder: number, maxDiscount: number) => Promise<void>;
}

export const CatalogSettingsView: React.FC<CatalogSettingsViewProps> = ({
  catalog,
  settings,
  promos,
  userRole = 'super_admin',
  onAddCatalogItem,
  onUpdateCatalogItem,
  onDeleteCatalogItem,
  onUpdateSettings,
  onCreatePromo,
}) => {
  const isHubManager = userRole === 'hub_manager';
  const [activeTab, setActiveTab] = useState<'catalog' | 'pricing' | 'promos'>('catalog');

  // Add Item Modal
  const [showAddModal, setShowAddModal] = useState(false);
  const [newItemNameEn, setNewItemNameEn] = useState('');
  const [newItemNameHi, setNewItemNameHi] = useState('');
  const [newItemCategory, setNewItemCategory] = useState('Grocery');
  const [newItemUnit, setNewItemUnit] = useState('1 kg');
  const [newItemMrp, setNewItemMrp] = useState<number>(45);
  const [newItemImageUrl, setNewItemImageUrl] = useState(
    'https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=500&q=80'
  );

  // Pricing Engine Form State
  const [movInput, setMovInput] = useState<number>(settings?.min_order_value || 99);
  const [baseDeliveryInput, setBaseDeliveryInput] = useState<number>(settings?.base_delivery_fee || 15);
  const [perKmFeeInput, setPerKmFeeInput] = useState<number>(settings?.per_km_fee || 5);
  const [platformFeeInput, setPlatformFeeInput] = useState<number>(settings?.platform_fee || 3);
  const [commissionInput, setCommissionInput] = useState<number>(settings?.vendor_commission_pct || 0);
  const [maxRadiusInput, setMaxRadiusInput] = useState<number>(settings?.max_delivery_radius_km || 8);
  const [isSavingSettings, setIsSavingSettings] = useState(false);

  // Promo Code Form State
  const [promoCodeInput, setPromoCodeInput] = useState('');
  const [promoDiscountInput, setPromoDiscountInput] = useState<number>(20);
  const [promoMinOrderInput, setPromoMinOrderInput] = useState<number>(149);
  const [promoMaxDiscountInput, setPromoMaxDiscountInput] = useState<number>(50);
  const [isCreatingPromo, setIsCreatingPromo] = useState(false);

  const handleSaveSettings = async () => {
    if (isHubManager) {
      alert('Hub Managers are restricted from modifying pricing engine rules.');
      return;
    }
    setIsSavingSettings(true);
    try {
      await onUpdateSettings({
        min_order_value: movInput,
        base_delivery_fee: baseDeliveryInput,
        per_km_fee: perKmFeeInput,
        platform_fee: platformFeeInput,
        vendor_commission_pct: commissionInput,
        max_delivery_radius_km: maxRadiusInput,
      });
      alert('Platform pricing rules updated successfully!');
    } catch (e: any) {
      alert(`Settings update error: ${e.message}`);
    } finally {
      setIsSavingSettings(false);
    }
  };

  const handleCreatePromoSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!promoCodeInput.trim()) return;
    setIsCreatingPromo(true);
    try {
      await onCreatePromo(
        promoCodeInput.trim().toUpperCase(),
        promoDiscountInput,
        promoMinOrderInput,
        promoMaxDiscountInput
      );
      setPromoCodeInput('');
      alert('Promotional code created successfully!');
    } catch (e: any) {
      alert(`Promo creation error: ${e.message}`);
    } finally {
      setIsCreatingPromo(false);
    }
  };

  const handleAddItemSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await onAddCatalogItem({
        name_en: newItemNameEn,
        name_hi: newItemNameHi,
        category: newItemCategory,
        standard_unit: newItemUnit,
        suggested_price: newItemMrp,
        image_url: newItemImageUrl,
      });
      setShowAddModal(false);
      setNewItemNameEn('');
      setNewItemNameHi('');
    } catch (err: any) {
      alert(`Failed to add item: ${err.message}`);
    }
  };

  return (
    <div className="space-y-6">
      {/* Navigation Header */}
      <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <Package className="w-5 h-5 text-emerald-600" />
            <h2 className="text-sm font-extrabold text-slate-900">
              Master Global Catalog & Rural Pricing Engine
            </h2>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Centralized product catalog with standard MRPs, delivery fee calculation rules, and promo codes.
          </p>
        </div>

        {/* Tab Switcher */}
        <div className="flex items-center space-x-1 bg-slate-100 p-1 rounded-xl text-xs font-bold">
          <button
            onClick={() => setActiveTab('catalog')}
            className={`px-3 py-1.5 rounded-lg transition ${
              activeTab === 'catalog'
                ? 'bg-white text-slate-900 shadow-xs'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Global Catalog ({catalog.length})
          </button>
          <button
            onClick={() => setActiveTab('pricing')}
            className={`px-3 py-1.5 rounded-lg transition ${
              activeTab === 'pricing'
                ? 'bg-white text-slate-900 shadow-xs'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Pricing Engine Rules
          </button>
          <button
            onClick={() => setActiveTab('promos')}
            className={`px-3 py-1.5 rounded-lg transition ${
              activeTab === 'promos'
                ? 'bg-white text-slate-900 shadow-xs'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Promotional Codes ({promos.length})
          </button>
        </div>
      </div>

      {/* SECTION 1: Master Global Catalog */}
      {activeTab === 'catalog' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <p className="text-xs text-slate-500 font-medium">
              Standard products and MRPs configured centrally. Local village stores select from this master list when stocking inventory.
            </p>
            {!isHubManager && (
              <button
                onClick={() => setShowAddModal(true)}
                className="px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold shadow-xs flex items-center space-x-1.5 transition"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>Add Product to Master Catalog</span>
              </button>
            )}
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {catalog.map((item) => (
              <div
                key={item.id}
                className="bg-white rounded-2xl p-4 border border-slate-200 shadow-xs hover:border-emerald-500 hover:shadow-md transition flex flex-col justify-between"
              >
                <div>
                  <img
                    src={item.image_url}
                    alt={item.name_en}
                    className="w-full h-32 object-cover rounded-xl mb-3 bg-slate-50"
                  />
                  <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded">
                    {item.category}
                  </span>
                  <h4 className="font-bold text-slate-900 text-xs mt-1.5 leading-snug">
                    {item.name_en}
                  </h4>
                  <div className="text-[11px] text-slate-500">{item.name_hi}</div>
                </div>

                <div className="mt-3 pt-3 border-t border-slate-100 flex items-center justify-between">
                  <div>
                    <span className="text-xs font-black text-slate-900">
                      ₹{item.suggested_price || item.suggested_mrp}
                    </span>
                    <span className="text-[10px] text-slate-400 ml-1">
                      / {item.standard_unit || item.default_unit || '1 kg'}
                    </span>
                  </div>
                  {!isHubManager && onDeleteCatalogItem && item.id && (
                    <button
                      onClick={() => {
                        if (window.confirm(`Delete '${item.name_en}' from Global Catalog?`)) {
                          onDeleteCatalogItem(item.id!);
                        }
                      }}
                      className="text-slate-400 hover:text-rose-600 p-1"
                      title="Delete Product"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* SECTION 2: Pricing Engine Rules */}
      {activeTab === 'pricing' && (
        <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-xs space-y-6">
          <div className="border-b border-slate-100 pb-3 flex items-center justify-between">
            <div>
              <h3 className="text-sm font-extrabold text-slate-900">
                Automated Rural Pricing Engine Configuration
              </h3>
              <p className="text-xs text-slate-500">
                Configure Minimum Order Value (MOV), tiered delivery fee calculations, and platform fee policies.
              </p>
            </div>
            {isHubManager && (
              <span className="px-2.5 py-1 bg-amber-50 text-amber-800 text-xs font-bold rounded-lg border border-amber-200 flex items-center gap-1">
                <Lock className="w-3.5 h-3.5" /> Read-Only Mode (Hub Manager)
              </span>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-xs">
            {/* MOV */}
            <div className="space-y-1.5">
              <label className="font-bold text-slate-700 block">
                Minimum Order Value (MOV) in INR:
              </label>
              <p className="text-[11px] text-slate-500">
                Orders below this threshold cannot be placed. Ensures economic viability for rural delivery partners.
              </p>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-slate-500">₹</span>
                <input
                  type="number"
                  value={movInput}
                  disabled={isHubManager}
                  onChange={(e) => setMovInput(parseFloat(e.target.value) || 0)}
                  className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-xl font-bold outline-none disabled:bg-slate-100"
                />
              </div>
            </div>

            {/* Base Delivery Fee */}
            <div className="space-y-1.5">
              <label className="font-bold text-slate-700 block">
                Base Delivery Fee (First 2 km):
              </label>
              <p className="text-[11px] text-slate-500">
                Flat base charge guaranteed to runner partner for delivery within initial 2km village boundary.
              </p>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-slate-500">₹</span>
                <input
                  type="number"
                  value={baseDeliveryInput}
                  disabled={isHubManager}
                  onChange={(e) => setBaseDeliveryInput(parseFloat(e.target.value) || 0)}
                  className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-xl font-bold outline-none disabled:bg-slate-100"
                />
              </div>
            </div>

            {/* Per KM Charge */}
            <div className="space-y-1.5">
              <label className="font-bold text-slate-700 block">
                Per KM Distance Surcharge (Beyond 2 km):
              </label>
              <p className="text-[11px] text-slate-500">
                Added incrementally per kilometer based on GPS distance from village store to customer hut.
              </p>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-slate-500">₹</span>
                <input
                  type="number"
                  value={perKmFeeInput}
                  disabled={isHubManager}
                  onChange={(e) => setPerKmFeeInput(parseFloat(e.target.value) || 0)}
                  className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-xl font-bold outline-none disabled:bg-slate-100"
                />
              </div>
            </div>

            {/* Platform Fee */}
            <div className="space-y-1.5">
              <label className="font-bold text-slate-700 block">
                Platform Convenience Fee per Order:
              </label>
              <p className="text-[11px] text-slate-500">
                Fixed rural maintenance fee added to every order (Standard: ₹3 - ₹5).
              </p>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-slate-500">₹</span>
                <input
                  type="number"
                  value={platformFeeInput}
                  disabled={isHubManager}
                  onChange={(e) => setPlatformFeeInput(parseFloat(e.target.value) || 0)}
                  className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-xl font-bold outline-none disabled:bg-slate-100"
                />
              </div>
            </div>

            {/* Vendor Commission % */}
            <div className="space-y-1.5">
              <label className="font-bold text-slate-700 block">
                Vendor Commission Percentage (%):
              </label>
              <p className="text-[11px] text-slate-500">
                GaonBazaar 0% introductory rural guarantee policy.
              </p>
              <div className="flex items-center space-x-2">
                <input
                  type="number"
                  value={commissionInput}
                  disabled={isHubManager}
                  onChange={(e) => setCommissionInput(parseFloat(e.target.value) || 0)}
                  className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-xl font-bold outline-none disabled:bg-slate-100"
                />
                <span className="font-bold text-slate-500">%</span>
              </div>
            </div>

            {/* Max Delivery Radius */}
            <div className="space-y-1.5">
              <label className="font-bold text-slate-700 block">
                Maximum Operational Geofence Radius:
              </label>
              <p className="text-[11px] text-slate-500">
                Strict 8km cutoff boundary. Orders beyond this distance are rejected by geofencing engine.
              </p>
              <div className="flex items-center space-x-2">
                <input
                  type="number"
                  value={maxRadiusInput}
                  disabled={isHubManager}
                  onChange={(e) => setMaxRadiusInput(parseFloat(e.target.value) || 0)}
                  className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-xl font-bold outline-none disabled:bg-slate-100"
                />
                <span className="font-bold text-slate-500">km</span>
              </div>
            </div>
          </div>

          {!isHubManager && (
            <div className="pt-4 border-t border-slate-100 flex justify-end">
              <button
                onClick={handleSaveSettings}
                disabled={isSavingSettings}
                className="px-6 py-2.5 bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs rounded-xl shadow-md transition flex items-center space-x-2"
              >
                <Save className="w-4 h-4 text-emerald-400" />
                <span>Save Pricing Engine Rules</span>
              </button>
            </div>
          )}
        </div>
      )}

      {/* SECTION 3: Promotional Codes */}
      {activeTab === 'promos' && (
        <div className="space-y-6">
          {!isHubManager && (
            <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs">
              <h3 className="text-sm font-extrabold text-slate-900 mb-1">
                Create Promotional Discount Promo Code
              </h3>
              <p className="text-xs text-slate-500 mb-4">
                Launch targeted rural marketing campaigns to incentivize first-time village orders.
              </p>

              <form onSubmit={handleCreatePromoSubmit} className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 text-xs">
                <div>
                  <label className="font-bold text-slate-700 block mb-1">Promo Code:</label>
                  <input
                    type="text"
                    value={promoCodeInput}
                    onChange={(e) => setPromoCodeInput(e.target.value.toUpperCase())}
                    placeholder="e.g. GAON30"
                    className="w-full p-2 bg-slate-50 border border-slate-200 rounded-lg font-mono font-bold uppercase outline-none"
                    required
                  />
                </div>
                <div>
                  <label className="font-bold text-slate-700 block mb-1">Discount %:</label>
                  <input
                    type="number"
                    value={promoDiscountInput}
                    onChange={(e) => setPromoDiscountInput(parseFloat(e.target.value) || 0)}
                    className="w-full p-2 bg-slate-50 border border-slate-200 rounded-lg font-bold outline-none"
                    required
                  />
                </div>
                <div>
                  <label className="font-bold text-slate-700 block mb-1">Min Order (₹):</label>
                  <input
                    type="number"
                    value={promoMinOrderInput}
                    onChange={(e) => setPromoMinOrderInput(parseFloat(e.target.value) || 0)}
                    className="w-full p-2 bg-slate-50 border border-slate-200 rounded-lg font-bold outline-none"
                    required
                  />
                </div>
                <div className="flex items-end">
                  <button
                    type="submit"
                    disabled={isCreatingPromo}
                    className="w-full py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs rounded-lg shadow-xs transition"
                  >
                    Activate Promo
                  </button>
                </div>
              </form>
            </div>
          )}

          <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 uppercase text-[10px] font-bold tracking-wider border-b border-slate-200">
                <tr>
                  <th className="px-6 py-3">Code</th>
                  <th className="px-6 py-3">Discount</th>
                  <th className="px-6 py-3">Min Order Value</th>
                  <th className="px-6 py-3">Max Discount Cap</th>
                  <th className="px-6 py-3">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
                {promos.map((p) => (
                  <tr key={p.id} className="hover:bg-slate-50/80 transition">
                    <td className="px-6 py-3.5 font-mono font-bold text-emerald-800">{p.code}</td>
                    <td className="px-6 py-3.5 font-bold text-slate-900">{p.discount_pct}% OFF</td>
                    <td className="px-6 py-3.5">₹{p.min_order_value}</td>
                    <td className="px-6 py-3.5">₹{p.max_discount}</td>
                    <td className="px-6 py-3.5">
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800">
                        Active
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Add Product Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-slate-950/75 z-50 flex items-center justify-center p-4 backdrop-blur-xs">
          <div className="bg-white rounded-3xl max-w-md w-full p-6 space-y-4 shadow-2xl border border-slate-200">
            <div className="flex items-center justify-between pb-2 border-b border-slate-100">
              <h3 className="text-sm font-black text-slate-900 uppercase">
                Add Global Catalog Product
              </h3>
              <button onClick={() => setShowAddModal(false)} className="text-slate-400">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleAddItemSubmit} className="space-y-3 text-xs">
              <div>
                <label className="font-bold text-slate-700 block mb-1">Product Name (English):</label>
                <input
                  type="text"
                  value={newItemNameEn}
                  onChange={(e) => setNewItemNameEn(e.target.value)}
                  placeholder="e.g. Sona Masoori Rice"
                  className="w-full p-2 bg-slate-50 border border-slate-200 rounded-xl outline-none"
                  required
                />
              </div>

              <div>
                <label className="font-bold text-slate-700 block mb-1">Product Name (Hindi):</label>
                <input
                  type="text"
                  value={newItemNameHi}
                  onChange={(e) => setNewItemNameHi(e.target.value)}
                  placeholder="उदा. सोना मसूरी चावल"
                  className="w-full p-2 bg-slate-50 border border-slate-200 rounded-xl outline-none"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="font-bold text-slate-700 block mb-1">Category:</label>
                  <select
                    value={newItemCategory}
                    onChange={(e) => setNewItemCategory(e.target.value)}
                    className="w-full p-2 bg-slate-50 border border-slate-200 rounded-xl outline-none"
                  >
                    <option value="Grocery">Grocery & Ration</option>
                    <option value="Vegetables">Fresh Vegetables</option>
                    <option value="Dairy">Dairy & Milk</option>
                    <option value="Pooja">Pooja Samagri</option>
                    <option value="Hardware">Electrical & Hardware</option>
                  </select>
                </div>
                <div>
                  <label className="font-bold text-slate-700 block mb-1">Standard MRP (₹):</label>
                  <input
                    type="number"
                    value={newItemMrp}
                    onChange={(e) => setNewItemMrp(parseFloat(e.target.value) || 0)}
                    className="w-full p-2 bg-slate-50 border border-slate-200 rounded-xl outline-none font-bold"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="font-bold text-slate-700 block mb-1">Image URL (Unsplash):</label>
                <input
                  type="url"
                  value={newItemImageUrl}
                  onChange={(e) => setNewItemImageUrl(e.target.value)}
                  className="w-full p-2 bg-slate-50 border border-slate-200 rounded-xl outline-none text-[11px]"
                  required
                />
              </div>

              <div className="flex items-center justify-end space-x-2 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 text-xs text-slate-600 font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs rounded-xl shadow-xs"
                >
                  Save to Master Catalog
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
