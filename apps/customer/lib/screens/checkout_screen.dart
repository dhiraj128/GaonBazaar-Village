import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import 'package:localization/localization.dart';
import '../state/app_state.dart';
import 'order_tracking_screen.dart';

class CheckoutScreen extends StatefulWidget {
  const CheckoutScreen({super.key});

  @override
  State<CheckoutScreen> createState() => _CheckoutScreenState();
}

class _CheckoutScreenState extends State<CheckoutScreen> {
  String _selectedPaymentMethod = 'COD'; // COD or ONLINE
  bool _isSubmitting = false;
  String? _errorMessage;

  Future<void> _handlePlaceOrder() async {
    if (_isSubmitting) return; // Prevent duplicate clicks

    setState(() {
      _isSubmitting = true;
      _errorMessage = null;
    });

    final state = AppStateProvider.of(context);
    final loc = GBLocalizations.of(context);
    final itemsPayload = state.cartItems
        .map((i) => {'product_id': i.product.id, 'quantity': i.quantity})
        .toList();

    final response = await state.apiClient.createOrder(
      storeId: state.currentCartStoreId ?? 'str_01',
      deliveryAddressId: state.selectedAddress.id,
      paymentMethod: _selectedPaymentMethod,
      items: itemsPayload,
      customerNotes: 'Village delivery order',
    );

    setState(() => _isSubmitting = false);

    if (response.isSuccess && response.data != null && mounted) {
      final order = response.data!;
      state.addOrder(order);
      state.clearCart();

      // Show success bottom sheet then navigate to Live Order Tracking
      showModalBottomSheet(
        context: context,
        isDismissible: false,
        enableDrag: false,
        shape: const RoundedRectangleBorder(
          borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
        ),
        builder: (ctx) => Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                padding: const EdgeInsets.all(16),
                decoration: const BoxDecoration(
                  color: GBColors.primary,
                  shape: BoxShape.circle,
                ),
                child: const Icon(Icons.check, size: 40, color: Colors.white),
              ),
              const SizedBox(height: 16),
              Text(
                loc.tr('order_success'),
                textAlign: TextAlign.center,
                style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w900),
              ),
              const SizedBox(height: 6),
              Text(
                loc.isHindi
                    ? 'आपका ऑर्डर दर्ज कर लिया गया है (30-60 मिनट में डिलीवरी)'
                    : 'Your order has been placed (30-60 min delivery target)',
                textAlign: TextAlign.center,
                style: const TextStyle(fontSize: 13, color: Colors.grey),
              ),
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: GBColors.primary.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Text(
                  loc.isHindi
                      ? 'डिलीवरी पिन: ${order.deliveryOtp}'
                      : 'Delivery PIN: ${order.deliveryOtp}',
                  style: const TextStyle(
                    fontWeight: FontWeight.w800,
                    fontSize: 16,
                    color: GBColors.primary,
                  ),
                ),
              ),
              const SizedBox(height: 24),
              GBPrimaryButton(
                label: loc.isHindi ? 'लाइव ट्रैकिंग देखें' : 'Track Live Order',
                onPressed: () {
                  Navigator.of(ctx).pop();
                  Navigator.of(context).pushReplacement(
                    MaterialPageRoute(
                      builder: (_) => OrderTrackingScreen(order: order),
                    ),
                  );
                },
              ),
            ],
          ),
        ),
      );
    } else if (mounted) {
      setState(() {
        _errorMessage = response.errorMessage ?? loc.tr('order_failed');
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = AppStateProvider.of(context);
    final loc = GBLocalizations.of(context);
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      appBar: AppBar(
        title: Text(
          loc.isHindi ? 'चेकआउट' : 'Checkout',
          style: const TextStyle(fontWeight: FontWeight.w800),
        ),
      ),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // Delivery Address card
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: isDark ? GBColors.cardDark : Colors.white,
                borderRadius: BorderRadius.circular(14),
                border: Border.all(
                  color: isDark ? GBColors.borderDark : GBColors.borderLight,
                ),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.location_on, color: GBColors.primary, size: 20),
                      const SizedBox(width: 8),
                      Text(
                        loc.tr('delivery_address'),
                        style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 14),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text(
                    '${state.selectedAddress.recipientName} • +91 ${state.selectedAddress.phone}',
                    style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    '${state.selectedAddress.village}, ${state.selectedAddress.landmark != null ? (loc.isHindi ? "निकट " : "Near ") + state.selectedAddress.landmark! + ", " : ""}${state.selectedAddress.block}, ${state.selectedAddress.district}',
                    style: TextStyle(
                      fontSize: 12,
                      color: isDark ? GBColors.textSecondaryDark : GBColors.textSecondaryLight,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Payment Options
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: isDark ? GBColors.cardDark : Colors.white,
                borderRadius: BorderRadius.circular(14),
                border: Border.all(
                  color: isDark ? GBColors.borderDark : GBColors.borderLight,
                ),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    loc.tr('select_payment'),
                    style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 14),
                  ),
                  const SizedBox(height: 12),
                  // COD
                  RadioListTile<String>(
                    value: 'COD',
                    groupValue: _selectedPaymentMethod,
                    activeColor: GBColors.primary,
                    contentPadding: EdgeInsets.zero,
                    title: Text(
                      loc.tr('pay_cod'),
                      style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 14),
                    ),
                    subtitle: Text(
                      loc.isHindi ? 'सामान मिलने पर नकद दें' : 'Pay cash upon delivery handoff',
                      style: const TextStyle(fontSize: 12),
                    ),
                    onChanged: (val) {
                      setState(() => _selectedPaymentMethod = val!);
                    },
                  ),
                  const Divider(height: 1),
                  // Online UPI
                  RadioListTile<String>(
                    value: 'ONLINE',
                    groupValue: _selectedPaymentMethod,
                    activeColor: GBColors.primary,
                    contentPadding: EdgeInsets.zero,
                    title: Text(
                      loc.tr('pay_online'),
                      style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 14),
                    ),
                    subtitle: const Text('PhonePe, Google Pay, Paytm, BHIM', style: TextStyle(fontSize: 12)),
                    onChanged: (val) {
                      setState(() => _selectedPaymentMethod = val!);
                    },
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Order items summary
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: isDark ? GBColors.cardDark : Colors.white,
                borderRadius: BorderRadius.circular(14),
                border: Border.all(
                  color: isDark ? GBColors.borderDark : GBColors.borderLight,
                ),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    loc.isHindi
                        ? 'सामान सूची (${state.cartCount} सामग्री)'
                        : 'Item Summary (${state.cartCount} items)',
                    style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 14),
                  ),
                  const SizedBox(height: 10),
                  ...state.cartItems.map((item) => Padding(
                        padding: const EdgeInsets.symmetric(vertical: 4),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              '${item.product.getLocalizedName(loc.isHindi)} x ${item.quantity}',
                              style: const TextStyle(fontSize: 13),
                            ),
                            Text(
                              '₹${item.totalPrice.toStringAsFixed(0)}',
                              style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13),
                            ),
                          ],
                        ),
                      )),
                  const Divider(height: 20),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(loc.tr('subtotal'), style: const TextStyle(fontSize: 13)),
                      Text('₹${state.cartSubtotal.toStringAsFixed(0)}', style: const TextStyle(fontSize: 13)),
                    ],
                  ),
                  const SizedBox(height: 6),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(loc.tr('delivery_fee'), style: const TextStyle(fontSize: 13)),
                      Text('₹${state.cartDeliveryFee.toStringAsFixed(0)}', style: const TextStyle(fontSize: 13)),
                    ],
                  ),
                  const SizedBox(height: 6),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(loc.isHindi ? 'प्लेटफ़ॉर्म शुल्क' : 'Platform Fee', style: const TextStyle(fontSize: 13)),
                      Text('₹${state.cartPlatformFee.toStringAsFixed(0)}', style: const TextStyle(fontSize: 13)), // Strict ₹3
                    ],
                  ),
                  const Divider(height: 20),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        loc.tr('total_to_pay'),
                        style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w900),
                      ),
                      Text(
                        '₹${state.cartTotal.toStringAsFixed(0)}',
                        style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w900, color: GBColors.primary),
                      ),
                    ],
                  ),
                ],
              ),
            ),

            if (_errorMessage != null) ...[
              const SizedBox(height: 12),
              Text(
                _errorMessage!,
                style: const TextStyle(color: GBColors.error, fontSize: 13),
              ),
            ],

            const SizedBox(height: 24),

            GBPrimaryButton(
              label: loc.tr('place_order'),
              isLoading: _isSubmitting,
              onPressed: _handlePlaceOrder,
            ),
            const SizedBox(height: 20),
          ],
        ),
      ),
    );
  }
}
