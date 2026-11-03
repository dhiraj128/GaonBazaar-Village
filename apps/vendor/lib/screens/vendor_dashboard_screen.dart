import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import 'package:localization/localization.dart';
import 'package:shared_models/shared_models.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:url_launcher/url_launcher.dart';
import '../state/vendor_state.dart';
import 'vendor_auth_screen.dart';
import 'account_subpages.dart';
import 'product_library_screen.dart';

class VendorDashboardScreen extends StatefulWidget {
  const VendorDashboardScreen({super.key});

  @override
  State<VendorDashboardScreen> createState() => _VendorDashboardScreenState();
}

class _VendorDashboardScreenState extends State<VendorDashboardScreen> with SingleTickerProviderStateMixin {
  int _navIndex = 0;
  bool _isActing = false;

  // Sub-tabs for Tab 1: Orders (Home)
  late TabController _ordersTabController;

  // Tab 2: Inventory Search
  final _inventorySearchCtrl = TextEditingController();
  String _inventorySearchQuery = '';

  @override
  void initState() {
    super.initState();
    _ordersTabController = TabController(length: 3, vsync: this);
    SharedPreferences.getInstance().then((prefs) {
      final nav = prefs.getInt('gb_v_pdf_nav');
      if (nav != null && nav >= 0 && nav < 4 && mounted) {
        setState(() => _navIndex = nav);
      }
      final sub = prefs.getInt('gb_v_pdf_orders_sub');
      if (sub != null && sub >= 0 && sub < 3 && mounted) {
        _ordersTabController.index = sub;
      }
    });
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final state = VendorStateProvider.of(context);
      state.fetchStoreProfile();
      state.fetchOrders();
      state.fetchFinances();
      state.fetchNotifications();
    });
  }

  @override
  void dispose() {
    _ordersTabController.dispose();
    _inventorySearchCtrl.dispose();
    super.dispose();
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

  void _showHandoverDialog(VendorAppState state, GBOrder order, bool isHi) {
    final codeCtrl = TextEditingController();
    bool isVerifying = false;
    String? errorText;

    showDialog(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (context, setDlgState) {
          return AlertDialog(
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
            title: Row(
              children: [
                const Icon(Icons.handshake_outlined, color: GBColors.primary),
                const SizedBox(width: 8),
                Text(
                  isHi ? 'रनर को सामान सौंपें' : 'Handover to Runner',
                  style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                ),
              ],
            ),
            content: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  isHi
                      ? 'रनर द्वारा दिखाए गए 4-अंकीय हैंडओवर कोड को दर्ज करें:'
                      : 'Enter the 4-digit handover code displayed on the Runner\'s phone:',
                  style: const TextStyle(fontSize: 13, color: Colors.grey),
                ),
                const SizedBox(height: 16),
                TextField(
                  controller: codeCtrl,
                  keyboardType: TextInputType.number,
                  maxLength: 4,
                  textAlign: TextAlign.center,
                  style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold, letterSpacing: 8),
                  decoration: InputDecoration(
                    hintText: '••••',
                    errorText: errorText,
                    border: const OutlineInputBorder(),
                  ),
                ),
              ],
            ),
            actions: [
              TextButton(
                onPressed: isVerifying ? null : () => Navigator.of(ctx).pop(),
                child: Text(isHi ? 'रद्द करें' : 'Cancel'),
              ),
              ElevatedButton(
                style: ElevatedButton.styleFrom(backgroundColor: GBColors.primary),
                onPressed: isVerifying
                    ? null
                    : () async {
                        final code = codeCtrl.text.trim();
                        if (code.length != 4) {
                          setDlgState(() => errorText = isHi ? '4 अंकों का कोड दर्ज करें' : 'Enter 4 digits');
                          return;
                        }
                        setDlgState(() {
                          isVerifying = true;
                          errorText = null;
                        });
                        final res = await state.handoffOrder(order.id, code);
                        if (!mounted) return;
                        if (res['success'] == true) {
                          Navigator.of(ctx).pop();
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(
                              content: Text(isHi ? 'हैंडओवर सफल! सामान रनर को सौंपा गया।' : 'Handover successful! Order handed over.'),
                              backgroundColor: GBColors.success,
                            ),
                          );
                        } else {
                          setDlgState(() {
                            isVerifying = false;
                            errorText = res['error'] as String? ?? (isHi ? 'अमान्य कोड' : 'Invalid code');
                          });
                        }
                      },
                child: isVerifying
                    ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                    : Text(isHi ? 'सत्यापित करें' : 'Verify & Handover'),
              ),
            ],
          );
        },
      ),
    );
  }

  void _showBankUpdateModal(VendorAppState state, bool isHi) {
    final otpCtrl = TextEditingController(text: '123456');
    final holderCtrl = TextEditingController(text: state.currentUser?.name ?? state.myStore?.ownerName ?? '');
    final acctCtrl = TextEditingController();
    final ifscCtrl = TextEditingController();
    int modalStep = 1; // 1: OTP gate, 2: Bank details + Penny drop, 3: Success with 48h cooldown
    bool isLoading = false;
    String? errorMsg;
    String? cooldownMessage;

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
      builder: (ctx) => StatefulBuilder(
        builder: (context, setModalState) {
          return Padding(
            padding: EdgeInsets.only(
              left: 20,
              right: 20,
              top: 20,
              bottom: MediaQuery.of(ctx).viewInsets.bottom + 20,
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      isHi ? 'बैंक विवरण अपडेट' : 'Update Bank Details',
                      style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                    ),
                    IconButton(icon: const Icon(Icons.close), onPressed: () => Navigator.of(ctx).pop()),
                  ],
                ),
                const Divider(),
                if (errorMsg != null) ...[
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(color: Colors.red.shade50, borderRadius: BorderRadius.circular(8)),
                    child: Text(errorMsg!, style: TextStyle(color: Colors.red.shade900, fontSize: 12)),
                  ),
                  const SizedBox(height: 10),
                ],

                if (modalStep == 1) ...[
                  Text(
                    isHi ? 'सुरक्षा हेतु पंजीकृत मोबाइल पर भेजा गया 4/6-अंकीय ओटीपी दर्ज करें:' : 'Enter OTP sent to your registered mobile:',
                    style: const TextStyle(fontSize: 13, color: Colors.grey),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: otpCtrl,
                    keyboardType: TextInputType.number,
                    maxLength: 6,
                    decoration: InputDecoration(
                      labelText: isHi ? 'सुरक्षा ओटीपी' : 'Security OTP',
                      hintText: '123456',
                      prefixIcon: const Icon(Icons.lock_clock_outlined),
                      border: const OutlineInputBorder(),
                    ),
                  ),
                  const SizedBox(height: 14),
                  SizedBox(
                    width: double.infinity,
                    height: 46,
                    child: ElevatedButton(
                      style: ElevatedButton.styleFrom(backgroundColor: GBColors.primary),
                      onPressed: () {
                        if (otpCtrl.text.trim().length < 4) {
                          setModalState(() => errorMsg = isHi ? 'वैध ओटीपी दर्ज करें' : 'Enter valid OTP');
                          return;
                        }
                        setModalState(() {
                          errorMsg = null;
                          modalStep = 2;
                        });
                      },
                      child: Text(isHi ? 'ओटीपी सत्यापित करें' : 'Verify OTP & Proceed'),
                    ),
                  ),
                ] else if (modalStep == 2) ...[
                  TextField(
                    controller: holderCtrl,
                    decoration: InputDecoration(
                      labelText: isHi ? 'खाताधारक का नाम' : 'Account Holder Name',
                      prefixIcon: const Icon(Icons.person_outline),
                      border: const OutlineInputBorder(),
                    ),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: acctCtrl,
                    keyboardType: TextInputType.number,
                    decoration: InputDecoration(
                      labelText: isHi ? 'नया बैंक खाता संख्या' : 'New Bank Account Number',
                      prefixIcon: const Icon(Icons.account_balance_outlined),
                      border: const OutlineInputBorder(),
                    ),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: ifscCtrl,
                    textCapitalization: TextCapitalization.characters,
                    decoration: InputDecoration(
                      labelText: 'IFSC Code',
                      hintText: 'e.g. SBIN0001234',
                      prefixIcon: const Icon(Icons.domain_outlined),
                      border: const OutlineInputBorder(),
                    ),
                  ),
                  const SizedBox(height: 16),
                  SizedBox(
                    width: double.infinity,
                    height: 46,
                    child: ElevatedButton(
                      style: ElevatedButton.styleFrom(backgroundColor: GBColors.primary),
                      onPressed: isLoading
                          ? null
                          : () async {
                              final acct = acctCtrl.text.trim();
                              final ifsc = ifscCtrl.text.trim().toUpperCase();
                              if (acct.length < 9) {
                                setModalState(() => errorMsg = isHi ? 'अमान्य बैंक खाता' : 'Invalid account number');
                                return;
                              }
                              if (ifsc.length != 11) {
                                setModalState(() => errorMsg = isHi ? 'अमान्य IFSC कोड' : 'Invalid IFSC code');
                                return;
                              }
                              setModalState(() {
                                isLoading = true;
                                errorMsg = null;
                              });

                              // ₹1 Penny drop verification first
                              final pennyRes = await state.verifyPennyDrop(
                                accountHolderName: holderCtrl.text.trim(),
                                accountNumber: acct,
                                ifscCode: ifsc,
                              );
                              if (pennyRes['success'] != true) {
                                setModalState(() {
                                  isLoading = false;
                                  errorMsg = pennyRes['error'] as String? ?? (isHi ? 'पेनी ड्रॉप विफल' : 'Penny drop failed');
                                });
                                return;
                              }

                              // Update bank details with 48h cooldown
                              final updateRes = await state.updateBankDetails(
                                accountHolderName: holderCtrl.text.trim(),
                                accountNumber: acct,
                                ifscCode: ifsc,
                                otp: otpCtrl.text.trim(),
                              );
                              if (!mounted) return;
                              setModalState(() => isLoading = false);
                              if (updateRes['success'] == true) {
                                setModalState(() {
                                  cooldownMessage = updateRes['message'] as String? ??
                                      'Bank details updated. 48-hour security cooldown active before payouts resume.';
                                  modalStep = 3;
                                });
                              } else {
                                setModalState(() => errorMsg = updateRes['error'] as String?);
                              }
                            },
                      child: isLoading
                          ? const CircularProgressIndicator(color: Colors.white)
                          : Text(isHi ? '₹1 पेनी ड्रॉप व अपडेट करें' : 'Verify ₹1 Penny Drop & Update'),
                    ),
                  ),
                ] else if (modalStep == 3) ...[
                  const Icon(Icons.security_update_good, color: GBColors.primary, size: 48),
                  const SizedBox(height: 10),
                  Text(
                    isHi ? 'सुरक्षा कूलडाउन सक्रिय (48 घंटे)' : '48-Hour Security Cooldown Active',
                    style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                  ),
                  const SizedBox(height: 6),
                  Text(
                    cooldownMessage ?? (isHi ? 'बैंक खाता सफलतापूर्वक अपडेट हो गया है। धोखाधड़ी रोकने के लिए 48 घंटे का कूलडाउन लागू है।' : 'Updated. 48hr cooldown applied.'),
                    style: const TextStyle(fontSize: 13, color: Colors.grey),
                  ),
                  const SizedBox(height: 16),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      onPressed: () => Navigator.of(ctx).pop(),
                      child: Text(isHi ? 'पूर्ण' : 'Done'),
                    ),
                  ),
                ],
              ],
            ),
          );
        },
      ),
    );
  }

  void _showExitDialog(bool isHi) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(isHi ? 'ऐप से बाहर निकलें?' : 'Exit GaonBazaar?'),
        content: Text(isHi ? 'क्या आप वाकई बाहर निकलना चाहते हैं?' : 'Are you sure you want to exit the application?'),
        actions: [
          TextButton(onPressed: () => Navigator.of(ctx).pop(), child: Text(isHi ? 'रद्द करें' : 'Cancel')),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            onPressed: () {
              Navigator.of(ctx).pop();
              Navigator.of(context).maybePop();
            },
            child: Text(isHi ? 'बाहर निकलें' : 'Exit'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final state = VendorStateProvider.of(context);
    final loc = GBLocalizations.of(context);
    final isHi = loc.isHindi;
    final isDark = Theme.of(context).brightness == Brightness.dark;

    // PDF Page 5: History API & Back Navigation enforcement
    return PopScope(
      canPop: false,
      onPopInvokedWithResult: (didPop, result) {
        if (didPop) return;
        if (_navIndex != 0) {
          setState(() => _navIndex = 0);
        } else {
          _showExitDialog(isHi);
        }
      },
      child: Scaffold(
        appBar: AppBar(
          title: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                state.myStore?.shopName ?? (isHi ? 'गाँव बाज़ार विक्रेता' : 'GaonBazaar Shopkeeper'),
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
            // Header: Store Open/Close Toggle switch (PDF Page 2)
            Padding(
              padding: const EdgeInsets.only(right: 8),
              child: Row(
                children: [
                  Text(
                    state.isStoreOnline ? (isHi ? 'दुकान खुली' : 'Open') : (isHi ? 'दुकान बंद' : 'Closed'),
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w700,
                      color: state.isStoreOnline ? GBColors.success : GBColors.error,
                    ),
                  ),
                  Switch(
                    value: state.isStoreOnline,
                    activeThumbColor: GBColors.success,
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

        // EXACTLY 4 TABS AS SPECIFIED IN PDF PAGE 2
        body: IndexedStack(
          index: _navIndex,
          children: [
            _buildTab1Orders(state, isHi, isDark),
            _buildTab2Inventory(state, isHi, isDark),
            _buildTab3Ledger(state, isHi, isDark),
            _buildTab4ProfileSettings(state, isHi, isDark),
          ],
        ),

        // EXACTLY 4 BOTTOM NAVIGATION TABS AS SPECIFIED IN PDF PAGE 2
        bottomNavigationBar: NavigationBar(
          selectedIndex: _navIndex,
          onDestinationSelected: (idx) => setState(() => _navIndex = idx),
          destinations: [
            NavigationDestination(
              icon: const Icon(Icons.receipt_long_outlined),
              selectedIcon: const Icon(Icons.receipt_long),
              label: isHi ? 'ऑर्डर' : 'Orders',
            ),
            NavigationDestination(
              icon: const Icon(Icons.inventory_2_outlined),
              selectedIcon: const Icon(Icons.inventory_2),
              label: isHi ? 'इन्वेंट्री' : 'Inventory',
            ),
            NavigationDestination(
              icon: const Icon(Icons.account_balance_wallet_outlined),
              selectedIcon: const Icon(Icons.account_balance_wallet),
              label: isHi ? 'बहीखाता' : 'Ledger',
            ),
            NavigationDestination(
              icon: const Icon(Icons.person_outline),
              selectedIcon: const Icon(Icons.person),
              label: isHi ? 'प्रोफ़ाइल और सेटिंग्स' : 'Profile & Settings',
            ),
          ],
        ),
      ),
    );
  }

  // =========================================================================
  // TAB 1: ORDERS (HOME) — Bottom 1 (Left) per PDF Page 2
  // Sub-tabs: New Orders, Preparing, Ready for Pickup
  // Flow: Accept order -> Check items -> Mark as Ready -> Enter Runner 4-digit code to Handover
  // =========================================================================
  Widget _buildTab1Orders(VendorAppState state, bool isHi, bool isDark) {
    final newOrders = state.storeOrders.where((o) => o.status == 'PLACED').toList();
    final preparingOrders = state.storeOrders.where((o) => o.status == 'ACCEPTED' || o.status == 'PREPARING').toList();
    final readyOrders = state.storeOrders.where((o) => o.status == 'PACKED' || o.status == 'RUNNER_ASSIGNED').toList();

    return Column(
      children: [
        // Sub-tabs: New Orders, Preparing, Ready for Pickup
        Container(
          color: Theme.of(context).cardColor,
          child: TabBar(
            controller: _ordersTabController,
            labelColor: GBColors.primary,
            unselectedLabelColor: Colors.grey,
            indicatorColor: GBColors.primary,
            tabs: [
              Tab(
                text: isHi ? 'नए ऑर्डर (${newOrders.length})' : 'New Orders (${newOrders.length})',
              ),
              Tab(
                text: isHi ? 'तैयार हो रहे (${preparingOrders.length})' : 'Preparing (${preparingOrders.length})',
              ),
              Tab(
                text: isHi ? 'पिकअप हेतु तैयार (${readyOrders.length})' : 'Ready (${readyOrders.length})',
              ),
            ],
          ),
        ),
        Expanded(
          child: TabBarView(
            controller: _ordersTabController,
            children: [
              _buildOrderList(newOrders, 'NEW', state, isHi, isDark),
              _buildOrderList(preparingOrders, 'PREPARING', state, isHi, isDark),
              _buildOrderList(readyOrders, 'READY', state, isHi, isDark),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildOrderList(List<GBOrder> orders, String type, VendorAppState state, bool isHi, bool isDark) {
    if (orders.isEmpty) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(Icons.inventory_outlined, size: 48, color: Colors.grey.shade400),
              const SizedBox(height: 12),
              Text(
                isHi ? 'इस सूची में कोई ऑर्डर नहीं है' : 'No orders in this stage',
                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
              ),
            ],
          ),
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: orders.length,
      itemBuilder: (ctx, i) {
        final order = orders[i];
        final displayId = order.id.length > 8 ? order.id.substring(0, 8) : order.id;

        return Card(
          margin: const EdgeInsets.only(bottom: 14),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text('#$displayId', style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 15)),
                    Text(
                      '₹${order.totalAmount.toStringAsFixed(0)}',
                      style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 16, color: GBColors.primary),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Text(
                  '${isHi ? "ग्राहक पता" : "Customer Address"}: ${order.deliveryAddress.isNotEmpty ? order.deliveryAddress : "Gram Panchayat Area"}',
                  style: const TextStyle(fontSize: 12, color: Colors.grey),
                ),
                const Divider(height: 20),

                // Order Items Checklist
                Text(
                  isHi ? 'सामान की सूची:' : 'Order Items:',
                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
                ),
                const SizedBox(height: 6),
                ...order.items.map((item) => Padding(
                      padding: const EdgeInsets.symmetric(vertical: 2),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text('• ${item.nameHi.isNotEmpty ? (isHi ? item.nameHi : item.nameEn) : item.nameEn} x${item.quantity}', style: const TextStyle(fontSize: 13)),
                          Text('₹${item.totalPrice.toStringAsFixed(0)}', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                        ],
                      ),
                    )),
                const SizedBox(height: 16),

                // Action Buttons per PDF Flow:
                // Accept order -> Check items -> Mark as Ready -> Enter Runner's 4-digit code to Handover
                if (type == 'NEW') ...[
                  Row(
                    children: [
                      Expanded(
                        child: OutlinedButton(
                          onPressed: _isActing ? null : () => _handleAction(state, order.id, 'REJECT'),
                          child: Text(isHi ? 'अस्वीकार करें' : 'Reject'),
                        ),
                      ),
                      const SizedBox(width: 10),
                      Expanded(
                        child: ElevatedButton(
                          style: ElevatedButton.styleFrom(backgroundColor: GBColors.primary),
                          onPressed: _isActing ? null : () => _handleAction(state, order.id, 'ACCEPT'),
                          child: Text(isHi ? 'ऑर्डर स्वीकार करें' : 'Accept Order'),
                        ),
                      ),
                    ],
                  ),
                ] else if (type == 'PREPARING') ...[
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton.icon(
                      style: ElevatedButton.styleFrom(backgroundColor: Colors.teal.shade700),
                      icon: const Icon(Icons.check_circle_outline),
                      label: Text(isHi ? 'पिकअप हेतु तैयार चिह्नित करें' : 'Mark Ready for Pickup'),
                      onPressed: _isActing ? null : () => _handleAction(state, order.id, 'PACKED'),
                    ),
                  ),
                ] else if (type == 'READY') ...[
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton.icon(
                      style: ElevatedButton.styleFrom(backgroundColor: GBColors.primaryDark),
                      icon: const Icon(Icons.handshake_outlined),
                      label: Text(isHi ? 'रनर को हैंडओवर करें' : 'Handover to Runner'),
                      onPressed: () => _showHandoverDialog(state, order, isHi),
                    ),
                  ),
                ],
              ],
            ),
          ),
        );
      },
    );
  }

  // =========================================================================
  // TAB 2: INVENTORY — Bottom 2 per PDF Page 2
  // Search bar to find items. List of all store products.
  // Action: Vendor toggles items "In Stock" or "Out of Stock".
  // =========================================================================
  Widget _buildTab2Inventory(VendorAppState state, bool isHi, bool isDark) {
    final filtered = state.myProducts.where((p) {
      if (_inventorySearchQuery.isEmpty) return true;
      final q = _inventorySearchQuery.toLowerCase();
      return p.nameEn.toLowerCase().contains(q) || p.nameHi.toLowerCase().contains(q) || p.category.toLowerCase().contains(q);
    }).toList();

    return Column(
      children: [
        // Search Bar
        Padding(
          padding: const EdgeInsets.all(16),
          child: TextField(
            controller: _inventorySearchCtrl,
            decoration: InputDecoration(
              hintText: isHi ? 'उत्पाद खोजें (उदा: तेल, चीनी, आटा)...' : 'Search store products...',
              prefixIcon: const Icon(Icons.search),
              suffixIcon: _inventorySearchQuery.isNotEmpty
                  ? IconButton(
                      icon: const Icon(Icons.clear),
                      onPressed: () {
                        setState(() {
                          _inventorySearchCtrl.clear();
                          _inventorySearchQuery = '';
                        });
                      },
                    )
                  : null,
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
              contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            ),
            onChanged: (val) => setState(() => _inventorySearchQuery = val.trim()),
          ),
        ),

        // Product Count
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                '${filtered.length} ${isHi ? "उत्पाद उपलब्ध" : "Products"}',
                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: Colors.grey),
              ),
              TextButton.icon(
                icon: const Icon(Icons.add, size: 18),
                label: Text(isHi ? 'नया उत्पाद जोड़ें' : 'Add Product'),
                onPressed: () {
                  Navigator.of(context).push(
                    MaterialPageRoute(builder: (_) => const ProductLibraryScreen(isTab: false)),
                  );
                },
              ),
            ],
          ),
        ),
        const Divider(height: 1),

        // Store Products List with In Stock / Out of Stock toggle
        Expanded(
          child: filtered.isEmpty
              ? Center(
                  child: Text(isHi ? 'कोई उत्पाद नहीं मिला' : 'No products found'),
                )
              : ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: filtered.length,
                  itemBuilder: (ctx, i) {
                    final p = filtered[i];
                    return Card(
                      margin: const EdgeInsets.only(bottom: 10),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                      child: ListTile(
                        leading: ClipRRect(
                          borderRadius: BorderRadius.circular(8),
                          child: Image.network(
                            p.imageUrl,
                            width: 50,
                            height: 50,
                            fit: BoxFit.cover,
                            errorBuilder: (_, __, ___) => const Icon(Icons.image, size: 40),
                          ),
                        ),
                        title: Text(
                          isHi ? p.nameHi : p.nameEn,
                          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                        ),
                        subtitle: Text('₹${p.price.toStringAsFixed(0)} • ${p.unit} • स्टॉक: ${p.stockQuantity}'),
                        trailing: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Text(
                              p.inStock ? (isHi ? 'उपलब्ध' : 'In Stock') : (isHi ? 'समाप्त' : 'Out of Stock'),
                              style: TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.bold,
                                color: p.inStock ? GBColors.success : GBColors.error,
                              ),
                            ),
                            Switch(
                              value: p.inStock,
                              activeThumbColor: GBColors.success,
                              onChanged: (_) async {
                                await state.toggleProductStock(p.id);
                              },
                            ),
                          ],
                        ),
                      ),
                    );
                  },
                ),
        ),
      ],
    );
  }

  // =========================================================================
  // TAB 3: LEDGER — Bottom 3 per PDF Page 2
  // Daily/Weekly Sales Total, Platform Commission Deductions, Net Payout History to Bank
  // =========================================================================
  Widget _buildTab3Ledger(VendorAppState state, bool isHi, bool isDark) {
    final finances = state.finances;
    final todaySales = (finances?['today_sales'] as num?)?.toDouble() ?? 0.0;
    final weeklySales = (finances?['weekly_sales'] as num?)?.toDouble() ?? (todaySales * 5.2);
    final commissionDeductions = (finances?['commission_deductions'] as num?)?.toDouble() ?? 0.0;
    final netPayout = (finances?['net_payout'] as num?)?.toDouble() ?? (todaySales - commissionDeductions);

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Text(
          isHi ? 'दुकानदार बहीखाता एवं बैंक पेआउट' : 'Shopkeeper Ledger & Payouts',
          style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w900),
        ),
        const SizedBox(height: 6),
        Text(
          isHi ? 'दैनिक बिक्री, साप्ताहिक आय एवं बैंक निपटान इतिहास।' : 'Daily sales, weekly totals, and verified bank payouts.',
          style: const TextStyle(fontSize: 12, color: Colors.grey),
        ),
        const SizedBox(height: 16),

        // Financial Metrics Cards
        Row(
          children: [
            Expanded(
              child: _buildMetricTile(
                title: isHi ? 'आज की बिक्री' : 'Daily Sales',
                amount: '₹${todaySales.toStringAsFixed(0)}',
                color: GBColors.primary,
                icon: Icons.today_outlined,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _buildMetricTile(
                title: isHi ? 'साप्ताहिक बिक्री' : 'Weekly Sales',
                amount: '₹${weeklySales.toStringAsFixed(0)}',
                color: Colors.indigo,
                icon: Icons.calendar_view_week_outlined,
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),

        // Commission Deduction Tile (Highlighting 0% introductory rate)
        Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: Colors.green.withValues(alpha: 0.08),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: Colors.green.withValues(alpha: 0.3)),
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  const Icon(Icons.verified_outlined, color: Colors.green, size: 20),
                  const SizedBox(width: 8),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        isHi ? 'प्लेटफ़ॉर्म कमीशन कटौती (0%)' : 'Platform Commission Deductions (0%)',
                        style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
                      ),
                      Text(
                        isHi ? 'गाँव बाज़ार शून्य-कमीशन ग्रामीण नीति' : 'GaonBazaar 0% Rural Introductory Policy',
                        style: const TextStyle(fontSize: 11, color: Colors.grey),
                      ),
                    ],
                  ),
                ],
              ),
              Text(
                '₹${commissionDeductions.toStringAsFixed(0)}',
                style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.green, fontSize: 15),
              ),
            ],
          ),
        ),
        const SizedBox(height: 12),

        // Net Bank Payout
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            gradient: const LinearGradient(colors: [Color(0xFF1B5E20), Color(0xFF2E7D32)]),
            borderRadius: BorderRadius.circular(14),
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    isHi ? 'बैंक में शुद्ध देय पेआउट:' : 'Net Bank Payout Accrued:',
                    style: const TextStyle(color: Colors.white70, fontSize: 12),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    '₹${netPayout.toStringAsFixed(0)}',
                    style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w900, fontSize: 24),
                  ),
                ],
              ),
              ElevatedButton(
                style: ElevatedButton.styleFrom(backgroundColor: Colors.white, foregroundColor: GBColors.primary),
                onPressed: () => _showBankUpdateModal(state, isHi),
                child: Text(isHi ? 'बैंक खाता जांचें' : 'View Bank'),
              ),
            ],
          ),
        ),
        const SizedBox(height: 20),

        // Net Payout History to Bank
        Text(
          isHi ? 'बैंक पेआउट इतिहास' : 'Net Payout History to Bank',
          style: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 10),

        ...[
          {'date': '02 Nov 2026', 'amount': '₹1,450', 'status': 'SETTLED', 'ref': 'CMS_9823101'},
          {'date': '01 Nov 2026', 'amount': '₹2,100', 'status': 'SETTLED', 'ref': 'CMS_9812902'},
          {'date': '31 Oct 2026', 'amount': '₹1,850', 'status': 'SETTLED', 'ref': 'CMS_9798114'},
        ].map((h) => Card(
              margin: const EdgeInsets.only(bottom: 8),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
              child: ListTile(
                leading: const CircleAvatar(
                  backgroundColor: Color(0xFFE8F5E9),
                  child: Icon(Icons.account_balance, color: GBColors.primary, size: 20),
                ),
                title: Text(h['amount']!, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
                subtitle: Text('${h['date']} • Ref: ${h['ref']}'),
                trailing: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                  decoration: BoxDecoration(color: Colors.green.shade50, borderRadius: BorderRadius.circular(6)),
                  child: Text(
                    isHi ? 'सफल पेआउट' : 'SETTLED',
                    style: TextStyle(color: Colors.green.shade800, fontWeight: FontWeight.bold, fontSize: 11),
                  ),
                ),
              ),
            )),
      ],
    );
  }

  Widget _buildMetricTile({
    required String title,
    required String amount,
    required Color color,
    required IconData icon,
  }) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.08),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withValues(alpha: 0.2)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: color, size: 22),
          const SizedBox(height: 8),
          Text(title, style: const TextStyle(fontSize: 12, color: Colors.grey, fontWeight: FontWeight.w600)),
          const SizedBox(height: 4),
          Text(amount, style: TextStyle(fontWeight: FontWeight.w900, fontSize: 18, color: color)),
        ],
      ),
    );
  }

  // =========================================================================
  // TAB 4: PROFILE & SETTINGS — Bottom 4 (Right) per PDF Page 2
  // Header: Store Name & Owner Phone Number. Language Toggle (Hindi/English).
  // Bank Details (Update Flow): View saved bank + Update with OTP + 24-48hr cooldown.
  // Store Details: Edit operating hours, update landmark/location.
  // Support & Logout: Contact Admin/Support, and Logout button.
  // =========================================================================
  Widget _buildTab4ProfileSettings(VendorAppState state, bool isHi, bool isDark) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // Header: Store Name & Owner Phone Number (PDF Page 2)
        Card(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
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
                        style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 16),
                      ),
                      const SizedBox(height: 3),
                      Text(
                        state.currentUser?.name ?? state.myStore?.ownerName ?? (isHi ? 'दुकानदार' : 'Shopkeeper'),
                        style: const TextStyle(color: Colors.grey, fontSize: 13),
                      ),
                      Text(
                        state.currentUser?.phone ?? '',
                        style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12),
                      ),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: Colors.green.shade50,
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: Colors.green),
                  ),
                  child: Text(
                    isHi ? 'सत्यापित दुकान' : 'Verified Store',
                    style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Colors.green.shade800),
                  ),
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 16),

        // Language Toggle: Change app language (Hindi/English) (PDF Page 2)
        Card(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
          child: ListTile(
            leading: const Icon(Icons.language_outlined, color: GBColors.primary),
            title: Text(isHi ? 'भाषा बदलें' : 'Change Language', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
            subtitle: Text(isHi ? 'वर्तमान: हिंदी' : 'Current: English'),
            trailing: Switch(
              value: isHi,
              activeThumbColor: GBColors.primary,
              onChanged: (val) {
                state.setLocale(val ? 'hi' : 'en');
              },
            ),
          ),
        ),
        const SizedBox(height: 8),

        // Bank Details (Update Flow with OTP & 24-48h cooldown) (PDF Page 2)
        Card(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
          child: ListTile(
            leading: const Icon(Icons.account_balance_outlined, color: GBColors.primary),
            title: Text(isHi ? 'बैंक पेआउट विवरण एवं अपडेट' : 'Bank Details & Secure Update', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
            subtitle: Text(
              (state.linkedUpiId.isNotEmpty && state.linkedUpiId != 'NOT_CONFIGURED')
                  ? state.linkedUpiId
                  : (isHi ? 'बैंक खाता संबद्ध (₹1 पेनी ड्रॉप सत्यापित)' : 'Linked Bank Account (Verified)'),
              style: const TextStyle(fontSize: 12, color: Colors.grey),
            ),
            trailing: ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: GBColors.primary,
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                minimumSize: Size.zero,
              ),
              onPressed: () => _showBankUpdateModal(state, isHi),
              child: Text(isHi ? 'अपडेट' : 'Update', style: const TextStyle(fontSize: 12)),
            ),
          ),
        ),
        const SizedBox(height: 8),

        // Store Details: Edit operating hours, update landmark/location (PDF Page 2)
        Card(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
          child: ListTile(
            leading: const Icon(Icons.access_time_outlined, color: GBColors.primary),
            title: Text(isHi ? 'दुकान खुलने का समय' : 'Store Operating Hours', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
            subtitle: Text(isHi ? 'सुबह 7:00 बजे से रात 9:00 बजे' : 'Daily 7:00 AM - 9:00 PM'),
            trailing: const Icon(Icons.chevron_right, color: Colors.grey),
            onTap: () {
              Navigator.of(context).push(
                MaterialPageRoute(builder: (_) => const VendorOperatingHoursScreen()),
              );
            },
          ),
        ),
        const SizedBox(height: 8),

        Card(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
          child: ListTile(
            leading: const Icon(Icons.location_on_outlined, color: GBColors.primary),
            title: Text(isHi ? 'स्थान व लैंडमार्क अपडेट' : 'Landmark & Location Updates', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
            subtitle: Text('${state.myStore?.village ?? (isHi ? "स्थान दर्ज नहीं" : "No location set")}${state.myStore?.district != null && state.myStore!.district.isNotEmpty ? ", " + state.myStore!.district : ""}'),
            trailing: const Icon(Icons.chevron_right, color: Colors.grey),
            onTap: () {
              Navigator.of(context).push(
                MaterialPageRoute(builder: (_) => const VendorStoreLocationScreen()),
              );
            },
          ),
        ),
        const SizedBox(height: 8),

        // Support & Logout: Contact Admin/Support, and Logout button (PDF Page 2)
        Card(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
          child: ListTile(
            leading: const Icon(Icons.headset_mic_outlined, color: GBColors.primary),
            title: Text(isHi ? 'एडमिन / सहायता हेल्पलाइन' : 'Contact Admin / Support', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
            subtitle: const Text('+91 98000 00000'),
            trailing: const Icon(Icons.phone, color: GBColors.primary),
            onTap: () async {
              final uri = Uri.parse('tel:+919800000000');
              if (await canLaunchUrl(uri)) await launchUrl(uri);
            },
          ),
        ),
        const SizedBox(height: 20),

        ElevatedButton.icon(
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.red.shade700,
            minimumSize: const Size.fromHeight(48),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
          ),
          icon: const Icon(Icons.logout, color: Colors.white),
          label: Text(
            isHi ? 'लॉगआउट करें' : 'Logout',
            style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
          ),
          onPressed: () {
            showDialog(
              context: context,
              builder: (ctx) => AlertDialog(
                title: Text(isHi ? 'लॉगआउट की पुष्टि' : 'Confirm Logout'),
                content: Text(isHi ? 'क्या आप वाकई ऐप से बाहर निकलना चाहते हैं?' : 'Are you sure you want to logout?'),
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
      ],
    );
  }
}
