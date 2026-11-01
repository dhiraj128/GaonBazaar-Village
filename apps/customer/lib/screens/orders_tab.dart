import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import 'package:localization/localization.dart';
import '../state/app_state.dart';
import 'order_tracking_screen.dart';

class OrdersTab extends StatefulWidget {
  final Function(int) onTabChange;

  const OrdersTab({super.key, required this.onTabChange});

  @override
  State<OrdersTab> createState() => _OrdersTabState();
}

class _OrdersTabState extends State<OrdersTab> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      AppStateProvider.of(context).fetchOrders();
    });
  }

  @override
  Widget build(BuildContext context) {
    final state = AppStateProvider.of(context);
    final loc = GBLocalizations.of(context);
    final isDark = Theme.of(context).brightness == Brightness.dark;

    final orders = state.myOrders;

    return Scaffold(
      appBar: AppBar(
        title: Text(loc.tr('tab_orders'), style: const TextStyle(fontWeight: FontWeight.w800)),
      ),
      body: state.isLoadingOrders
          ? const Center(child: GBLoadingState())
          : orders.isEmpty
              ? GBEmptyState(
                  title: loc.tr('no_orders'),
                  message: loc.tr('no_orders_msg'),
                  actionLabel: loc.isHindi ? 'खरीदारी शुरू करें' : 'Start Shopping',
                  onAction: () => widget.onTabChange(0),
                )
              : RefreshIndicator(
                  onRefresh: state.fetchOrders,
                  color: GBColors.primary,
                  child: ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: orders.length,
                    itemBuilder: (context, index) {
                      final order = orders[index];
                      final shortId = order.id.length > 8 ? order.id.substring(0, 8) : order.id;

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
                                  '₹${order.totalAmount.toStringAsFixed(2)} • ${order.paymentMethod}',
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
                                          loc.tr('order_tracking'),
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
                ),
    );
  }
}
