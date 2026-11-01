import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import 'package:localization/localization.dart';
import 'package:shared_models/shared_models.dart';
import '../state/vendor_state.dart';
import 'product_library_screen.dart';

class VendorInventoryScreen extends StatelessWidget {
  const VendorInventoryScreen({super.key});

  void _showEditStockDialog(BuildContext context, VendorAppState state, GBProduct product) {
    final loc = GBLocalizations.of(context);
    final priceCtrl = TextEditingController(text: product.price.toStringAsFixed(0));
    final stockCtrl = TextEditingController(text: product.stockQuantity.toString());

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(
          loc.isHindi ? '${product.nameHi} अपडेट करें' : 'Edit ${product.nameEn}',
          style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16),
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: priceCtrl,
              keyboardType: const TextInputType.numberWithOptions(decimal: true),
              decoration: InputDecoration(
                labelText: loc.isHindi ? 'विक्रय मूल्य (₹)' : 'Selling Price (₹)',
                prefixText: '₹ ',
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
              ),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: stockCtrl,
              keyboardType: TextInputType.number,
              decoration: InputDecoration(
                labelText: loc.isHindi ? 'स्टॉक मात्रा (इकाइयाँ)' : 'Stock Quantity (Units)',
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
              ),
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
              final newPrice = double.tryParse(priceCtrl.text.trim()) ?? product.price;
              final newStock = int.tryParse(stockCtrl.text.trim()) ?? product.stockQuantity;

              Navigator.of(ctx).pop();
              final res = await state.apiClient.updateProductStock(
                product.id,
                price: newPrice,
                stockQuantity: newStock,
              );

              if (res.isSuccess) {
                state.fetchProducts();
                if (context.mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text(loc.tr('stock_updated')),
                      backgroundColor: GBColors.success,
                    ),
                  );
                }
              }
            },
            child: Text(loc.tr('save')),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final state = VendorStateProvider.of(context);
    final loc = GBLocalizations.of(context);
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      appBar: AppBar(
        title: Text(
          loc.tr('menu_inventory'),
          style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16),
        ),
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
        child: state.isLoadingProducts
            ? const Center(child: GBLoadingState())
            : state.myProducts.isEmpty
                ? Center(
                    child: Padding(
                      padding: const EdgeInsets.all(24),
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          const Icon(Icons.inventory_2_outlined, size: 56, color: Colors.grey),
                          const SizedBox(height: 14),
                          Text(
                            loc.isHindi ? 'दुकान में कोई सामान नहीं है' : 'No Products in Your Store',
                            style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 16),
                          ),
                          const SizedBox(height: 6),
                          Text(
                            loc.isHindi
                                ? 'केंद्रीय उत्पाद लाइब्रेरी से सामग्री जोड़कर बिक्री शुरू करें।'
                                : 'Add products from the central catalog to start selling to village customers.',
                            textAlign: TextAlign.center,
                            style: const TextStyle(fontSize: 12, color: Colors.grey),
                          ),
                          const SizedBox(height: 20),
                          ElevatedButton.icon(
                            style: ElevatedButton.styleFrom(
                              backgroundColor: GBColors.primary,
                              foregroundColor: Colors.white,
                            ),
                            icon: const Icon(Icons.add_shopping_cart, size: 18),
                            label: Text(loc.tr('add_to_my_store')),
                            onPressed: () {
                              Navigator.of(context).push(
                                MaterialPageRoute(builder: (_) => const ProductLibraryScreen()),
                              );
                            },
                          ),
                        ],
                      ),
                    ),
                  )
                : ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: state.myProducts.length,
                    itemBuilder: (context, idx) {
                      final p = state.myProducts[idx];
                      return Container(
                        margin: const EdgeInsets.only(bottom: 12),
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: isDark ? GBColors.cardDark : Colors.white,
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(
                            color: isDark ? GBColors.borderDark : Colors.grey.shade300,
                          ),
                        ),
                        child: Row(
                          children: [
                            ClipRRect(
                              borderRadius: BorderRadius.circular(8),
                              child: Image.network(
                                p.imageUrl,
                                width: 54,
                                height: 54,
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
                                    loc.isHindi ? p.nameHi : p.nameEn,
                                    style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 14),
                                  ),
                                  const SizedBox(height: 2),
                                  Text(
                                    '₹${p.price.toStringAsFixed(0)} / ${p.unit} • ${loc.isHindi ? "स्टॉक" : "Stock"}: ${p.stockQuantity}',
                                    style: TextStyle(
                                      fontSize: 12,
                                      color: isDark ? GBColors.textMutedDark : GBColors.textMutedLight,
                                    ),
                                  ),
                                  const SizedBox(height: 4),
                                  Container(
                                    padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                    decoration: BoxDecoration(
                                      color: p.inStock
                                          ? Colors.green.withOpacity(0.1)
                                          : Colors.red.withOpacity(0.1),
                                      borderRadius: BorderRadius.circular(4),
                                    ),
                                    child: Text(
                                      p.inStock ? loc.tr('in_stock') : loc.tr('out_of_stock'),
                                      style: TextStyle(
                                        fontSize: 10,
                                        fontWeight: FontWeight.w700,
                                        color: p.inStock ? GBColors.success : GBColors.error,
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            // Stock Toggle Switch
                            Switch(
                              value: p.inStock,
                              activeColor: GBColors.success,
                              onChanged: (_) => state.toggleProductStock(p.id),
                            ),
                            IconButton(
                              icon: const Icon(Icons.edit_outlined, size: 20, color: GBColors.primary),
                              onPressed: () => _showEditStockDialog(context, state, p),
                            ),
                          ],
                        ),
                      );
                    },
                  ),
      ),
    );
  }
}
