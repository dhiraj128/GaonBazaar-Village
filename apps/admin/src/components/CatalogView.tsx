import { useState } from 'react';
import {
  Plus,
  Search,
  X,
} from 'lucide-react';
import type { CatalogItem } from '../types';

interface CatalogViewProps {
  catalog: CatalogItem[];
  onAddItem: (item: CatalogItem) => Promise<void>;
}

export const CatalogView: React.FC<CatalogViewProps> = ({ catalog, onAddItem }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Form state
  const [formData, setFormData] = useState<CatalogItem>({
    name_en: '',
    name_hi: '',
    category: 'Grocery & Ration',
    standard_unit: '1 kg',
    suggested_price: 50.0,
    image_url: 'https://images.unsplash.com/photo-1586201375761-83865001e31c?w=500&q=80',
  });

  const categories = [
    'All',
    'Grocery & Ration',
    'Vegetables & Fruits',
    'Fresh Dairy',
    'Pooja & Rituals',
    'Electrical & Hardware',
    'General Store',
  ];

  const filteredItems = catalog.filter((item) => {
    if (selectedCategory !== 'All' && item.category !== selectedCategory) return false;
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      return (
        item.name_en.toLowerCase().includes(term) ||
        item.name_hi.toLowerCase().includes(term) ||
        item.category.toLowerCase().includes(term)
      );
    }
    return true;
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name_en || !formData.name_hi) return;
    setIsSubmitting(true);
    try {
      await onAddItem(formData);
      setIsModalOpen(false);
      setFormData({
        name_en: '',
        name_hi: '',
        category: 'Grocery & Ration',
        standard_unit: '1 kg',
        suggested_price: 50.0,
        image_url: 'https://images.unsplash.com/photo-1586201375761-83865001e31c?w=500&q=80',
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Search, Filter & Add Item Header */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center space-x-2 overflow-x-auto pb-1 md:pb-0">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold whitespace-nowrap transition ${
                selectedCategory === cat
                  ? 'bg-slate-900 text-white'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>

        <div className="flex items-center space-x-3">
          <div className="relative w-full md:w-64">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search product (EN/HI)..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-3 py-2 text-xs border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
            />
          </div>

          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center space-x-1.5 px-3.5 py-2 text-xs font-bold bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg transition shadow-sm whitespace-nowrap"
          >
            <Plus className="w-4 h-4" />
            <span>Add Master Item</span>
          </button>
        </div>
      </div>

      {/* Product Library Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-5">
        {filteredItems.map((item, idx) => (
          <div
            key={item.id || idx}
            className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm hover:shadow-md transition flex flex-col"
          >
            <div className="h-40 bg-slate-100 relative overflow-hidden">
              <img
                src={item.image_url}
                alt={item.name_en}
                className="w-full h-full object-cover"
                onError={(e) => {
                  (e.currentTarget as HTMLImageElement).src =
                    'https://images.unsplash.com/photo-1542838132-92c53300491e?w=500&q=80';
                }}
              />
              <span className="absolute top-2.5 right-2.5 px-2 py-0.5 rounded text-[10px] font-bold bg-slate-900/80 text-white backdrop-blur-sm">
                {item.standard_unit}
              </span>
            </div>

            <div className="p-4 flex-1 flex flex-col justify-between">
              <div>
                <span className="text-[10px] font-bold text-emerald-700 uppercase tracking-wider block mb-1">
                  {item.category}
                </span>
                <h4 className="font-extrabold text-slate-800 text-sm leading-snug line-clamp-1">
                  {item.name_en}
                </h4>
                <div className="text-xs text-slate-500 font-medium mt-0.5 line-clamp-1">
                  {item.name_hi}
                </div>
              </div>

              <div className="mt-3 pt-3 border-t border-slate-100 flex items-center justify-between">
                <div>
                  <span className="text-[10px] text-slate-400 block">Suggested Price</span>
                  <span className="font-extrabold text-slate-900 text-sm">
                    ₹{(item.suggested_price || item.suggested_mrp || 0).toFixed(2)}
                  </span>
                </div>
                <span className="text-[10px] text-emerald-600 bg-emerald-50 px-2 py-1 rounded font-semibold border border-emerald-200">
                  Master Library
                </span>
              </div>
            </div>
          </div>
        ))}

        {filteredItems.length === 0 && (
          <div className="col-span-full p-12 text-center text-slate-400 bg-white rounded-xl border border-slate-200">
            No master catalog items match your search.
          </div>
        )}
      </div>

      {/* Add Master Item Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl border border-slate-200">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <h3 className="font-extrabold text-slate-800 text-base">Add Master Product</h3>
              <button
                onClick={() => setIsModalOpen(false)}
                className="text-slate-400 hover:text-slate-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="mt-4 space-y-3.5">
              <div>
                <label className="text-xs font-bold text-slate-700 block mb-1">
                  English Product Name *
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Fortune Mustard Oil"
                  value={formData.name_en}
                  onChange={(e) => setFormData({ ...formData, name_en: e.target.value })}
                  className="w-full text-xs px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
                />
              </div>

              <div>
                <label className="text-xs font-bold text-slate-700 block mb-1">
                  Hindi Product Name (हिंदी नाम) *
                </label>
                <input
                  type="text"
                  required
                  placeholder="उदा. फॉर्च्यून सरसों का तेल"
                  value={formData.name_hi}
                  onChange={(e) => setFormData({ ...formData, name_hi: e.target.value })}
                  className="w-full text-xs px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-bold text-slate-700 block mb-1">Category</label>
                  <select
                    value={formData.category}
                    onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                    className="w-full text-xs px-2.5 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
                  >
                    <option value="Grocery & Ration">Grocery & Ration</option>
                    <option value="Vegetables & Fruits">Vegetables & Fruits</option>
                    <option value="Fresh Dairy">Fresh Dairy</option>
                    <option value="Pooja & Rituals">Pooja & Rituals</option>
                    <option value="Electrical & Hardware">Electrical & Hardware</option>
                    <option value="General Store">General Store</option>
                  </select>
                </div>

                <div>
                  <label className="text-xs font-bold text-slate-700 block mb-1">
                    Standard Unit
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. 1 kg, 500 ml"
                    value={formData.standard_unit}
                    onChange={(e) => setFormData({ ...formData, standard_unit: e.target.value })}
                    className="w-full text-xs px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-bold text-slate-700 block mb-1">
                    Suggested Price (₹)
                  </label>
                  <input
                    type="number"
                    step="0.5"
                    required
                    value={formData.suggested_price}
                    onChange={(e) =>
                      setFormData({ ...formData, suggested_price: parseFloat(e.target.value) || 0 })
                    }
                    className="w-full text-xs px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
                  />
                </div>

                <div>
                  <label className="text-xs font-bold text-slate-700 block mb-1">
                    Image URL
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.image_url}
                    onChange={(e) => setFormData({ ...formData, image_url: e.target.value })}
                    className="w-full text-xs px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
                  />
                </div>
              </div>

              <div className="pt-3 border-t border-slate-100 flex items-center justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-lg transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-4 py-2 text-xs font-bold text-white bg-emerald-600 hover:bg-emerald-700 rounded-lg transition shadow-sm"
                >
                  {isSubmitting ? 'Adding...' : 'Save Product'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
