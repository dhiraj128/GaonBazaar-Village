import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import 'package:shared_models/shared_models.dart';
import '../state/vendor_state.dart';
import 'product_library_screen.dart';

class VendorInventoryScreen extends StatelessWidget {
  const VendorInventoryScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final state = VendorStateProvider.of(context);

    // Initial seed products if empty
    if (state.myProducts.isEmpty) {
      state.myProducts = [
        GBProduct(
          id: 'prd_01',
          storeId: 'str_01',
          nameEn: 'Chakki Fresh Atta',
          nameHi: 'ताज़ा चक्की आटा',
          category: 'Grocery',
          unit: '1 kg',
          price: 38.0,
          mrp: 45.0,
          imageUrl: 'https://images.unsplash.com/photo-1509440159596-0249088772ff?w=400',
          stockQuantity: 45,
          inStock: true,
        ),
        GBProduct(
          id: 'prd_02',
          storeId: 'str_01',
          nameEn: 'Kachhi Ghani Mustard Oil',
          nameHi: 'कच्ची घानी सरसों तेल',
          category: 'Grocery',
          unit: '1 L',
          price: 142.0,
          mrp: 155.0,
          imageUrl: 'https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=400',
          stockQuantity: 28,
          inStock: true,
        ),
        GBProduct(
          id: 'prd_04',
          storeId: 'str_01',
          nameEn: 'Fresh Local Potato (Aloo)',
          nameHi: 'ताज़ा देशी आलू',
          category: 'Vegetables',
          unit: '1 kg',
          price: 24.0,
          mrp: 30.0,
          imageUrl: 'https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=400',
          stockQuantity: 80,
          inStock: true,
        ),
      ];
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('मेरी दुकान की इन्वेंट्री (My Inventory)', style: TextStyle(fontWeight: FontWeight.w800, fontSize: 16)),
        actions: [
          IconButton(
            icon: const Icon(Icons.add_circle, color: GBColors.primary, size: 28),
            onPressed: () {
              Navigator.of(context).push(
                MaterialPageRoute(builder: (_) => const ProductLibraryScreen()),
              );
            },
          ),
        ],
      ),
      body: SafeArea(
        child: ListView.builder(
          padding: const EdgeInsets.all(16),
          itemCount: state.myProducts.length,
          itemBuilder: (context, idx) {
            final p = state.myProducts[idx];
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
                    child: Image.network(p.imageUrl, width: 50, height: 50, fit: BoxFit.cover),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(p.nameHi, style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 14)),
                        Text('₹${p.price.toStringAsFixed(0)} / ${p.unit} • स्टॉक: ${p.stockQuantity}', style: const TextStyle(fontSize: 12, color: Colors.grey)),
                      ],
                    ),
                  ),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      Switch(
                        value: p.inStock,
                        activeColor: GBColors.primary,
                        onChanged: (v) => state.toggleProductStock(p.id),
                      ),
                      Text(
                        p.inStock ? 'उपलब्ध (In Stock)' : 'समाप्त (Out of Stock)',
                        style: TextStyle(
                          fontSize: 10,
                          fontWeight: FontWeight.w700,
                          color: p.inStock ? GBColors.success : GBColors.error,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            );
          },
        ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        backgroundColor: GBColors.primary,
        onPressed: () {
          Navigator.of(context).push(
            MaterialPageRoute(builder: (_) => const ProductLibraryScreen()),
          );
        },
        icon: const Icon(Icons.library_books),
        label: const Text('लाइब्रेरी से नया जोड़ें'),
      ),
    );
  }
}
