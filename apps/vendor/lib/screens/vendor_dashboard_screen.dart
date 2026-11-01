import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
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

  // Active incoming sample orders
  final List<Map<String, dynamic>> _sampleOrders = [
    {
      'id': 'ord_101',
      'customer': 'Ramesh Singh (Chaturshi)',
      'items': 'चक्की आटा x 2 kg, गाय का दूध x 1 L',
      'amount': 132.0,
      'status': 'PLACED',
      'time': '2 mins ago',
    },
    {
      'id': 'ord_102',
      'customer': 'Suresh Kumar (Tubanaghara)',
      'items': 'सरसों तेल x 1 L, आलू x 2 kg',
      'amount': 190.0,
      'status': 'ACCEPTED',
      'time': '12 mins ago',
    },
    {
      'id': 'ord_103',
      'customer': 'Sunil Sah (Sivay Patti)',
      'items': 'एलईडी बल्ब x 2, अगरबत्ती x 1',
      'amount': 190.0,
      'status': 'PACKED',
      'time': '25 mins ago',
    },
  ];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
  }

  void _handleAction(String orderId, String action) {
    setState(() {
      for (final o in _sampleOrders) {
        if (o['id'] == orderId) {
          if (action == 'ACCEPT') o['status'] = 'ACCEPTED';
          if (action == 'PACK') o['status'] = 'PACKED';
          if (action == 'HANDOFF') o['status'] = 'COMPLETED';
          if (action == 'REJECT') o['status'] = 'REJECTED';
          break;
        }
      }
    });
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('ऑर्डर #$orderId: $action किया गया।')),
    );
  }

  @override
  Widget build(BuildContext context) {
    final state = VendorStateProvider.of(context);

    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(state.myStore?.shopName ?? 'माँ शारदा किराना स्टोर', style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16)),
            Text('${state.myStore?.village ?? "Chaturshi"}, Minapur', style: const TextStyle(fontSize: 11, color: Colors.grey)),
          ],
        ),
        actions: [
          // Store Online / Offline Toggle
          Padding(
            padding: const EdgeInsets.only(right: 8),
            child: Row(
              children: [
                Text(
                  state.isStoreOnline ? 'Online' : 'Offline',
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w700,
                    color: state.isStoreOnline ? GBColors.success : GBColors.error,
                  ),
                ),
                Switch(
                  value: state.isStoreOnline,
                  activeColor: GBColors.success,
                  onChanged: (v) => state.toggleStoreOnline(),
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
          tabs: const [
            Tab(text: 'नया (New)'),
            Tab(text: 'पैकिंग (Pack)'),
            Tab(text: 'पिकअप (Ready)'),
            Tab(text: 'पूर्ण (Done)'),
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
                  Text(state.myStore?.shopName ?? 'माँ शारदा किराना स्टोर', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w800, fontSize: 16)),
                  const Text('0% कमीशन विक्रेता खाता', style: TextStyle(color: Colors.white70, fontSize: 12)),
                ],
              ),
            ),
            ListTile(
              leading: const Icon(Icons.inventory_2_outlined),
              title: const Text('इन्वेंट्री प्रबंधन (Inventory)'),
              onTap: () {
                Navigator.of(context).pop();
                Navigator.of(context).push(MaterialPageRoute(builder: (_) => const VendorInventoryScreen()));
              },
            ),
            ListTile(
              leading: const Icon(Icons.library_add_outlined),
              title: const Text('केंद्रीय उत्पाद लाइब्रेरी (Product Catalog)'),
              onTap: () {
                Navigator.of(context).pop();
                Navigator.of(context).push(MaterialPageRoute(builder: (_) => const ProductLibraryScreen()));
              },
            ),
            ListTile(
              leading: const Icon(Icons.account_balance_wallet_outlined),
              title: const Text('कमाई व सेटलमेंट (Settlements)'),
              onTap: () {
                Navigator.of(context).pop();
                Navigator.of(context).push(MaterialPageRoute(builder: (_) => const VendorSettlementsScreen()));
              },
            ),
            const Divider(),
            ListTile(
              leading: const Icon(Icons.logout, color: GBColors.error),
              title: const Text('लॉग आउट (Logout)', style: TextStyle(color: GBColors.error, fontWeight: FontWeight.w700)),
              onTap: () {
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
            // Quick Status Bar
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
                          ? 'दुकान ऑनलाइन है — नए ऑर्डर स्वीकार किए जा रहे हैं।'
                          : 'दुकान ऑफलाइन है — ग्राहक नए ऑर्डर नहीं दे सकते।',
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

            // Tab Views for Orders
            Expanded(
              child: TabBarView(
                controller: _tabController,
                children: [
                  // Tab 0: New Orders (PLACED)
                  _buildOrdersList('PLACED'),
                  // Tab 1: In Packing (ACCEPTED)
                  _buildOrdersList('ACCEPTED'),
                  // Tab 2: Ready for Pickup (PACKED)
                  _buildOrdersList('PACKED'),
                  // Tab 3: Completed Orders
                  _buildOrdersList('COMPLETED'),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildOrdersList(String statusFilter) {
    final list = _sampleOrders.where((o) => o['status'] == statusFilter).toList();

    if (list.isEmpty) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(Icons.inbox_outlined, size: 48, color: Colors.grey.shade400),
              const SizedBox(height: 12),
              Text('इस श्रेणी में कोई ऑर्डर नहीं है ($statusFilter)', style: const TextStyle(color: Colors.grey, fontWeight: FontWeight.w600)),
            ],
          ),
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: list.length,
      itemBuilder: (context, idx) {
        final order = list[idx];
        return Container(
          margin: const EdgeInsets.only(bottom: 14),
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: Colors.white,
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
                  Text('Order #${order['id']}', style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 15)),
                  Text(order['time'] as String, style: const TextStyle(fontSize: 12, color: Colors.grey)),
                ],
              ),
              const SizedBox(height: 6),
              Text(order['customer'] as String, style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13)),
              const SizedBox(height: 4),
              Text(order['items'] as String, style: const TextStyle(fontSize: 12, color: Colors.black87)),
              const Divider(height: 20),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('₹${order['amount']}', style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 16, color: GBColors.primary)),
                  Row(
                    children: [
                      if (order['status'] == 'PLACED') ...[
                        OutlinedButton(
                          onPressed: () => _handleAction(order['id'] as String, 'REJECT'),
                          style: OutlinedButton.styleFrom(foregroundColor: GBColors.error),
                          child: const Text('अस्वीकार'),
                        ),
                        const SizedBox(width: 8),
                        ElevatedButton(
                          onPressed: () => _handleAction(order['id'] as String, 'ACCEPT'),
                          style: ElevatedButton.styleFrom(backgroundColor: GBColors.primary),
                          child: const Text('स्वीकार करें'),
                        ),
                      ] else if (order['status'] == 'ACCEPTED') ...[
                        ElevatedButton(
                          onPressed: () => _handleAction(order['id'] as String, 'PACK'),
                          style: ElevatedButton.styleFrom(backgroundColor: GBColors.secondary),
                          child: const Text('पैक हो गया (Mark Packed)'),
                        ),
                      ] else if (order['status'] == 'PACKED') ...[
                        ElevatedButton(
                          onPressed: () => _handleAction(order['id'] as String, 'HANDOFF'),
                          style: ElevatedButton.styleFrom(backgroundColor: GBColors.primaryDark),
                          child: const Text('डिलीवरी साथी को दिया (Handoff)'),
                        ),
                      ],
                    ],
                  ),
                ],
              ),
            ],
          ),
        );
      },
    );
  }
}
