import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import 'package:localization/localization.dart';
import 'package:shared_models/shared_models.dart';
import 'package:url_launcher/url_launcher.dart';
import '../state/vendor_state.dart';
import 'vendor_auth_screen.dart';
import 'product_library_screen.dart';
import 'vendor_settlements_screen.dart';
import 'vendor_picking_packing_screen.dart';
import 'vendor_store_settings_screen.dart';

class VendorDashboardScreen extends StatefulWidget {
  const VendorDashboardScreen({super.key});

  @override
  State<VendorDashboardScreen> createState() => _VendorDashboardScreenState();
}

class _VendorDashboardScreenState extends State<VendorDashboardScreen> {
  int _navIndex = 0;
  String _orderFilter = 'ALL';
  bool _isActing = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final state = VendorStateProvider.of(context);
      state.fetchStoreProfile();
      state.fetchOrders();
      state.fetchFinances();
      state.fetchNotifications();
    });
  }

  Future<void> _handleAction(VendorAppState state, String orderId, String action) async {
    setState(() => _isActing = true);
    final success = await state.handleOrderAction(orderId, action);
    if (!mounted) return;
    setState(() => _isActing = false);

    final loc = GBLocalizations.of(context);
    if (success) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(loc.isHindi ? 'ऑर्डर की स्थिति सफलतापूर्वक अपडेट हो गई' : 'Order status updated successfully'),
          backgroundColor: GBColors.success,
        ),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(loc.isHindi ? 'कार्रवाई विफल रही' : 'Action failed'),
          backgroundColor: GBColors.error,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = VendorStateProvider.of(context);
    final loc = GBLocalizations.of(context);
    final isHi = loc.isHindi;
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              state.myStore?.shopName ?? (isHi ? 'गाँव बाज़ार दुकानदार साथी' : 'GaonBazaar Shopkeeper'),
              style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16),
            ),
            Text(
              '${state.myStore?.village ?? ""}${state.myStore?.block != null ? ", " + state.myStore!.block : ""}',
              style: TextStyle(fontSize: 11, color: isDark ? Colors.white60 : Colors.black54),
            ),
          ],
        ),
        actions: [
          // Notification Bell
          GBNotificationBell(
            unreadCount: state.unreadNotificationCount,
            onTap: () {
              showGBNotificationSheet(
                context,
                isHindi: isHi,
                notifications: state.notifications.map((n) {
                  final diff = DateTime.now().difference(n.timestamp);
                  final timeStr = diff.inMinutes < 60
                      ? (isHi ? '${diff.inMinutes} मिनट पहले' : '${diff.inMinutes}m ago')
                      : (isHi ? '${diff.inHours} घंटे पहले' : '${diff.inHours}h ago');
                  return GBNotificationItemData(
                    id: n.id,
                    title: n.title,
                    body: n.body,
                    time: timeStr,
                    isRead: n.isRead,
                    type: n.type,
                  );
                }).toList(),
                onMarkAllRead: () => state.markAllNotificationsRead(),
              );
            },
          ),
          // Online / Offline Switch
          Padding(
            padding: const EdgeInsets.only(right: 8),
            child: Row(
              children: [
                Text(
                  state.isStoreOnline
                      ? (isHi ? 'दुकान खुली' : 'Open')
                      : (isHi ? 'दुकान बंद' : 'Closed'),
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w700,
                    color: state.isStoreOnline ? GBColors.success : GBColors.error,
                  ),
                ),
                Switch(
                  value: state.isStoreOnline,
                  activeColor: GBColors.success,
                  onChanged: (v) async {
                    final err = await state.toggleStoreOnline();
                    if (err != null && context.mounted) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(content: Text(err), backgroundColor: GBColors.error),
                      );
                    }
                  },
                ),
              ],
            ),
          ),
        ],
      ),
      body: IndexedStack(
        index: _navIndex,
        children: [
          _buildHomeTab(state),
          _buildOrdersTab(state),
          const ProductLibraryScreen(isTab: true),
          const VendorSettlementsScreen(isTab: true),
          _buildAccountTab(state),
        ],
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _navIndex,
        onTap: (idx) => setState(() => _navIndex = idx),
        selectedItemColor: GBColors.primary,
        unselectedItemColor: isDark ? Colors.white60 : Colors.grey,
        type: BottomNavigationBarType.fixed,
        items: [
          BottomNavigationBarItem(
            icon: const Icon(Icons.home_outlined),
            activeIcon: const Icon(Icons.home),
            label: isHi ? 'होम' : 'Home',
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.receipt_long_outlined),
            activeIcon: const Icon(Icons.receipt_long),
            label: isHi ? 'ऑर्डर' : 'Orders',
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.inventory_2_outlined),
            activeIcon: const Icon(Icons.inventory_2),
            label: isHi ? 'कैटलॉग' : 'Catalog',
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.account_balance_wallet_outlined),
            activeIcon: const Icon(Icons.account_balance_wallet),
            label: isHi ? 'कमाई' : 'Earnings',
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.person_outline),
            activeIcon: const Icon(Icons.person),
            label: isHi ? 'खाता' : 'Account',
          ),
        ],
      ),
    );
  }

  // =========================================================================
  // TAB 0: HOME DASHBOARD (Blinkit-Grade Operations Center)
  // =========================================================================
  Widget _buildHomeTab(VendorAppState state) {
    final loc = GBLocalizations.of(context);
    final isHi = loc.isHindi;
    final isDark = Theme.of(context).brightness == Brightness.dark;

    final newOrders = state.storeOrders.where((o) => o.status == 'PLACED').toList();
    final packingOrders = state.storeOrders.where((o) => o.status == 'ACCEPTED').toList();
    final readyOrders = state.storeOrders.where((o) => o.status == 'PACKED' || o.status == 'RUNNER_ASSIGNED').toList();
    final deliveredOrders = state.storeOrders.where((o) => o.status == 'DELIVERED').toList();

    final todaySales = (state.finances?['today_sales'] as num?)?.toDouble() ??
        deliveredOrders.fold<double>(0.0, (double sum, o) => sum + o.subtotal);

    final lowStockItems = state.myProducts.where((p) => p.stockQuantity < 5 || !p.inStock).toList();

    return RefreshIndicator(
      onRefresh: () async {
        await state.fetchStoreProfile();
        await state.fetchOrders();
        await state.fetchFinances();
      },
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Operational Summary Metrics
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: isDark ? const Color(0xFF1E293B) : Colors.white,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: isDark ? Colors.white12 : Colors.black12),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      isHi ? 'आज का व्यापार सारांश' : 'Today\'s Business Summary',
                      style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 14),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(
                        color: GBColors.primary.withValues(alpha: 0.1),
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: Text(
                        isHi ? '0% कमीशन' : '0% Commission',
                        style: const TextStyle(
                          color: GBColors.primary,
                          fontWeight: FontWeight.w800,
                          fontSize: 11,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    _buildStatPill(
                      title: isHi ? 'नए ऑर्डर' : 'New',
                      value: '${newOrders.length}',
                      color: Colors.amber.shade800,
                      isDark: isDark,
                      onTap: () => setState(() {
                        _navIndex = 1;
                        _orderFilter = 'PLACED';
                      }),
                    ),
                    const SizedBox(width: 8),
                    _buildStatPill(
                      title: isHi ? 'पैकिंग में' : 'Packing',
                      value: '${packingOrders.length}',
                      color: Colors.blue.shade700,
                      isDark: isDark,
                      onTap: () => setState(() {
                        _navIndex = 1;
                        _orderFilter = 'ACCEPTED';
                      }),
                    ),
                    const SizedBox(width: 8),
                    _buildStatPill(
                      title: isHi ? 'तैयार' : 'Ready',
                      value: '${readyOrders.length}',
                      color: Colors.purple.shade700,
                      isDark: isDark,
                      onTap: () => setState(() {
                        _navIndex = 1;
                        _orderFilter = 'PACKED';
                      }),
                    ),
                    const SizedBox(width: 8),
                    _buildStatPill(
                      title: isHi ? 'पूर्ण' : 'Delivered',
                      value: '${deliveredOrders.length}',
                      color: GBColors.success,
                      isDark: isDark,
                      onTap: () => setState(() {
                        _navIndex = 1;
                        _orderFilter = 'DELIVERED';
                      }),
                    ),
                  ],
                ),
                const Divider(height: 20),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      isHi ? 'आज की कुल वास्तविक बिक्री:' : 'Today\'s Actual Sales:',
                      style: const TextStyle(fontSize: 13, color: Colors.grey, fontWeight: FontWeight.w600),
                    ),
                    Text(
                      '₹${todaySales.toStringAsFixed(0)}',
                      style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 18, color: GBColors.primary),
                    ),
                  ],
                ),
              ],
            ),
          ),

          const SizedBox(height: 18),

          // High-Priority: New Orders Requiring Action
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                isHi ? 'नए ऑर्डर (तत्काल कार्रवाई आवश्यक)' : 'New Orders (Action Required)',
                style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 15),
              ),
              if (newOrders.isNotEmpty)
                TextButton(
                  onPressed: () => setState(() {
                    _navIndex = 1;
                    _orderFilter = 'PLACED';
                  }),
                  child: Text(isHi ? 'सभी देखें' : 'View All'),
                ),
            ],
          ),
          const SizedBox(height: 8),

          if (newOrders.isEmpty && packingOrders.isEmpty)
            Container(
              padding: const EdgeInsets.symmetric(vertical: 24, horizontal: 16),
              alignment: Alignment.center,
              decoration: BoxDecoration(
                color: isDark ? const Color(0xFF1E293B) : Colors.white,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: isDark ? Colors.white12 : Colors.black12),
              ),
              child: Column(
                children: [
                  Icon(Icons.check_circle_outline, color: GBColors.primary.withValues(alpha: 0.6), size: 40),
                  const SizedBox(height: 8),
                  Text(
                    isHi ? 'सभी नए ऑर्डर प्रोसेस हो चुके हैं!' : 'All new orders processed!',
                    style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 14),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    isHi ? 'दुकान खुली है — नए ग्रामीण ऑर्डर की प्रतीक्षा की जा रही है।' : 'Store is open — waiting for new customer orders.',
                    style: const TextStyle(fontSize: 12, color: Colors.grey),
                  ),
                ],
              ),
            )
          else ...[
            ...newOrders.take(3).map((o) => _buildOrderActionCard(o, state, isHi, isDark)),
            ...packingOrders.take(2).map((o) => _buildOrderActionCard(o, state, isHi, isDark)),
          ],

          const SizedBox(height: 20),

          // Low Stock Alerts Card
          if (lowStockItems.isNotEmpty) ...[
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: Colors.red.withValues(alpha: 0.08),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.red.withValues(alpha: 0.25)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.warning_amber_rounded, color: Colors.red, size: 20),
                      const SizedBox(width: 8),
                      Text(
                        isHi ? 'कम स्टॉक चेतावनी (${lowStockItems.length} उत्पाद)' : 'Low Stock Alerts (${lowStockItems.length} items)',
                        style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 14, color: Colors.red),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  ...lowStockItems.take(2).map((p) => Padding(
                        padding: const EdgeInsets.symmetric(vertical: 4),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(isHi ? p.nameHi : p.nameEn, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600)),
                            Text(
                              p.inStock ? '${p.stockQuantity} बची' : (isHi ? 'समाप्त' : 'Out of Stock'),
                              style: TextStyle(
                                fontSize: 12,
                                color: p.inStock ? Colors.orange.shade800 : Colors.red,
                                fontWeight: FontWeight.w700,
                              ),
                            ),
                          ],
                        ),
                      )),
                  const SizedBox(height: 8),
                  InkWell(
                    onTap: () => setState(() => _navIndex = 2),
                    child: Text(
                      isHi ? 'इन्वेंट्री में स्टॉक अपडेट करें →' : 'Manage Stock in Catalog →',
                      style: const TextStyle(color: GBColors.primary, fontWeight: FontWeight.w800, fontSize: 12),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),
          ],

          // Quick Operations Shortcuts
          Text(
            isHi ? 'त्वरित संचालन' : 'Quick Operations',
            style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 15),
          ),
          const SizedBox(height: 10),
          Row(
            children: [
              Expanded(
                child: _buildShortcutButton(
                  icon: Icons.add_circle_outline,
                  label: isHi ? 'उत्पाद जोड़ें' : 'Add Item',
                  onTap: () => setState(() => _navIndex = 2),
                  isDark: isDark,
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: _buildShortcutButton(
                  icon: Icons.inventory_2_outlined,
                  label: isHi ? 'स्टॉक जांचें' : 'Check Stock',
                  onTap: () => setState(() => _navIndex = 2),
                  isDark: isDark,
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: _buildShortcutButton(
                  icon: Icons.account_balance_wallet_outlined,
                  label: isHi ? 'कमाई देखें' : 'Earnings',
                  onTap: () => setState(() => _navIndex = 3),
                  isDark: isDark,
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),
        ],
      ),
    );
  }

  Widget _buildStatPill({
    required String title,
    required String value,
    required Color color,
    required bool isDark,
    required VoidCallback onTap,
  }) {
    return Expanded(
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(8),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 8),
          decoration: BoxDecoration(
            color: color.withValues(alpha: 0.1),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Column(
            children: [
              Text(
                value,
                style: TextStyle(fontWeight: FontWeight.w900, fontSize: 18, color: color),
              ),
              const SizedBox(height: 2),
              Text(
                title,
                style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: color),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildShortcutButton({
    required IconData icon,
    required String label,
    required VoidCallback onTap,
    required bool isDark,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(10),
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 12),
        decoration: BoxDecoration(
          color: isDark ? const Color(0xFF1E293B) : Colors.white,
          borderRadius: BorderRadius.circular(10),
          border: Border.all(color: isDark ? Colors.white12 : Colors.black12),
        ),
        child: Column(
          children: [
            Icon(icon, color: GBColors.primary, size: 24),
            const SizedBox(height: 6),
            Text(label, style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 12)),
          ],
        ),
      ),
    );
  }

  Widget _buildOrderActionCard(GBOrder order, VendorAppState state, bool isHi, bool isDark) {
    final diff = DateTime.now().difference(order.placedAt);
    final timeAgo = diff.inMinutes < 60
        ? (isHi ? '${diff.inMinutes} मिनट पहले' : '${diff.inMinutes}m ago')
        : (isHi ? '${diff.inHours} घंटे पहले' : '${diff.inHours}h ago');

    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: InkWell(
        onTap: () {
          Navigator.of(context).push(
            MaterialPageRoute(builder: (_) => VendorPickingPackingScreen(order: order)),
          );
        },
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('ऑर्डर #${order.id.toUpperCase()}', style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 14)),
                  Text(timeAgo, style: const TextStyle(fontSize: 11, color: Colors.grey)),
                ],
              ),
              const SizedBox(height: 6),
              Text(
                order.items.map((i) => '${i.quantity}x ${isHi ? i.nameHi : i.nameEn}').join(', '),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w500),
              ),
              const SizedBox(height: 8),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Row(
                    children: [
                      Text(
                        '₹${order.totalAmount.toStringAsFixed(0)}',
                        style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 15, color: GBColors.primary),
                      ),
                      const SizedBox(width: 8),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                        decoration: BoxDecoration(
                          color: order.paymentMethod == 'COD' ? Colors.orange.withValues(alpha: 0.15) : Colors.green.withValues(alpha: 0.15),
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: Text(
                          order.paymentMethod,
                          style: TextStyle(
                            fontSize: 10,
                            fontWeight: FontWeight.w800,
                            color: order.paymentMethod == 'COD' ? Colors.orange.shade900 : Colors.green.shade800,
                          ),
                        ),
                      ),
                    ],
                  ),
                  if (order.status == 'PLACED') ...[
                    Row(
                      children: [
                        OutlinedButton(
                          style: OutlinedButton.styleFrom(
                            foregroundColor: Colors.red,
                            side: const BorderSide(color: Colors.red),
                            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                            minimumSize: Size.zero,
                          ),
                          onPressed: _isActing ? null : () => _handleAction(state, order.id, 'REJECT'),
                          child: Text(isHi ? 'अस्वीकार' : 'Reject', style: const TextStyle(fontSize: 12)),
                        ),
                        const SizedBox(width: 8),
                        ElevatedButton(
                          style: ElevatedButton.styleFrom(
                            backgroundColor: GBColors.primary,
                            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
                            minimumSize: Size.zero,
                          ),
                          onPressed: _isActing ? null : () => _handleAction(state, order.id, 'ACCEPT'),
                          child: Text(isHi ? 'स्वीकार करें' : 'Accept', style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
                        ),
                      ],
                    ),
                  ] else if (order.status == 'ACCEPTED') ...[
                    ElevatedButton.icon(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.blue.shade700,
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                        minimumSize: Size.zero,
                      ),
                      icon: const Icon(Icons.checklist, size: 16),
                      label: Text(isHi ? 'पैकिंग शुरू करें' : 'Pack Items', style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
                      onPressed: () {
                        Navigator.of(context).push(
                          MaterialPageRoute(builder: (_) => VendorPickingPackingScreen(order: order)),
                        );
                      },
                    ),
                  ],
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  // =========================================================================
  // TAB 1: ORDERS (Full Operational Workflow Filter)
  // =========================================================================
  Widget _buildOrdersTab(VendorAppState state) {
    final loc = GBLocalizations.of(context);
    final isHi = loc.isHindi;

    final filterMap = {
      'ALL': isHi ? 'सभी' : 'All',
      'PLACED': isHi ? 'नया' : 'New',
      'ACCEPTED': isHi ? 'स्वीकृत' : 'Accepted',
      'PACKED': isHi ? 'पैक' : 'Packed',
      'OUT_FOR_DELIVERY': isHi ? 'रास्ते में' : 'On Way',
      'DELIVERED': isHi ? 'पूर्ण' : 'Completed',
      'CANCELLED': isHi ? 'रद्द' : 'Cancelled',
    };

    final filtered = state.storeOrders.where((o) {
      if (_orderFilter == 'ALL') return true;
      if (_orderFilter == 'PACKED') return o.status == 'PACKED' || o.status == 'RUNNER_ASSIGNED';
      if (_orderFilter == 'OUT_FOR_DELIVERY') return o.status == 'PICKED_UP' || o.status == 'OUT_FOR_DELIVERY';
      return o.status == _orderFilter;
    }).toList();

    return Column(
      children: [
        // Filter Chips Bar
        SizedBox(
          height: 50,
          child: ListView(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            children: filterMap.entries.map((e) {
              final isSel = _orderFilter == e.key;
              return Padding(
                padding: const EdgeInsets.only(right: 8),
                child: FilterChip(
                  label: Text(e.value),
                  selected: isSel,
                  selectedColor: GBColors.primary.withValues(alpha: 0.15),
                  checkmarkColor: GBColors.primary,
                  labelStyle: TextStyle(
                    color: isSel ? GBColors.primary : Colors.grey,
                    fontWeight: isSel ? FontWeight.w800 : FontWeight.w600,
                    fontSize: 12,
                  ),
                  onSelected: (_) => setState(() => _orderFilter = e.key),
                ),
              );
            }).toList(),
          ),
        ),
        // Orders List
        Expanded(
          child: RefreshIndicator(
            onRefresh: () async => await state.fetchOrders(),
            child: filtered.isEmpty
                ? Center(
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Icon(Icons.receipt_long_outlined, size: 48, color: Colors.grey),
                        const SizedBox(height: 12),
                        Text(
                          isHi ? 'इस श्रेणी में कोई ऑर्डर नहीं है' : 'No orders in this category',
                          style: const TextStyle(fontWeight: FontWeight.w700, color: Colors.grey),
                        ),
                      ],
                    ),
                  )
                : ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: filtered.length,
                    itemBuilder: (ctx, idx) => _buildOrderFullCard(filtered[idx], state, isHi),
                  ),
          ),
        ),
      ],
    );
  }

  Widget _buildOrderFullCard(GBOrder order, VendorAppState state, bool isHi) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: InkWell(
        onTap: () {
          Navigator.of(context).push(
            MaterialPageRoute(builder: (_) => VendorPickingPackingScreen(order: order)),
          );
        },
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('ऑर्डर #${order.id.toUpperCase()}', style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 14)),
                  _buildStatusBadge(order.status, isHi),
                ],
              ),
              const SizedBox(height: 8),
              Text(
                order.items.map((i) => '${i.quantity}x ${isHi ? i.nameHi : i.nameEn}').join(', '),
                style: const TextStyle(fontSize: 13),
              ),
              const SizedBox(height: 8),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    '₹${order.totalAmount.toStringAsFixed(0)} (${order.paymentMethod})',
                    style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 14, color: GBColors.primary),
                  ),
                  Text(
                    order.deliveryAddress,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(fontSize: 11, color: Colors.grey),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStatusBadge(String status, bool isHi) {
    Color bg = Colors.blue.withValues(alpha: 0.1);
    Color txt = Colors.blue;
    String label = status;

    switch (status) {
      case 'PLACED':
        bg = Colors.amber.withValues(alpha: 0.15);
        txt = Colors.amber.shade900;
        label = isHi ? 'नया' : 'New';
        break;
      case 'ACCEPTED':
        bg = Colors.blue.withValues(alpha: 0.15);
        txt = Colors.blue.shade800;
        label = isHi ? 'स्वीकृत' : 'Accepted';
        break;
      case 'PACKED':
        bg = Colors.purple.withValues(alpha: 0.15);
        txt = Colors.purple.shade800;
        label = isHi ? 'पैक' : 'Packed';
        break;
      case 'RUNNER_ASSIGNED':
        bg = Colors.orange.withValues(alpha: 0.15);
        txt = Colors.orange.shade900;
        label = isHi ? 'साथी आ रहा है' : 'Runner Assigned';
        break;
      case 'PICKED_UP':
      case 'OUT_FOR_DELIVERY':
        bg = Colors.teal.withValues(alpha: 0.15);
        txt = Colors.teal.shade800;
        label = isHi ? 'रास्ते में' : 'On Way';
        break;
      case 'DELIVERED':
        bg = Colors.green.withValues(alpha: 0.15);
        txt = Colors.green.shade800;
        label = isHi ? 'पूर्ण' : 'Delivered';
        break;
      case 'CANCELLED':
        bg = Colors.red.withValues(alpha: 0.15);
        txt = Colors.red.shade800;
        label = isHi ? 'रद्द' : 'Cancelled';
        break;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(color: bg, borderRadius: BorderRadius.circular(6)),
      child: Text(label, style: TextStyle(color: txt, fontWeight: FontWeight.w800, fontSize: 11)),
    );
  }

  // =========================================================================
  // TAB 4: ACCOUNT & SETTINGS
  // =========================================================================
  Widget _buildAccountTab(VendorAppState state) {
    final loc = GBLocalizations.of(context);
    final isHi = loc.isHindi;

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // Shopkeeper Profile Card
        Card(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                const CircleAvatar(
                  radius: 28,
                  backgroundColor: GBColors.primary,
                  child: Icon(Icons.storefront, color: Colors.white, size: 30),
                ),
                const SizedBox(width: 14),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        state.myStore?.shopName ?? (isHi ? 'गाँव बाज़ार स्टोर' : 'GaonBazaar Store'),
                        style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        state.currentUser?.name ?? state.myStore?.ownerName ?? (isHi ? 'दुकानदार' : 'Shopkeeper'),
                        style: const TextStyle(color: Colors.grey, fontSize: 13),
                      ),
                      Text(
                        state.currentUser?.phone ?? '',
                        style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 12),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),

        const SizedBox(height: 16),

        // Settings Items
        _buildAccountTile(
          icon: Icons.store_outlined,
          title: isHi ? 'दुकान प्रबंधन व सेटिंग्स' : 'Store Profile & Settings',
          onTap: () {
            Navigator.of(context).push(
              MaterialPageRoute(builder: (_) => const VendorStoreSettingsScreen()),
            );
          },
        ),
        _buildAccountTile(
          icon: Icons.verified_user_outlined,
          title: isHi ? 'सत्यापन व केवाईसी स्थिति' : 'Verification & KYC Status',
          subtitle: state.isStoreApproved ? (isHi ? 'सत्यापित (Verified)' : 'Verified') : (isHi ? 'समीक्षाधीन (Under Review)' : 'Under Review'),
          onTap: () {
            Navigator.of(context).push(
              MaterialPageRoute(builder: (_) => const VendorStoreSettingsScreen()),
            );
          },
        ),
        _buildAccountTile(
          icon: Icons.account_balance_outlined,
          title: isHi ? 'बैंक व यूपीआई सेटिंग्स' : 'Bank & UPI Settings',
          subtitle: state.myStore?.upiId ?? 'Not linked',
          onTap: () => setState(() => _navIndex = 3),
        ),
        _buildAccountTile(
          icon: Icons.language_outlined,
          title: isHi ? 'भाषा (Language)' : 'Language',
          subtitle: isHi ? 'हिंदी (Hindi)' : 'English',
          onTap: () {
            showDialog(
              context: context,
              builder: (ctx) => AlertDialog(
                title: Text(isHi ? 'भाषा बदलें' : 'Change Language'),
                content: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    ListTile(
                      title: const Text('हिंदी (Hindi)'),
                      leading: Radio<String>(
                        value: 'hi',
                        groupValue: state.currentLocale,
                        onChanged: (v) {
                          state.setLocale('hi');
                          Navigator.of(ctx).pop();
                        },
                      ),
                    ),
                    ListTile(
                      title: const Text('English'),
                      leading: Radio<String>(
                        value: 'en',
                        groupValue: state.currentLocale,
                        onChanged: (v) {
                          state.setLocale('en');
                          Navigator.of(ctx).pop();
                        },
                      ),
                    ),
                  ],
                ),
              ),
            );
          },
        ),
        _buildAccountTile(
          icon: Icons.brightness_medium_outlined,
          title: isHi ? 'थीम (Theme)' : 'Theme Mode',
          subtitle: state.themeMode == ThemeMode.dark
              ? (isHi ? 'डार्क थीम' : 'Dark Mode')
              : (isHi ? 'लाइट थीम' : 'Light Mode'),
          onTap: () {
            state.setTheme(state.themeMode == ThemeMode.dark ? ThemeMode.light : ThemeMode.dark);
          },
        ),
        _buildAccountTile(
          icon: Icons.headset_mic_outlined,
          title: isHi ? 'दुकानदार सहायता व हेल्पलाइन' : 'Helpdesk & Support',
          onTap: () async {
            final uri = Uri.parse('tel:+919800000000');
            if (await canLaunchUrl(uri)) await launchUrl(uri);
          },
        ),

        const SizedBox(height: 20),

        // Logout
        ElevatedButton.icon(
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.red.shade700,
            minimumSize: const Size.fromHeight(48),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
          ),
          icon: const Icon(Icons.logout),
          label: Text(isHi ? 'लॉगआउट करें' : 'Logout'),
          onPressed: () {
            showDialog(
              context: context,
              builder: (ctx) => AlertDialog(
                title: Text(isHi ? 'लॉगआउट की पुष्टि' : 'Confirm Logout'),
                content: Text(isHi ? 'क्या आप वाकई ऐप से बाहर निकलना चाहते हैं?' : 'Are you sure you want to log out?'),
                actions: [
                  TextButton(onPressed: () => Navigator.of(ctx).pop(), child: Text(isHi ? 'रद्द करें' : 'Cancel')),
                  ElevatedButton(
                    style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
                    onPressed: () {
                      Navigator.of(ctx).pop();
                      state.logout();
                      Navigator.of(context).pushAndRemoveUntil(
                        MaterialPageRoute(builder: (_) => const VendorAuthScreen()),
                        (r) => false,
                      );
                    },
                    child: Text(isHi ? 'लॉगआउट' : 'Logout'),
                  ),
                ],
              ),
            );
          },
        ),
        const SizedBox(height: 24),
      ],
    );
  }

  Widget _buildAccountTile({
    required IconData icon,
    required String title,
    String? subtitle,
    required VoidCallback onTap,
  }) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
      child: ListTile(
        leading: Icon(icon, color: GBColors.primary),
        title: Text(title, style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 14)),
        subtitle: subtitle != null ? Text(subtitle, style: const TextStyle(fontSize: 12, color: Colors.grey)) : null,
        trailing: const Icon(Icons.chevron_right, size: 20, color: Colors.grey),
        onTap: onTap,
      ),
    );
  }
}
