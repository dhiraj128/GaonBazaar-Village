import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import 'package:localization/localization.dart';
import 'package:shared_models/shared_models.dart';
import '../state/app_state.dart';

class ProductDetailsScreen extends StatelessWidget {
  final GBProduct product;
  final String storeName;

  const ProductDetailsScreen({
    super.key,
    required this.product,
    required this.storeName,
  });

  @override
  Widget build(BuildContext context) {
    final state = AppStateProvider.of(context);
    final loc = GBLocalizations.of(context);
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final qty = state.getItemQuantity(product.id);

    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          tooltip: loc.isHindi ? 'पीछे जाएं' : 'Back',
          onPressed: () => Navigator.of(context).pop(),
        ),
        title: Text(
          product.getLocalizedName(loc.isHindi),
          style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16),
        ),
      ),
      body: SafeArea(
        child: Column(
          children: [
            Expanded(
              child: ListView(
                padding: const EdgeInsets.all(20),
                children: [
                  // Product Photo
                  Container(
                    constraints: BoxConstraints(
                      maxHeight: MediaQuery.of(context).size.height * 0.30,
                      minHeight: 180,
                    ),
                    width: double.infinity,
                    decoration: BoxDecoration(
                      color: isDark ? GBColors.cardDark : Colors.white,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: isDark ? GBColors.borderDark : GBColors.borderLight),
                    ),
                    child: Center(
                      child: ClipRRect(
                        borderRadius: BorderRadius.circular(16),
                        child: Image.network(
                          product.imageUrl,
                          fit: BoxFit.contain,
                          errorBuilder: (ctx, err, stack) => const Icon(
                            Icons.shopping_bag_outlined,
                            size: 64,
                            color: GBColors.primary,
                          ),
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 20),

                  // Category & In-Stock Badge
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                        decoration: BoxDecoration(
                          color: GBColors.primary.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(6),
                        ),
                        child: Text(
                          product.category,
                          style: const TextStyle(color: GBColors.primary, fontSize: 12, fontWeight: FontWeight.w700),
                        ),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                        decoration: BoxDecoration(
                          color: GBColors.success.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(6),
                        ),
                        child: Row(
                          children: [
                            const Icon(Icons.check_circle, size: 12, color: GBColors.success),
                            const SizedBox(width: 4),
                            Text(
                              loc.isHindi ? 'उपलब्ध है' : 'In Stock',
                              style: const TextStyle(color: GBColors.success, fontSize: 11, fontWeight: FontWeight.w700),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),

                  // Title
                  Text(
                    product.getLocalizedName(loc.isHindi),
                    style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w900),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    loc.isHindi
                        ? 'इकाई: ${product.unit} • दुकान: $storeName'
                        : 'Unit: ${product.unit} • Store: $storeName',
                    style: TextStyle(fontSize: 13, color: isDark ? GBColors.textMutedDark : GBColors.textMutedLight),
                  ),
                  const SizedBox(height: 16),

                  // Price
                  Row(
                    children: [
                      Text(
                        '₹${product.price.toStringAsFixed(0)}',
                        style: const TextStyle(fontSize: 26, fontWeight: FontWeight.w900, color: GBColors.primary),
                      ),
                      if (product.mrp != null && product.mrp! > product.price) ...[
                        const SizedBox(width: 10),
                        Text(
                          '₹${product.mrp!.toStringAsFixed(0)}',
                          style: TextStyle(
                            fontSize: 16,
                            decoration: TextDecoration.lineThrough,
                            color: isDark ? GBColors.textMutedDark : GBColors.textMutedLight,
                          ),
                        ),
                      ],
                    ],
                  ),
                  const Divider(height: 32),

                  // Village Service Guarantee
                  Container(
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(
                      color: isDark ? GBColors.cardDark : Colors.white,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: isDark ? GBColors.borderDark : GBColors.borderLight),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          loc.isHindi ? 'गाँव बाज़ार सेवा गारंटी' : 'GaonBazaar Rural Guarantee',
                          style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 13),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          loc.isHindi
                              ? '• ताज़ा एवं जाँचा-परखा सामान सीधे स्थानीय गाँव की दुकान से।\n• 30-60 मिनट के अंदर गाँव डिलीवरी।\n• केवल ₹3.00 प्लेटफ़ॉर्म शुल्क।'
                              : '• Fresh, quality-checked items directly from local village stores.\n• Village doorstep delivery in 30-60 minutes.\n• Flat ₹3.00 platform fee with 180s cancellation protection.',
                          style: TextStyle(
                            fontSize: 12,
                            height: 1.5,
                            color: isDark ? GBColors.textSecondaryDark : GBColors.textSecondaryLight,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),

            // Bottom Add to Cart CTA
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: isDark ? GBColors.surfaceDark : Colors.white,
                border: Border(top: BorderSide(color: isDark ? GBColors.borderDark : GBColors.borderLight)),
              ),
              child: Row(
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text('₹${product.price.toStringAsFixed(0)}', style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w900)),
                      Text(product.unit, style: const TextStyle(fontSize: 11, color: Colors.grey)),
                    ],
                  ),
                  const Spacer(),
                  GBAddToCartButton(
                    quantity: qty,
                    onAdd: () => state.addToCart(product, storeName),
                    onIncrement: () => state.incrementItem(product.id),
                    onDecrement: () => state.decrementItem(product.id),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
