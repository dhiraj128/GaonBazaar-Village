import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import 'package:localization/localization.dart';
import '../state/vendor_state.dart';

class ProductLibraryScreen extends StatefulWidget {
  const ProductLibraryScreen({super.key});

  @override
  State<ProductLibraryScreen> createState() => _ProductLibraryScreenState();
}

class _ProductLibraryScreenState extends State<ProductLibraryScreen> {
  final TextEditingController _searchCtrl = TextEditingController();
  List<Map<String, dynamic>> _catalog = [];
  bool _isLoading = true;

  final List<Map<String, dynamic>> _defaultLibrary = [
    {
      'id': 'cat_atta',
      'name_en': 'Chakki Fresh Atta',
      'name_hi': 'ताज़ा चक्की आटा',
      'category': 'Grocery',
      'unit': '1 kg',
      'suggested_price': 38.0,
      'image_url': 'https://images.unsplash.com/photo-1509440159596-0249088772ff?w=400',
    },
    {
      'id': 'cat_rice',
      'name_en': 'Basmati Rice (Minapur Special)',
      'name_hi': 'बासमती चावल',
      'category': 'Grocery',
      'unit': '1 kg',
      'suggested_price': 54.0,
      'image_url': 'https://images.unsplash.com/photo-1586201375761-83865001e31c?w=400',
    },
    {
      'id': 'cat_mustard_oil',
      'name_en': 'Kachhi Ghani Mustard Oil',
      'name_hi': 'कच्ची घानी सरसों तेल',
      'category': 'Grocery',
      'unit': '1 L',
      'suggested_price': 142.0,
      'image_url': 'https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=400',
    },
    {
      'id': 'cat_milk',
      'name_en': 'Fresh Cow Milk',
      'name_hi': 'ताज़ा गाय का दूध',
      'category': 'Dairy',
      'unit': '1 L',
      'suggested_price': 56.0,
      'image_url': 'https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400',
    },
    {
      'id': 'cat_potato',
      'name_en': 'Fresh Local Potato (Aloo)',
      'name_hi': 'ताज़ा देशी आलू',
      'category': 'Vegetables',
      'unit': '1 kg',
      'suggested_price': 24.0,
      'image_url': 'https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=400',
    },
    {
      'id': 'cat_onion',
      'name_en': 'Red Onion (Pyaz)',
      'name_hi': 'लाल प्याज़',
      'category': 'Vegetables',
      'unit': '1 kg',
      'suggested_price': 32.0,
      'image_url': 'https://images.unsplash.com/photo-1618512496248-a07fe83aa8cb?w=400',
    },
    {
      'id': 'cat_tomato',
      'name_en': 'Fresh Tomato (Tamatar)',
      'name_hi': 'देशी टमाटर',
      'category': 'Vegetables',
      'unit': '1 kg',
      'suggested_price': 28.0,
      'image_url': 'https://images.unsplash.com/photo-1546470427-227c7369a941?w=400',
    },
    {
      'id': 'cat_pooja_agarbatti',
      'name_en': 'Chandan Agarbatti',
      'name_hi': 'चंदन अगरबत्ती',
      'category': 'Pooja',
      'unit': '1 pack',
      'suggested_price': 20.0,
      'image_url': 'https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?w=400',
    },
    {
      'id': 'cat_led_bulb',
      'name_en': '9W LED Bulb',
      'name_hi': '9W एलईडी बल्ब',
      'category': 'Electrical',
      'unit': '1 piece',
      'suggested_price': 85.0,
      'image_url': 'https://images.unsplash.com/photo-1550985543-f47f38aeee65?w=400',
    },
    {
      'id': 'cat_sugar',
      'name_en': 'Pure Refined Sugar (Cheeni)',
      'name_hi': 'सफ़ेद चीनी (शक्कर)',
      'category': 'Grocery',
      'unit': '1 kg',
      'suggested_price': 44.0,
      'image_url': 'https://images.unsplash.com/photo-1622484212850-eb596d769edc?w=400',
    },
    {
      'id': 'cat_salt',
      'name_en': 'Tata Iodized Salt (Namak)',
      'name_hi': 'आयोडीन युक्त नमक',
      'category': 'Grocery',
      'unit': '1 kg',
      'suggested_price': 26.0,
      'image_url': 'https://images.unsplash.com/photo-1626082896492-766af4eb6501?w=400',
    },
    {
      'id': 'cat_biscuits',
      'name_en': 'Parle-G Glucose Biscuits',
      'name_hi': 'पारले-जी ग्लूकोज बिस्कुट',
      'category': 'Snacks',
      'unit': '1 pack (250g)',
      'suggested_price': 25.0,
      'image_url': 'https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=400',
    },
    {
      'id': 'cat_green_chili',
      'name_en': 'Fresh Green Chili & Coriander',
      'name_hi': 'ताज़ा हरी मिर्च और धनिया',
      'category': 'Vegetables',
      'unit': '250 g',
      'suggested_price': 18.0,
      'image_url': 'https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=400',
    },
    {
      'id': 'cat_toor_dal',
      'name_en': 'Desi Toor / Arhar Dal',
      'name_hi': 'देशी अरहर दाल',
      'category': 'Grocery',
      'unit': '1 kg',
      'suggested_price': 140.0,
      'image_url': 'https://images.unsplash.com/photo-1585994192701-f1a505c817ea?w=400',
    },
  ];

