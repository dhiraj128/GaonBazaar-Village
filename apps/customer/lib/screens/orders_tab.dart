import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import 'package:localization/localization.dart';
import 'package:shared_models/shared_models.dart';
import '../state/app_state.dart';
import 'order_tracking_screen.dart';

class OrdersTab extends StatefulWidget {
  final Function(int) onTabChange;

  const OrdersTab({super.key, required this.onTabChange});

  @override
  State<OrdersTab> createState() => _OrdersTabState();
}

class _OrdersTabState extends State<OrdersTab> {
  bool _isLoading = true;
  List<GBOrder> _orders = [];

  @override
  void initState() {
    super.initState();
    _fetchOrders();
  }

  Future<void> _fetchOrders() async {
    setState(() => _isLoading = true);
    final state = AppStateProvider.of(context);
    final response = await state.apiClient.createOrder(
      storeId: 'dummy',
      deliveryAddressId: 'dummy',
      paymentMethod: 'dummy',
      items: [],
    ); // Just to verify client connectivity, or fetch directly

    // Load from AppState
    _orders = state.myOrders;
    if (_orders.isEmpty) {
      // Baseline sample order for Minapur customer
      _orders = [
        GBOrder(
          id: 'ord_sample_01',
          customerId: 'usr_c1',
          storeId: 'str_01',
          storeName: 'माँ शारदा किराना स्टोर (Chaturshi)',
          deliveryAddress: 'Chaturshi, Near Gram Panchayat Bhavan, Minapur',
          status: 'OUT_FOR_DELIVERY',
          subtotal: 180.0,
          deliveryFee: 15.0,
          platformFee: 3.0,
          totalAmount: 198.0,
          paymentMethod: 'COD',
          paymentStatus: 'PENDING',
          deliveryOtp: '4821',
          placedAt: DateTime.now().subtract(const Duration(minutes: 25)),
          cancelUntil: DateTime.now().subtract(const Duration(minutes: 22)),
          canCancel: false,
          cancelSecondsRemaining: 0,
          items: [
            GBOrderItem(
              id: 'oi_1',
              productId: 'prd_01',
              nameEn: 'Chakki Fresh Atta',
              nameHi: 'ताज़ा चक्की आटा',
              unit: '1 kg',
              unitPrice: 38.0,
              quantity: 2,
              totalPrice: 76.0,
            ),
            GBOrderItem(
              id: 'oi_2',
              productId: 'prd_03',
              nameEn: 'Fresh Cow Milk',
              nameHi: 'ताज़ा गाय का दूध',
              unit: '1 L',
              unitPrice: 56.0,
              quantity: 1,
              totalPrice: 56.0,
            ),
          ],
          timeline: [
            GBOrderTimelineItem(
              status: 'PLACED',
              title: 'ऑर्डर दर्ज हुआ',
              timestamp: DateTime.now().subtract(const Duration(minutes: 25)),
            ),
            GBOrderTimelineItem(
              status: 'PACKED',
              title: 'सामान पैक हुआ',
              timestamp: DateTime.now().subtract(const Duration(minutes: 18)),
            ),
            GBOrderTimelineItem(
              status: 'OUT_FOR_DELIVERY',
              title: 'डिलीवरी के लिए निकल चुके हैं',
              timestamp: DateTime.now().subtract(const Duration(minutes: 8)),
            ),
          ],
        )
      ];
    }

    if (mounted) {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final loc = GBLocalizations.of(context);
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      appBar: AppBar(
        title: Text(loc.tr('tab_orders'), style: const TextStyle(fontWeight: FontWeight.w800)),
      ),
      body: _isLoading
          ? const Center(child: GBLoadingState())
          : _orders.isEmpty
              ? GBEmptyState(
                  title: loc.isHindi ? 'कोई ऑर्डर नहीं मिला' : 'No Orders Found',
                  message: loc.isHindi
                      ? 'आपने अभी तक कोई सामान ऑर्डर नहीं किया है।'
                      : 'You have not placed any orders yet.',
                  actionLabel: loc.isHindi ? 'खरीदारी शुरू करें' : 'Start Shopping',
                  onAction: () => widget.onTabChange(0),
                )
              : RefreshIndicator(
                  onRefresh: _fetchOrders,
                  color: GBColors.primary,
                  child: ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: _orders.length,
                    itemBuilder: (context, index) {
                      final order = _orders[index];
                      return Container(
                        margin: const EdgeInsets.only(bottom: 14),
                        decoration: BoxDecoration(
                          color: isDark ? GBColors.cardDark : Colors.white,
                          borderRadius: BorderRadius.circular(14),
                          border: Border.all(
                            color: isDark ? GBColors.borderDark : GBColors.borderLight,
                          ),
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black.withOpacity(0.04),
                              blurRadius: 4,
                              offset: const Offset(0, 1),
                            ),
                          ],
                        ),
                        child: InkWell(
                          onTap: () {
                            Navigator.of(context).push(
                              MaterialPageRoute(
                                builder: (_) => OrderTrackingScreen(order: order),
                              ),
                            );
                          },
                          borderRadius: BorderRadius.circular(14),
                          child: Padding(
                            padding: const EdgeInsets.all(14),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Row(
                                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                  children: [
                                    Text(
                                      order.storeName,
                                      style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 15),
                                    ),
                                    GBOrderStatusBadge(status: order.status),
                                  ],
                                ),
                                const SizedBox(height: 6),
                                Text(
                                  '₹${order.totalAmount.toStringAsFixed(0)} • ${order.paymentMethod}',
                                  style: const TextStyle(
                                    fontWeight: FontWeight.w700,
                                    fontSize: 14,
                                    color: GBColors.primary,
                                  ),
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  order.deliveryAddress,
                                  maxLines: 1,
                                  overflow: TextOverflow.ellipsis,
                                  style: TextStyle(
                                    fontSize: 12,
                                    color: isDark ? GBColors.textMutedDark : GBColors.textMutedLight,
                                  ),
                                ),
                                const Divider(height: 20),
                                Row(
                                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                  children: [
                                    Row(
                                      children: [
                                        const Icon(Icons.pin, size: 16, color: GBColors.primary),
                                        const SizedBox(width: 4),
                                        Text(
                                          'OTP: ${order.deliveryOtp}',
                                          style: const TextStyle(
                                            fontWeight: FontWeight.w800,
                                            fontSize: 13,
                                            color: GBColors.primary,
                                          ),
                                        ),
                                      ],
                                    ),
                                    const Row(
                                      children: [
                                        Text(
                                          'ट्रैक करें (Track)',
                                          style: TextStyle(fontWeight: FontWeight.w700, fontSize: 13),
                                        ),
                                        Icon(Icons.chevron_right, size: 18),
                                      ],
                                    ),
                                  ],
                                ),
                              ],
                            ),
                          ),
                        ),
                      );
                    },
                  ),
                ),
    );
  }
}
