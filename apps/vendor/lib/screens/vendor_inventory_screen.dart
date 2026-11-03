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

  void _showAddCustomProductDialog(BuildContext context, VendorAppState state) {
    final loc = GBLocalizations.of(context);
    final isHi = loc.isHindi;

    final nameHiCtrl = TextEditingController();
    final nameEnCtrl = TextEditingController();
    final priceCtrl = TextEditingController();
    final mrpCtrl = TextEditingController();
    final stockCtrl = TextEditingController(text: '25');
    String selectedCategory = 'Grocery';
    String selectedUnit = '1 kg';
    String selectedImageUrl = 'https://images.unsplash.com/photo-1586201375761-83865001e31c?w=400';

    final presetImages = [
      {'name': isHi ? 'अनाज / चावल' : 'Grains / Rice', 'url': 'https://images.unsplash.com/photo-1586201375761-83865001e31c?w=400'},
      {'name': isHi ? 'सब्ज़ियां' : 'Vegetables', 'url': 'https://images.unsplash.com/photo-1546470427-227c7369a941?w=400'},
      {'name': isHi ? 'दूध / घी' : 'Dairy / Ghee', 'url': 'https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400'},
      {'name': isHi ? 'सरसों तेल' : 'Cooking Oil', 'url': 'https://upload.wikimedia.org/wikipedia/commons/e/e1/Dune_Aura_Mustard_oil_bottle_picture.jpg'},
      {'name': isHi ? 'गुड़ / शक्कर' : 'Jaggery / Sugar', 'url': 'https://images.unsplash.com/photo-1622484212850-eb596d769edc?w=400'},
      {'name': isHi ? 'पूजा सामग्री' : 'Pooja Items', 'url': 'https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?w=400'},
    ];

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
      builder: (ctx) => StatefulBuilder(
        builder: (bottomCtx, setModalState) {
          return Padding(
            padding: EdgeInsets.only(
              left: 20,
              right: 20,
              top: 20,
              bottom: MediaQuery.of(ctx).viewInsets.bottom + 20,
            ),
            child: SingleChildScrollView(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.add_business, color: GBColors.primary, size: 26),
                      const SizedBox(width: 10),
                      Expanded(
                        child: Text(
                          isHi ? 'दुकान में नया सामान जोड़ें' : 'Add Custom Product to Store',
                          style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 14),
                  TextField(
                    controller: nameHiCtrl,
                    decoration: InputDecoration(
                      labelText: isHi ? 'सामग्री का नाम (हिंदी में)' : 'Product Name (Hindi)',
                      hintText: isHi ? 'उदा. देशी चना सत्तू' : 'e.g. Desi Chana Sattu',
                      border: const OutlineInputBorder(),
                    ),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: nameEnCtrl,
                    decoration: InputDecoration(
                      labelText: isHi ? 'सामग्री का नाम (English)' : 'Product Name (English)',
                      hintText: 'e.g. Roasted Gram Sattu 500g',
                      border: const OutlineInputBorder(),
                    ),
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Expanded(
                        child: DropdownButtonFormField<String>(
                          value: selectedCategory,
                          decoration: InputDecoration(
                            labelText: isHi ? 'श्रेणी' : 'Category',
                            border: const OutlineInputBorder(),
                          ),
                          items: ['Grocery', 'Vegetables', 'Dairy', 'Snacks', 'Pooja', 'Spices', 'Household']
                              .map((c) => DropdownMenuItem(value: c, child: Text(c)))
                              .toList(),
                          onChanged: (v) => setModalState(() => selectedCategory = v ?? 'Grocery'),
                        ),
                      ),
                      const SizedBox(width: 10),
                      Expanded(
                        child: DropdownButtonFormField<String>(
                          value: selectedUnit,
                          decoration: InputDecoration(
                            labelText: isHi ? 'माप / इकाई' : 'Unit',
                            border: const OutlineInputBorder(),
                          ),
                          items: ['500 g', '1 kg', '2 kg', '5 kg', '1 L', '500 ml', '1 pack', '1 piece', '1 dozen']
                              .map((u) => DropdownMenuItem(value: u, child: Text(u)))
                              .toList(),
                          onChanged: (v) => setModalState(() => selectedUnit = v ?? '1 kg'),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Expanded(
                        child: TextField(
                          controller: priceCtrl,
                          keyboardType: const TextInputType.numberWithOptions(decimal: true),
                          decoration: InputDecoration(
                            labelText: isHi ? 'बिक्री मूल्य (₹)' : 'Selling Price (₹)',
                            prefixText: '₹ ',
                            border: const OutlineInputBorder(),
                          ),
                        ),
                      ),
                      const SizedBox(width: 10),
                      Expanded(
                        child: TextField(
                          controller: mrpCtrl,
                          keyboardType: const TextInputType.numberWithOptions(decimal: true),
                          decoration: InputDecoration(
                            labelText: isHi ? 'एमआरपी (₹)' : 'MRP (₹)',
                            prefixText: '₹ ',
                            border: const OutlineInputBorder(),
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: stockCtrl,
                    keyboardType: TextInputType.number,
                    decoration: InputDecoration(
                      labelText: isHi ? 'उपलब्ध स्टॉक मात्रा (Units)' : 'Initial Stock Quantity (Units)',
                      border: const OutlineInputBorder(),
                    ),
                  ),
                  const SizedBox(height: 14),
                  Text(
                    isHi ? 'सामग्री की फोटो चुनें:' : 'Select Product Photo:',
                    style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13),
                  ),
                  const SizedBox(height: 8),
                  SizedBox(
                    height: 40,
                    child: ListView(
                      scrollDirection: Axis.horizontal,
                      children: presetImages.map((img) {
                        final isSel = selectedImageUrl == img['url'];
                        return Padding(
                          padding: const EdgeInsets.only(right: 8),
                          child: ChoiceChip(
                            label: Text(img['name']!),
                            selected: isSel,
                            selectedColor: GBColors.primary.withAlpha(50),
                            onSelected: (_) => setModalState(() => selectedImageUrl = img['url']!),
                          ),
                        );
                      }).toList(),
                    ),
                  ),
                  const SizedBox(height: 18),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: GBColors.primary,
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 14),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                      ),
                      onPressed: () async {
                        final nameHi = nameHiCtrl.text.trim();
                        final nameEn = nameEnCtrl.text.trim();
                        final price = double.tryParse(priceCtrl.text.trim()) ?? 0.0;
                        final mrp = double.tryParse(mrpCtrl.text.trim()) ?? price;
                        final stock = int.tryParse(stockCtrl.text.trim()) ?? 10;

                        if (nameHi.isEmpty && nameEn.isEmpty) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(content: Text(isHi ? 'कृपया सामग्री का नाम दर्ज करें' : 'Please enter product name')),
                          );
                          return;
                        }
                        if (price <= 0) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(content: Text(isHi ? 'कृपया मान्य विक्रय मूल्य दर्ज करें' : 'Please enter valid price')),
                          );
                          return;
                        }

                        Navigator.of(ctx).pop();
                        final success = await state.addProduct({
                          'name_hi': nameHi.isNotEmpty ? nameHi : nameEn,
                          'name_en': nameEn.isNotEmpty ? nameEn : nameHi,
                          'category': selectedCategory,
                          'unit': selectedUnit,
                          'price': price,
                          'mrp': mrp,
                          'stock_quantity': stock,
                          'in_stock': true,
                          'image_url': selectedImageUrl,
                        });

                        if (context.mounted) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(
                              content: Text(
                                success
                                    ? (isHi ? 'सामग्री दुकान में सफलतापूर्वक जुड़ गई!' : 'Product added to store catalog!')
                                    : (isHi ? 'सामग्री सुरक्षित सहेजी गई' : 'Product saved locally'),
                              ),
                              backgroundColor: GBColors.success,
                            ),
                          );
                          state.fetchProducts();
                        }
                      },
                      child: Text(
                        isHi ? 'दुकान में जोड़ें (Add to Store)' : 'Add to My Store',
                        style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 15),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          );
        },
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
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          tooltip: loc.isHindi ? 'पीछे जाएं' : 'Back',
          onPressed: () => Navigator.of(context).pop(),
        ),
        title: Text(
          loc.tr('menu_inventory'),
          style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.library_add, color: GBColors.primary, size: 24),
            tooltip: loc.isHindi ? 'केंद्रीय लाइब्रेरी' : 'Central Library',
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
                              child: Padding(
                                padding: const EdgeInsets.only(right: 6),
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    Text(
                                      loc.isHindi ? p.nameHi : p.nameEn,
                                      maxLines: 2,
                                      overflow: TextOverflow.ellipsis,
                                      softWrap: true,
                                      style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 14, height: 1.25),
                                    ),
                                    const SizedBox(height: 2),
                                    Text(
                                      '₹${p.price.toStringAsFixed(0)} / ${p.unit} • ${loc.isHindi ? "स्टॉक" : "Stock"}: ${p.stockQuantity}',
                                      maxLines: 1,
                                      overflow: TextOverflow.ellipsis,
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
      floatingActionButton: FloatingActionButton.extended(
        backgroundColor: GBColors.primary,
        foregroundColor: Colors.white,
        icon: const Icon(Icons.add),
        label: Text(
          loc.isHindi ? 'नया सामान जोड़ें' : 'Add Custom Product',
          style: const TextStyle(fontWeight: FontWeight.w700),
        ),
        onPressed: () => _showAddCustomProductDialog(context, state),
      ),
    );
  }
}