  @override
  void initState() {
    super.initState();
    _loadCatalog();
  }

  void _loadCatalog() async {
    final state = VendorStateProvider.of(context);
    final res = await state.apiClient.getGlobalCatalog();
    if (res.isSuccess && res.data != null && res.data!.isNotEmpty) {
      _catalog = res.data!.map((item) {
        return {
          'id': item['id'],
          'name_en': item['name_en'] ?? 'Product',
          'name_hi': item['name_hi'] ?? 'उत्पाद',
          'category': item['category'] ?? 'Grocery',
          'unit': item['default_unit'] ?? '1 kg',
          'suggested_price': (item['suggested_mrp'] as num?)?.toDouble() ?? 50.0,
          'image_url': item['image_url'] ?? 'https://images.unsplash.com/photo-1542838132-92c53300491e?w=400',
        };
      }).toList();
    } else {
      _catalog = List.from(_defaultLibrary);
    }
    if (mounted) setState(() => _isLoading = false);
  }

  @override
  void dispose() {
    _searchCtrl.dispose();
    super.dispose();
  }

  void _showAddPriceDialog(Map<String, dynamic> item) {
    final state = VendorStateProvider.of(context);
    final loc = GBLocalizations.of(context);
    final priceCtrl = TextEditingController(text: item['suggested_price'].toString());
    final stockCtrl = TextEditingController(text: '50');
    final unitCtrl = TextEditingController(text: item['unit'].toString());

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(
          loc.isHindi ? '${item['name_hi']} दुकान में जोड़ें' : 'Add ${item['name_en']}',
          style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16),
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                ClipRRect(
                  borderRadius: BorderRadius.circular(8),
                  child: Image.network(
                    item['image_url'] as String,
                    width: 50,
                    height: 50,
                    fit: BoxFit.cover,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        loc.isHindi ? (item['name_hi'] as String) : (item['name_en'] as String),
                        style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 14),
                      ),
                      Text(
                        'Category: ${item['category']}',
                        style: const TextStyle(fontSize: 11, color: Colors.grey),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            TextField(
              controller: priceCtrl,
              keyboardType: const TextInputType.numberWithOptions(decimal: true),
              decoration: InputDecoration(
                labelText: loc.isHindi ? 'आपका विक्रय मूल्य (₹) *' : 'Your Selling Price (₹) *',
                prefixText: '₹ ',
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
              ),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: unitCtrl,
                    decoration: InputDecoration(
                      labelText: loc.isHindi ? 'इकाई (Unit)' : 'Unit',
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                    ),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: TextField(
                    controller: stockCtrl,
                    keyboardType: TextInputType.number,
                    decoration: InputDecoration(
                      labelText: loc.isHindi ? 'स्टॉक मात्रा' : 'Stock Qty',
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(),
            child: Text(loc.tr('cancel')),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: GBColors.primary,
              foregroundColor: Colors.white,
            ),
            onPressed: () async {
              final price = double.tryParse(priceCtrl.text.trim()) ?? (item['suggested_price'] as double);
              final stock = int.tryParse(stockCtrl.text.trim()) ?? 50;

              final productPayload = {
                'global_product_id': item['id'],
                'custom_name_en': item['name_en'],
                'custom_name_hi': item['name_hi'],
                'category': item['category'],
                'unit': unitCtrl.text.trim(),
                'price': price,
                'mrp': price * 1.15,
                'image_url': item['image_url'],
                'stock_quantity': stock,
                'in_stock': true,
              };

              Navigator.of(ctx).pop();
              final success = await state.addProduct(productPayload);

              if (mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text(
                      success ? loc.tr('product_added_success') : 'Failed to add product to store',
                    ),
                    backgroundColor: success ? GBColors.success : GBColors.error,
                  ),
                );
              }
            },
            child: Text(loc.tr('add_to_my_store')),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final state = VendorStateProvider.of(context);
    final loc = GBLocalizations.of(context);
    final query = _searchCtrl.text.trim().toLowerCase();

    final filtered = _catalog.where((item) {
      if (query.isEmpty) return true;
      final en = (item['name_en'] as String).toLowerCase();
      final hi = (item['name_hi'] as String).toLowerCase();
      final cat = (item['category'] as String).toLowerCase();
      return en.contains(query) || hi.contains(query) || cat.contains(query);
    }).toList();

    return Scaffold(
      appBar: AppBar(
        title: Text(
          loc.tr('menu_catalog'),
          style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16),
        ),
      ),
      body: SafeArea(
        child: Column(
          children: [
            // Search Input
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              child: TextField(
                controller: _searchCtrl,
                onChanged: (_) => setState(() {}),
                decoration: InputDecoration(
                  hintText: loc.isHindi ? 'सामग्री या श्रेणी खोजें...' : 'Search items or category...',
                  prefixIcon: const Icon(Icons.search),
                  suffixIcon: _searchCtrl.text.isNotEmpty
                      ? IconButton(
                          icon: const Icon(Icons.clear),
                          onPressed: () {
                            _searchCtrl.clear();
                            setState(() {});
                          },
                        )
                      : null,
                  filled: true,
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: BorderSide.none,
                  ),
                ),
              ),
            ),

            // Products List
            Expanded(
              child: _isLoading
                  ? const Center(child: GBLoadingState())
                  : filtered.isEmpty
                      ? Center(
                          child: Text(
                            loc.isHindi ? 'कोई उत्पाद नहीं मिला' : 'No products found',
                            style: const TextStyle(color: Colors.grey),
                          ),
                        )
                      : ListView.builder(
                          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
                          itemCount: filtered.length,
                          itemBuilder: (context, idx) {
                            final item = filtered[idx];
                            final alreadyAdded = state.myProducts.any(
                              (p) => p.nameEn == item['name_en'] || p.nameHi == item['name_hi'],
                            );

                            return Container(
                              margin: const EdgeInsets.only(bottom: 12),
                              padding: const EdgeInsets.all(12),
                              decoration: BoxDecoration(
                                color: Theme.of(context).cardColor,
                                borderRadius: BorderRadius.circular(12),
                                border: Border.all(color: Colors.grey.withOpacity(0.2)),
                              ),
                              child: Row(
                                children: [
                                  ClipRRect(
                                    borderRadius: BorderRadius.circular(8),
                                    child: Image.network(
                                      item['image_url'] as String,
                                      width: 56,
                                      height: 56,
                                      fit: BoxFit.cover,
                                      errorBuilder: (ctx, err, stack) => const Icon(
                                        Icons.shopping_basket_outlined,
                                        size: 32,
                                        color: GBColors.primary,
                                      ),
                                    ),
                                  ),
                                  const SizedBox(width: 12),
                                  Expanded(
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        Text(
                                          loc.isHindi ? (item['name_hi'] as String) : (item['name_en'] as String),
                                          style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 14),
                                        ),
                                        const SizedBox(height: 2),
                                        Text(
                                          '${item['category']} • ${item['unit']}',
                                          style: const TextStyle(fontSize: 12, color: Colors.grey),
                                        ),
                                        const SizedBox(height: 4),
                                        Text(
                                          '₹${(item['suggested_price'] as num).toStringAsFixed(0)}',
                                          style: const TextStyle(
                                            fontWeight: FontWeight.w800,
                                            fontSize: 14,
                                            color: GBColors.primary,
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),
                                  ElevatedButton(
                                    style: ElevatedButton.styleFrom(
                                      backgroundColor: alreadyAdded ? Colors.grey.shade400 : GBColors.primary,
                                      foregroundColor: Colors.white,
                                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                                    ),
                                    onPressed: alreadyAdded ? null : () => _showAddPriceDialog(item),
                                    child: Text(
                                      alreadyAdded
                                          ? (loc.isHindi ? 'जोड़ा हुआ' : 'Added')
                                          : (loc.isHindi ? 'जोड़ें' : 'Add'),
                                      style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700),
                                    ),
                                  ),
                                ],
                              ),
                            );
                          },
                        ),
            ),
          ],
        ),
      ),
    );
  }
}
