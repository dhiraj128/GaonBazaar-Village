import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import 'package:shared_models/shared_models.dart';
import '../state/vendor_state.dart';
import 'product_library_screen.dart';
import 'vendor_inventory_screen.dart';
import 'vendor_settlements_screen.dart';
import 'vendor_auth_screen.dart';

class VendorDashboardScreen extends StatefulWidget {
  const VendorDashboardScreen({super.key});

  @override
  State<VendorDashboardScreen> createState() => _VendorDashboardScreenState();
}

class _VendorDashboardScreenState extends State<VendorDashboardScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  bool _isActing = false;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _handleAction(VendorAppState state, String orderId, String action) async {
    setState(() => _isActing = true);
    final isHi = state.isHindi;
    final success = await state.handleOrderAction(orderId, action);
    if (!mounted) return;
    setState(() => _isActing = false);

    final actionLabel = action == 'ACCEPT'
        ? (isHi ? 'स्वीकार किया गया' : 'Accepted')
        : action == 'PACK'
            ? (isHi ? 'पैक चिह्नित किया गया' : 'Marked Packed')
            : action == 'HANDOFF'
                ? (isHi ? 'डिलीवरी पार्टनर को सौंपा गया' : 'Handed over to runner')
                : (isHi ? 'अस्वीकार किया गया' : 'Rejected');

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          success
              ? (isHi ? 'ऑर्डर #$orderId: $actionLabel' : 'Order #$orderId: $actionLabel')
              : (isHi ? 'कार्रवाई विफल रही। कृपया पुनः प्रयास करें।' : 'Action failed. Please retry.'),
        ),
        backgroundColor: success ? GBColors.success : GBColors.error,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final state = VendorStateProvider.of(context);
    final isHi = state.isHindi;

    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              state.myStore?.shopName ?? (isHi ? 'माँ शारदा किराना स्टोर' : 'Maa Sharda Kirana Store'),
              style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16),
            ),
            Text(
              '${state.myStore?.village ?? "Chaturshi"}, ${state.myStore?.block ?? "Minapur"}',
              style: const TextStyle(fontSize: 11, color: Colors.grey),
            ),
          ],
        ),
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 8),
            child: Row(
              children: [
                Text(
                  state.isStoreOnline
                      ? (isHi ? 'ऑनलाइन' : 'Online')
                      : (isHi ? 'ऑफलाइन' : 'Offline'),
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
        bottom: TabBar(
          controller: _tabController,
          labelColor: GBColors.primary,
          unselectedLabelColor: Colors.grey,
          indicatorColor: GBColors.primary,
          tabs: [
            Tab(text: isHi ? 'नया' : 'New'),
            Tab(text: isHi ? 'पैकिंग' : 'Packing'),
            Tab(text: isHi ? 'तैयार' : 'Ready'),
            Tab(text: isHi ? 'पूर्ण' : 'Delivered'),
          ],
        ),
      ),
      drawer: Drawer(
        child: ListView(
          padding: EdgeInsets.zero,
          children: [
            DrawerHeader(
              decoration: const BoxDecoration(color: GBColors.primaryDark),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  const Icon(Icons.storefront, color: Colors.white, size: 36),
                  const SizedBox(height: 8),
                  Text(
                    state.myStore?.shopName ?? (isHi ? 'माँ शारदा किराना स्टोर' : 'Maa Sharda Kirana Store'),
                    style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w800, fontSize: 16),
                  ),
                  Text(
                    isHi ? '0% कमीशन विक्रेता खाता' : '0% Commission Vendor Account',
                    style: const TextStyle(color: Colors.white70, fontSize: 12),
                  ),
                ],
              ),
            ),
            ListTile(
              leading: const Icon(Icons.inventory_2_outlined),
              title: Text(isHi ? 'इन्वेंट्री प्रबंधन' : 'Inventory Management'),
              onTap: () {
                Navigator.of(context).pop();
                Navigator.of(context).push(MaterialPageRoute(builder: (_) => const VendorInventoryScreen()));
              },
            ),
            ListTile(
              leading: const Icon(Icons.library_add_outlined),
              title: Text(isHi ? 'केंद्रीय उत्पाद कैटलॉग' : 'Product Catalog'),
              onTap: () {
                Navigator.of(context).pop();
                Navigator.of(context).push(MaterialPageRoute(builder: (_) => const ProductLibraryScreen()));
              },
            ),
            ListTile(
              leading: const Icon(Icons.account_balance_wallet_outlined),
              title: Text(isHi ? 'कमाई व सेटलमेंट' : 'Earnings & Settlements'),
              onTap: () {
                Navigator.of(context).pop();
                Navigator.of(context).push(MaterialPageRoute(builder: (_) => const VendorSettlementsScreen()));
              },
            ),
            const Divider(),
            ListTile(
              leading: const Icon(Icons.language),
              title: Text(isHi ? 'भाषा (Language)' : 'Language'),
              trailing: DropdownButton<String>(
                value: state.currentLocale,
                underline: const SizedBox(),
                items: const [
                  DropdownMenuItem(value: 'hi', child: Text('हिंदी')),
                  DropdownMenuItem(value: 'en', child: Text('English')),
                ],
                onChanged: (lang) {
                  if (lang != null) state.setLocale(lang);
                },
              ),
            ),
            ListTile(
              leading: Icon(state.themeMode == ThemeMode.dark ? Icons.dark_mode : Icons.light_mode),
              title: Text(isHi ? 'डार्क थीम' : 'Dark Theme'),
              trailing: Switch(
                value: state.themeMode == ThemeMode.dark,
                onChanged: (val) {
                  state.setTheme(val ? ThemeMode.dark : ThemeMode.light);
                },
              ),
            ),
            ListTile(
              leading: const Icon(Icons.support_agent, color: GBColors.primary),
              title: Text(isHi ? 'हेल्पलाइन सहायता' : 'Support Helpline'),
              subtitle: const Text('+91 9800000000'),
              onTap: () {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text(isHi ? 'कॉलिंग हेल्पलाइन: +91 9800000000' : 'Calling helpline: +91 9800000000'),
                  ),
                );
              },
            ),
            const Divider(),
            ListTile(
              leading: const Icon(Icons.logout, color: GBColors.error),
              title: Text(isHi ? 'लॉग आउट' : 'Logout', style: const TextStyle(color: GBColors.error, fontWeight: FontWeight.w700)),
              onTap: () {
                state.logout();
                Navigator.of(context).pushAndRemoveUntil(
                  MaterialPageRoute(builder: (_) => const VendorAuthScreen()),
                  (r) => false,
                );
              },
            ),
          ],
        ),
      ),
      body: SafeArea(
        child: Column(
          children: [
            // Approval Warning Banner if store not yet approved
            if (!state.isStoreApproved)
              Container(
                width: double.infinity,
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                color: Colors.amber.shade100,
                child: Row(
                  children: [
                    Icon(Icons.pending_actions, color: Colors.amber.shade900, size: 20),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Text(
                        isHi
                            ? 'आपकी दुकान सत्यापन प्रक्रिया में है। सुपर एडमिन द्वारा अनुमोदन के बाद ही आपकी दुकान ग्राहकों को दिखाई देगी।'
                            : 'Your store is under verification. It will become visible to customers after Super Admin approval.',
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.amber.shade900,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                  ],
                ),
              ),

            // Store Status Bar
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
              color: state.isStoreOnline ? GBColors.success.withOpacity(0.08) : GBColors.error.withOpacity(0.08),
              child: Row(
                children: [
                  Icon(
                    state.isStoreOnline ? Icons.check_circle : Icons.pause_circle,
                    size: 16,
                    color: state.isStoreOnline ? GBColors.success : GBColors.error,
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      state.isStoreOnline
                          ? (isHi ? 'दुकान ऑनलाइन है — नए ऑर्डर प्राप्त हो रहे हैं।' : 'Store is Online — Accepting orders.')
                          : (isHi ? 'दुकान ऑफलाइन है — ग्राहक नए ऑर्डर नहीं दे सकते।' : 'Store is Offline — Not accepting orders.'),
                      style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                        color: state.isStoreOnline ? GBColors.success : GBColors.error,
                      ),
                    ),
                  ),
                ],
              ),
            ),

            // Tab Views for Orders with Pull to Refresh
            Expanded(
              child: RefreshIndicator(
                onRefresh: () => state.fetchOrders(),
                child: TabBarView(
                  controller: _tabController,
                  children: [
                    _buildOrdersList(state, 'PLACED'),
                    _buildOrdersList(state, 'ACCEPTED'),
                    _buildOrdersList(state, 'PACKED'),
                    _buildOrdersList(state, 'DELIVERED'),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: 0,
        onTap: (idx) {
          if (idx == 1) {
            Navigator.of(context).push(MaterialPageRoute(builder: (_) => const VendorInventoryScreen()));
          } else if (idx == 2) {
            Navigator.of(context).push(MaterialPageRoute(builder: (_) => const ProductLibraryScreen()));
          } else if (idx == 3) {
            Navigator.of(context).push(MaterialPageRoute(builder: (_) => const VendorSettlementsScreen()));
          }
        },
        selectedItemColor: GBColors.primary,
        unselectedItemColor: Colors.grey,
        type: BottomNavigationBarType.fixed,
        items: [
          BottomNavigationBarItem(
            icon: const Icon(Icons.receipt_long_outlined),
            label: isHi ? 'ऑर्डर' : 'Orders',
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.inventory_2_outlined),
            label: isHi ? 'इन्वेंट्री' : 'Inventory',
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.library_add_outlined),
            label: isHi ? 'कैटलॉग' : 'Catalog',
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.account_balance_wallet_outlined),
            label: isHi ? 'सेटलमेंट' : 'Settlements',
          ),
        ],
      ),
    );
  }

  Widget _buildOrdersList(VendorAppState state, String statusFilter) {
    final isHi = state.isHindi;

    // Filter store orders from state
    final orders = state.storeOrders.where((o) {
      if (statusFilter == 'PLACED') return o.status == 'PLACED';
      if (statusFilter == 'ACCEPTED') return o.status == 'ACCEPTED';
      if (statusFilter == 'PACKED') {
        return o.status == 'PACKED' || o.status == 'RUNNER_ASSIGNED' || o.status == 'PICKED_UP';
      }
      if (statusFilter == 'DELIVERED') return o.status == 'DELIVERED' || o.status == 'CANCELLED';
      return false;
    }).toList();

    if (orders.isEmpty) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(Icons.inbox_outlined, size: 52, color: Colors.grey.shade400),
              const SizedBox(height: 12),
              Text(
                isHi ? 'इस श्रेणी में कोई सक्रिय ऑर्डर नहीं है।' : 'No active orders in this category.',
                style: const TextStyle(color: Colors.grey, fontWeight: FontWeight.w600, fontSize: 14),
              ),
              const SizedBox(height: 8),
              OutlinedButton.icon(
                onPressed: () => state.fetchOrders(),
                icon: const Icon(Icons.refresh, size: 16),
                label: Text(isHi ? 'ताज़ा करें' : 'Refresh'),
              ),
            ],
          ),
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: orders.length,
      itemBuilder: (context, idx) {
        final order = orders[idx];
        return _buildLiveOrderCard(state, order);
      },
    );
  }

  Widget _buildLiveOrderCard(VendorAppState state, GBOrder order) {
    final isHi = state.isHindi;
    final displayId = order.id.length > 8 ? order.id.substring(0, 8) : order.id;
    final itemsSummary = order.items.map((i) => '${isHi ? i.nameHi : i.nameEn} x ${i.quantity}').join(', ');

    return Container(
      margin: const EdgeInsets.only(bottom: 14),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey.shade300),
        boxShadow: [
          BoxShadow(color: Colors.black.withOpacity(0.04), blurRadius: 4, offset: const Offset(0, 1)),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('#$displayId', style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 15)),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(
                  color: _getStatusColor(order.status).withOpacity(0.12),
                  borderRadius: BorderRadius.circular(6),
                ),
                child: Text(
                  _getStatusLabel(order.status, isHi),
                  style: TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.w700,
                    color: _getStatusColor(order.status),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              const Icon(Icons.location_on_outlined, size: 16, color: Colors.grey),
              const SizedBox(width: 6),
              Expanded(
                child: Text(
                  order.deliveryAddress,
                  style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 13),
                ),
              ),
            ],
          ),
          const SizedBox(height: 6),
          Text(
            itemsSummary.isNotEmpty ? itemsSummary : (isHi ? 'किराना सामग्री' : 'Grocery items'),
            style: const TextStyle(fontSize: 13, color: Colors.black87),
          ),
          if (order.runnerName != null) ...[
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: GBColors.primaryLight.withOpacity(0.15),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                children: [
                  const Icon(Icons.two_wheeler, size: 16, color: GBColors.primary),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      '${isHi ? "डिलीवरी पार्टनर" : "Delivery Partner"}: ${order.runnerName}',
                      style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700),
                    ),
                  ),
                  if (order.runnerPhone != null)
                    InkWell(
                      onTap: () {
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(content: Text('${isHi ? "कॉलिंग पार्टनर" : "Calling partner"}: ${order.runnerPhone}')),
                        );
                      },
                      child: Text(
                        isHi ? 'कॉल करें' : 'Call',
                        style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w800, color: GBColors.primary),
                      ),
                    ),
                ],
              ),
            ),
          ],
          const Divider(height: 20),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '₹${order.totalAmount.toStringAsFixed(0)}',
                    style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 17, color: GBColors.primary),
                  ),
                  Text(
                    order.paymentMethod,
                    style: const TextStyle(fontSize: 11, color: Colors.grey, fontWeight: FontWeight.w600),
                  ),
                ],
              ),
              _buildOrderActions(state, order.id, order.status, isHi),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildOrderActions(VendorAppState state, String orderId, String status, bool isHi) {
    if (_isActing) {
      return const SizedBox(width: 24, height: 24, child: CircularProgressIndicator(strokeWidth: 2));
    }

    if (status == 'PLACED') {
      return Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          OutlinedButton(
            onPressed: () => _handleAction(state, orderId, 'REJECT'),
            style: OutlinedButton.styleFrom(
              foregroundColor: GBColors.error,
              side: const BorderSide(color: GBColors.error),
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
            ),
            child: Text(isHi ? 'अस्वीकार' : 'Reject', style: const TextStyle(fontSize: 12)),
          ),
          const SizedBox(width: 8),
          ElevatedButton(
            onPressed: () => _handleAction(state, orderId, 'ACCEPT'),
            style: ElevatedButton.styleFrom(
              backgroundColor: GBColors.primary,
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            ),
            child: Text(isHi ? 'स्वीकार करें' : 'Accept', style: const TextStyle(fontSize: 12)),
          ),
        ],
      );
    } else if (status == 'ACCEPTED') {
      return ElevatedButton.icon(
        onPressed: () => _handleAction(state, orderId, 'PACK'),
        style: ElevatedButton.styleFrom(
          backgroundColor: GBColors.secondary,
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        ),
        icon: const Icon(Icons.inventory_sharp, size: 14),
        label: Text(isHi ? 'पैक हो गया' : 'Mark Packed', style: const TextStyle(fontSize: 12)),
      );
    } else if (status == 'PACKED') {
      return ElevatedButton.icon(
        onPressed: () => _handleAction(state, orderId, 'HANDOFF'),
        style: ElevatedButton.styleFrom(
          backgroundColor: GBColors.primaryDark,
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        ),
        icon: const Icon(Icons.delivery_dining, size: 14),
        label: Text(isHi ? 'पार्टनर को सौंपा' : 'Handoff to Runner', style: const TextStyle(fontSize: 12)),
      );
    } else {
      return const SizedBox.shrink();
    }
  }

  Color _getStatusColor(String status) {
    switch (status) {
      case 'PLACED':
        return Colors.blue;
      case 'ACCEPTED':
        return Colors.orange;
      case 'PACKED':
      case 'RUNNER_ASSIGNED':
      case 'PICKED_UP':
        return GBColors.secondary;
      case 'DELIVERED':
        return GBColors.success;
      case 'CANCELLED':
        return GBColors.error;
      default:
        return Colors.grey;
    }
  }

  String _getStatusLabel(String status, bool isHi) {
    switch (status) {
      case 'PLACED':
        return isHi ? 'नया' : 'Placed';
      case 'ACCEPTED':
        return isHi ? 'स्वीकृत' : 'Accepted';
      case 'PACKED':
        return isHi ? 'पैक किया' : 'Packed';
      case 'RUNNER_ASSIGNED':
        return isHi ? 'पार्टनर रवाना' : 'Runner Assigned';
      case 'PICKED_UP':
        return isHi ? 'उठाया गया' : 'Picked Up';
      case 'DELIVERED':
        return isHi ? 'डिलीवर' : 'Delivered';
      case 'CANCELLED':
        return isHi ? 'रद्द' : 'Cancelled';
      default:
        return status;
    }
  }
}
