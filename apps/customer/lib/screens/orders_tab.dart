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

class _OrdersTabState extends State<OrdersTab> with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    WidgetsBinding.instance.addPostFrameCallback((_) {
      AppStateProvider.of(context).fetchOrders();
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  bool _isActiveOrder(String status) {
    return status != 'DELIVERED' && status != 'CANCELLED';
  }

  @override
  Widget build(BuildContext context) {
    final state = AppStateProvider.of(context);
    final loc = GBLocalizations.of(context);
    final isDark = Theme.of(context).brightness == Brightness.dark;

    final allOrders = state.myOrders;
    final activeOrders = allOrders.where((o) => _isActiveOrder(o.status)).toList();
    final pastOrders = allOrders.where((o) => !_isActiveOrder(o.status)).toList();

    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          tooltip: loc.isHindi ? 'होम पर वापस जाएं' : 'Back to Home',
          onPressed: () => widget.onTabChange(0),
        ),
        title: Text(loc.tr('tab_orders'), style: const TextStyle(fontWeight: FontWeight.w800)),
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: GBColors.primary,
          labelColor: GBColors.primary,
          unselectedLabelColor: isDark ? Colors.grey.shade400 : Colors.grey.shade700,
          labelStyle: const TextStyle(fontWeight: FontWeight.w800, fontSize: 13),
          tabs: [
            Tab(text: '${loc.isHindi ? "सक्रिय ऑर्डर" : "Active Orders"} (${activeOrders.length})'),
            Tab(text: '${loc.isHindi ? "पुराने ऑर्डर" : "Past Orders"} (${pastOrders.length})'),
          ],
        ),
      ),
      body: state.isLoadingOrders
          ? const Center(child: GBLoadingState())
          : TabBarView(
              controller: _tabController,
              children: [
                _buildOrderList(activeOrders, isActive: true, loc: loc, isDark: isDark, state: state),
                _buildOrderList(pastOrders, isActive: false, loc: loc, isDark: isDark, state: state),
              ],
            ),
    );
  }

  Widget _buildOrderList(
    List<GBOrder> orders, {
    required bool isActive,
    required GBLocalizations loc,
    required bool isDark,
    required CustomerAppState state,
  }) {
    if (orders.isEmpty) {
      return GBEmptyState(
        title: isActive
            ? (loc.isHindi ? 'कोई सक्रिय ऑर्डर नहीं है' : 'No Active Orders')
            : (loc.isHindi ? 'कोई पुराना ऑर्डर नहीं है' : 'No Past Orders'),
        message: isActive
            ? (loc.isHindi ? 'आपके द्वारा दिए गए नए ऑर्डर यहाँ दिखाई देंगे।' : 'New orders will appear here while in progress.')
            : (loc.isHindi ? 'डिलीवर हुए और पहले के सभी ऑर्डर यहाँ सहेजे जाते हैं।' : 'Completed and past delivery records appear here.'),
        actionLabel: loc.isHindi ? 'खरीदारी शुरू करें' : 'Start Shopping',
        onAction: () => widget.onTabChange(0),
      );
    }

    return RefreshIndicator(
      onRefresh: state.fetchOrders,
      color: GBColors.primary,
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: orders.length,
        itemBuilder: (context, index) {
          final order = orders[index];
          final shortId = order.id.length > 8 ? order.id.substring(0, 8) : order.id;

          final itemsSummary = order.items.isNotEmpty
              ? order.items.map((i) => '${i.quantity}x ${loc.isHindi ? i.nameHi : i.nameEn}').join(', ')
              : '${order.items.length} items';

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
                  color: Colors.black.withAlpha(10),
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
                ).then((_) => state.fetchOrders());
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
                        Expanded(
                          child: Text(
                            order.storeName,
                            style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 15),
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                        const SizedBox(width: 8),
                        GBOrderStatusBadge(status: order.status),
                      ],
                    ),
                    const SizedBox(height: 6),
                    Text(
                      '₹${order.totalAmount.toStringAsFixed(0)} • ${order.paymentMethod == "COD" ? (loc.isHindi ? "कैश ऑन डिलीवरी" : "Cash on Delivery") : "Online"}',
                      style: const TextStyle(
                        fontWeight: FontWeight.w800,
                        fontSize: 14,
                        color: GBColors.primary,
                      ),
                    ),
                    if (itemsSummary.isNotEmpty) ...[
                      const SizedBox(height: 4),
                      Text(
                        itemsSummary,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: TextStyle(
                          fontSize: 12,
                          color: isDark ? Colors.grey.shade300 : Colors.grey.shade800,
                        ),
                      ),
                    ],
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
                    const Divider(height: 18),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          '${loc.tr('order_id')}$shortId',
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w600,
                            color: isDark ? GBColors.textMutedDark : GBColors.textMutedLight,
                          ),
                        ),
                        Row(
                          children: [
                            Text(
                              isActive ? loc.tr('order_tracking') : (loc.isHindi ? 'विवरण देखें' : 'View Details'),
                              style: const TextStyle(
                                fontSize: 12,
                                fontWeight: FontWeight.w700,
                                color: GBColors.primary,
                              ),
                            ),
                            const SizedBox(width: 4),
                            const Icon(
                              Icons.arrow_forward_ios_rounded,
                              size: 12,
                              color: GBColors.primary,
                            ),
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
    );
  }
}
