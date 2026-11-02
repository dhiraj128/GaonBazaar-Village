import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import 'package:localization/localization.dart';
import 'package:shared_models/shared_models.dart';
import '../state/app_state.dart';
import 'product_details_screen.dart';

class StoreDetailsScreen extends StatefulWidget {
  final GBStore store;

  const StoreDetailsScreen({super.key, required this.store});

  @override
  State<StoreDetailsScreen> createState() => _StoreDetailsScreenState();
}

class _StoreDetailsScreenState extends State<StoreDetailsScreen> {
  List<GBProduct> _products = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _fetchProducts();
  }

  Future<void> _fetchProducts() async {
    setState(() => _isLoading = true);
    final state = AppStateProvider.of(context);
    final res = await state.apiClient.getStoreProducts(widget.store.id);
    if (res.isSuccess && res.data != null) {
      _products = res.data!;
    } else {
      // Fallback local products
      _products = [
        GBProduct(
          id: 'prd_01',
          storeId: widget.store.id,
          nameEn: 'Chakki Fresh Atta',
          nameHi: 'ताज़ा चक्की आटा',
          category: 'Grocery',
          unit: '1 kg',
          price: 38.0,
          mrp: 45.0,
          imageUrl: 'https://images.unsplash.com/photo-1509440159596-0249088772ff?w=400',
        ),
        GBProduct(
          id: 'prd_02',
          storeId: widget.store.id,
          nameEn: 'Kachhi Ghani Mustard Oil',
          nameHi: 'कच्ची घानी सरसों तेल',
          category: 'Grocery',
          unit: '1 L',
          price: 142.0,
          mrp: 155.0,
          imageUrl: 'https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=400',
        ),
      ];
    }
    if (mounted) {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = AppStateProvider.of(context);
    final loc = GBLocalizations.of(context);
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      appBar: AppBar(
        title: Text(widget.store.shopName, style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16)),
      ),
      body: SafeArea(
        child: Column(
          children: [
            // Store Info Banner
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: isDark ? GBColors.cardDark : Colors.white,
                border: Border(bottom: BorderSide(color: isDark ? GBColors.borderDark : GBColors.borderLight)),
              ),
              child: Row(
                children: [
                  Container(
                    width: 50,
                    height: 50,
                    decoration: BoxDecoration(
                      color: GBColors.primary.withOpacity(0.12),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: const Icon(Icons.storefront, color: GBColors.primary, size: 28),
                  ),
                  const SizedBox(width: 14),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(widget.store.shopName, style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 15)),
                        Text('${widget.store.village}, ${widget.store.block}', style: TextStyle(fontSize: 12, color: isDark ? GBColors.textMutedDark : GBColors.textMutedLight)),
                        Row(
                          children: [
                            const Icon(Icons.star, size: 14, color: Colors.amber),
                            const SizedBox(width: 4),
                            Text(
                              '${widget.store.rating} • ${widget.store.distanceKm ?? 0.8} ${loc.isHindi ? "किमी दूर" : "km away"}',
                              style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),

            // Products Grid
            Expanded(
              child: _isLoading
                  ? const Center(child: GBLoadingState())
                  : GridView.builder(
                      padding: const EdgeInsets.all(16),
                      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                        crossAxisCount: 2,
                        mainAxisSpacing: 12,
                        crossAxisSpacing: 12,
                        childAspectRatio: 0.68,
                      ),
                      itemCount: _products.length,
                      itemBuilder: (context, index) {
                        final product = _products[index];
                        final qty = state.getItemQuantity(product.id);

                        return GBProductCard(
                          name: product.getLocalizedName(loc.isHindi),
                          unit: product.unit,
                          price: product.price,
                          mrp: product.mrp,
                          imageUrl: product.imageUrl,
                          quantityInCart: qty,
                          onTap: () {
                            Navigator.of(context).push(
                              MaterialPageRoute(
                                builder: (_) => ProductDetailsScreen(
                                  product: product,
                                  storeName: widget.store.shopName,
                                ),
                              ),
                            );
                          },
                          onAdd: () => state.addToCart(product, widget.store.shopName),
                          onIncrement: () => state.incrementItem(product.id),
                          onDecrement: () => state.decrementItem(product.id),
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
