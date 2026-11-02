import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import 'package:localization/localization.dart';
import '../state/app_state.dart';
import 'checkout_screen.dart';
import 'map_picker_screen.dart';

class CartTab extends StatelessWidget {
  final Function(int) onTabChange;

  const CartTab({super.key, required this.onTabChange});

  @override
  Widget build(BuildContext context) {
    final state = AppStateProvider.of(context);
    final loc = GBLocalizations.of(context);
    final isDark = Theme.of(context).brightness == Brightness.dark;

    if (state.cartItems.isEmpty) {
      return Scaffold(
        appBar: AppBar(
          leading: IconButton(
            icon: const Icon(Icons.arrow_back),
            tooltip: loc.isHindi ? 'होम पर वापस जाएं' : 'Back to Home',
            onPressed: () => onTabChange(0),
          ),
          title: Text(loc.tr('my_cart'), style: const TextStyle(fontWeight: FontWeight.w800)),
        ),
        body: GBEmptyState(
          title: loc.tr('cart_empty'),
          message: loc.tr('cart_empty_msg'),
          actionLabel: loc.isHindi ? 'खरीदारी शुरू करें' : 'Start Shopping',
          onAction: () => onTabChange(0), // Switch to Home Tab
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          tooltip: loc.isHindi ? 'होम पर वापस जाएं' : 'Back to Home',
          onPressed: () => onTabChange(0),
        ),
        title: Text(loc.tr('my_cart'), style: const TextStyle(fontWeight: FontWeight.w800)),
        actions: [
          TextButton(
            onPressed: () => state.clearCart(),
            child: Text(
              loc.isHindi ? 'खाली करें' : 'Clear',
              style: const TextStyle(color: GBColors.error, fontWeight: FontWeight.w700),
            ),
          ),
        ],
      ),
      body: SafeArea(
        child: Column(
          children: [
            Expanded(
              child: ListView(
                padding: const EdgeInsets.all(16),
                children: [
                  // Store banner
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: GBColors.primary.withOpacity(0.08),
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(color: GBColors.primary.withOpacity(0.3)),
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.storefront, color: GBColors.primary, size: 20),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            state.currentCartStoreName ?? (loc.isHindi ? 'माँ शारदा किराना स्टोर' : 'Maa Sharda Kirana Store'),
                            style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 14),
                          ),
                        ),
                        Text(
                          loc.isHindi ? '~35 मिनट' : '~35 mins',
                          style: const TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w700,
                            color: GBColors.primary,
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 16),

                  // Cart item list
                  ...state.cartItems.map((item) {
                    final p = item.product;
                    return Container(
                      margin: const EdgeInsets.only(bottom: 12),
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: isDark ? GBColors.cardDark : Colors.white,
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(
                          color: isDark ? GBColors.borderDark : GBColors.borderLight,
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
                                size: 30,
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
                                  p.getLocalizedName(loc.isHindi),
                                  style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 14),
                                ),
                                const SizedBox(height: 2),
                                Text(
                                  p.unit,
                                  style: TextStyle(
                                    fontSize: 12,
                                    color: isDark ? GBColors.textMutedDark : GBColors.textMutedLight,
                                  ),
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  '₹${p.price.toStringAsFixed(0)}',
                                  style: const TextStyle(
                                    fontWeight: FontWeight.w800,
                                    fontSize: 14,
                                    color: GBColors.primary,
                                  ),
                                ),
                              ],
                            ),
                          ),
                          GBAddToCartButton(
                            quantity: item.quantity,
                            onAdd: () => state.incrementItem(p.id),
                            onIncrement: () => state.incrementItem(p.id),
                            onDecrement: () => state.decrementItem(p.id),
                          ),
                        ],
                      ),
                    );
                  }),

                  const SizedBox(height: 12),

                  // Delivery Address Card
                  Container(
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(
                      color: isDark ? GBColors.cardDark : Colors.white,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(
                        color: isDark ? GBColors.borderDark : GBColors.borderLight,
                      ),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Row(
                              children: [
                                const Icon(Icons.location_on_outlined, color: GBColors.primary, size: 20),
                                const SizedBox(width: 6),
                                Text(
                                  loc.tr('delivery_address'),
                                  style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 14),
                                ),
                              ],
                            ),
                            InkWell(
                              onTap: () {
                                Navigator.of(context).push(
                                  MaterialPageRoute(builder: (_) => const MapPickerScreen()),
                                );
                              },
                              child: Text(
                                loc.tr('change_address'),
                                style: const TextStyle(
                                  color: GBColors.primary,
                                  fontWeight: FontWeight.w700,
                                  fontSize: 13,
                                ),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),
                        Text(
                          '${state.selectedAddress.village}, ${state.selectedAddress.landmark != null ? "${loc.isHindi ? 'निकट ' : 'Near '}${state.selectedAddress.landmark!}, " : ""}${state.selectedAddress.block}, ${state.selectedAddress.district}',
                          style: TextStyle(
                            fontSize: 13,
                            color: isDark ? GBColors.textSecondaryDark : GBColors.textSecondaryLight,
                          ),
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(height: 16),

                  // Bill Breakdown
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: isDark ? GBColors.cardDark : Colors.white,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(
                        color: isDark ? GBColors.borderDark : GBColors.borderLight,
                      ),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          loc.tr('bill_details'),
                          style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 15),
                        ),
                        const SizedBox(height: 12),
                        _buildBillRow(loc.tr('subtotal'), '₹${state.cartSubtotal.toStringAsFixed(0)}'),
                        const SizedBox(height: 8),
                        _buildBillRow(loc.tr('delivery_fee'), '₹${state.cartDeliveryFee.toStringAsFixed(0)}'),
                        const SizedBox(height: 8),
                        _buildBillRow(
                          loc.isHindi ? 'प्लेटफ़ॉर्म शुल्क' : 'Platform Fee',
                          '₹${state.cartPlatformFee.toStringAsFixed(0)}', // Strict ₹3.00
                        ),
                        const Divider(height: 24),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              loc.tr('total_to_pay'),
                              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w800),
                            ),
                            Text(
                              '₹${state.cartTotal.toStringAsFixed(0)}',
                              style: const TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.w900,
                                color: GBColors.primary,
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 20),
                ],
              ),
            ),

            // Checkout Button Bottom Bar
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: isDark ? GBColors.surfaceDark : Colors.white,
                border: Border(
                  top: BorderSide(
                    color: isDark ? GBColors.borderDark : GBColors.borderLight,
                  ),
                ),
              ),
              child: Row(
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        '₹${state.cartTotal.toStringAsFixed(0)}',
                        style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w900),
                      ),
                      Text(
                        loc.isHindi ? 'कुल राशि' : 'Total Bill',
                        style: TextStyle(
                          fontSize: 11,
                          color: isDark ? GBColors.textMutedDark : GBColors.textMutedLight,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(width: 20),
                  Expanded(
                    child: GBPrimaryButton(
                      label: loc.tr('proceed_to_checkout'),
                      onPressed: () {
                        Navigator.of(context).push(
                          MaterialPageRoute(builder: (_) => const CheckoutScreen()),
                        );
                      },
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildBillRow(String label, String value) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label, style: const TextStyle(fontSize: 13)),
        Text(value, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600)),
      ],
    );
  }
}
