import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import 'package:shared_models/shared_models.dart';
import '../state/vendor_state.dart';

class ProductLibraryScreen extends StatefulWidget {
  const ProductLibraryScreen({super.key});

  @override
  State<ProductLibraryScreen> createState() => _ProductLibraryScreenState();
}

class _ProductLibraryScreenState extends State<ProductLibraryScreen> {
  final TextEditingController _searchCtrl = TextEditingController();

  final List<Map<String, dynamic>> _centralLibrary = [
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
      'name_en': 'Basmati Rice (Minapur)',
      'name_hi': 'बासमती चावल',
      'category': 'Grocery',
      'unit': '1 kg',
      'suggested_price': 54.0,
      'image_url': 'https://images.unsplash.com/photo-1586201375761-83865001e31c?w=400',
    },
    {
      'id': 'cat_mustard_oil',
      'name_en': 'Mustard Oil (Sarson Tel)',
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
      'name_en': 'Local Potato (Aloo)',
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
      'name_hi': '९ वॉट एलईडी बल्ब',
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

  void _showAddPriceDialog(Map<String, dynamic> item) {
    final priceCtrl = TextEditingController(text: item['suggested_price'].toString());
    final stockCtrl = TextEditingController(text: '50');

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text('${item['name_hi']} जोड़ें'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                ClipRRect(
                  borderRadius: BorderRadius.circular(8),
                  child: Image.network(item['image_url'] as String, width: 50, height: 50, fit: BoxFit.cover),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(item['name_hi'] as String, style: const TextStyle(fontWeight: FontWeight.w700)),
                      Text('इकाई (Unit): ${item['unit']}', style: const TextStyle(fontSize: 12, color: Colors.grey)),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            TextField(
              controller: priceCtrl,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(labelText: 'आपका बिक्री मूल्य ₹ (Selling Price)'),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: stockCtrl,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(labelText: 'उपलब्ध स्टॉक मात्रा (Stock Quantity)'),
            ),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.of(ctx).pop(), child: const Text('रद्द करें')),
          ElevatedButton(
            onPressed: () {
              final price = double.tryParse(priceCtrl.text) ?? (item['suggested_price'] as double);
              final stock = int.tryParse(stockCtrl.text) ?? 50;

              final prod = GBProduct(
                id: 'prod_${DateTime.now().millisecondsSinceEpoch}',
                storeId: 'str_01',
                globalProductId: item['id'] as String,
                nameEn: item['name_en'] as String,
                nameHi: item['name_hi'] as String,
                category: item['category'] as String,
                unit: item['unit'] as String,
                price: price,
                imageUrl: item['image_url'] as String,
                stockQuantity: stock,
                inStock: true,
              );

              VendorStateProvider.of(context).addProduct(prod);
              Navigator.of(ctx).pop();
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text('${prod.nameHi} आपकी दुकान में जोड़ दिया गया!')),
              );
            },
            child: const Text('दुकान में जोड़ें (Add)'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final filtered = _centralLibrary.where((item) {
      if (_searchCtrl.text.isEmpty) return true;
      final q = _searchCtrl.text.toLowerCase();
      return (item['name_en'] as String).toLowerCase().contains(q) ||
          (item['name_hi'] as String).toLowerCase().contains(q);
    }).toList();

    return Scaffold(
      appBar: AppBar(
        title: const Text('केंद्रीय उत्पाद लाइब्रेरी (Product Catalog)', style: TextStyle(fontWeight: FontWeight.w800, fontSize: 16)),
      ),
      body: SafeArea(
        child: Column(
          children: [
            Padding(
              padding: const EdgeInsets.all(16),
              child: TextField(
                controller: _searchCtrl,
                onChanged: (v) => setState(() {}),
                decoration: InputDecoration(
                  hintText: 'आलू, प्याज, आटा, दूध, तेल खोजें...',
                  prefixIcon: const Icon(Icons.search, color: GBColors.primary),
                  filled: true,
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                ),
              ),
            ),
            Expanded(
              child: ListView.builder(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                itemCount: filtered.length,
                itemBuilder: (context, idx) {
                  final item = filtered[idx];
                  return Container(
                    margin: const EdgeInsets.only(bottom: 12),
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: Colors.grey.shade300),
                    ),
                    child: Row(
                      children: [
                        ClipRRect(
                          borderRadius: BorderRadius.circular(8),
                          child: Image.network(item['image_url'] as String, width: 56, height: 56, fit: BoxFit.cover),
                        ),
                        const SizedBox(width: 14),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(item['name_hi'] as String, style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 14)),
                              Text(item['name_en'] as String, style: const TextStyle(fontSize: 12, color: Colors.grey)),
                              const SizedBox(height: 4),
                              Text(
                                'सुझाया गया मूल्य: ₹${item['suggested_price']} / ${item['unit']}',
                                style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: GBColors.primary),
                              ),
                            ],
                          ),
                        ),
                        ElevatedButton.icon(
                          onPressed: () => _showAddPriceDialog(item),
                          icon: const Icon(Icons.add, size: 16),
                          label: const Text('चुनें'),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: GBColors.primary,
                            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
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
