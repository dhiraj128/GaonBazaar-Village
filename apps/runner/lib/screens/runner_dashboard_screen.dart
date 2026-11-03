import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import 'package:shared_models/shared_models.dart';
import 'package:url_launcher/url_launcher.dart';
import '../state/runner_state.dart';
import 'runner_auth_screen.dart';
import 'runner_active_delivery_screen.dart';

class RunnerDashboardScreen extends StatefulWidget {
  const RunnerDashboardScreen({super.key});

  @override
  State<RunnerDashboardScreen> createState() => _RunnerDashboardScreenState();
}

class _RunnerDashboardScreenState extends State<RunnerDashboardScreen> {
  int _navIndex = 0;
  bool _isActing = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final state = RunnerStateProvider.of(context);
      state.fetchProfile();
      state.fetchJobs();
      state.fetchFinances();
      state.fetchNotifications();
    });
  }

  Future<void> _handleAction(
    RunnerAppState state,
    String orderId,
    String action, {
    String? otp,
  }) async {
    setState(() => _isActing = true);
    final res = await state.handleJobAction(orderId, action, deliveryOtp: otp);
    if (!mounted) return;
    setState(() => _isActing = false);

    final isHi = state.isHindi;
    final success = res['success'] == true;

    if (success) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            isHi
                ? 'कार्रवाई सफल रही: ${res['message'] ?? action}'
                : 'Action successful: ${res['message'] ?? action}',
          ),
          backgroundColor: GBColors.success,
        ),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(res['error']?.toString() ?? (isHi ? 'कार्रवाई विफल रही' : 'Action failed')),
          backgroundColor: GBColors.error,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = RunnerStateProvider.of(context);
    final isHi = state.isHindi;

    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              isHi ? 'गाँव बाज़ार डिलीवरी साथी' : 'GaonBazaar Runner',
              style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16),
            ),
            Text(
              state.runnerProfile?['village'] != null
                  ? '${state.runnerProfile!['village']}, ${state.runnerProfile!['district'] ?? ""}'
                  : (isHi ? 'डिलीवरी नेटवर्क' : 'Delivery Network'),
              style: const TextStyle(fontSize: 11, color: Colors.grey),
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
          // Duty Online / Offline switch
          Padding(
            padding: const EdgeInsets.only(right: 8),
            child: Row(
              children: [
                Text(
                  state.isOnline
                      ? (isHi ? 'ड्यूटी ऑन' : 'Online')
                      : (isHi ? 'ड्यूटी ऑफ' : 'Offline'),
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w700,
                    color: state.isOnline ? GBColors.success : GBColors.error,
                  ),
                ),
                Switch(
                  value: state.isOnline,
                  activeColor: GBColors.success,
                  onChanged: (v) async {
                    final err = await state.toggleDutyOnline();
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
          _buildJobsTab(state),
          _buildTripsTab(state),
          _buildEarningsTab(state),
          _buildAccountTab(state),
        ],
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _navIndex,
        onTap: (idx) => setState(() => _navIndex = idx),
        selectedItemColor: GBColors.primary,
        unselectedItemColor: Colors.grey,
        type: BottomNavigationBarType.fixed,
        items: [
          BottomNavigationBarItem(
            icon: const Icon(Icons.home_outlined),
            activeIcon: const Icon(Icons.home),
            label: isHi ? 'होम' : 'Home',
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.delivery_dining_outlined),
            activeIcon: const Icon(Icons.delivery_dining),
            label: isHi ? 'कार्य (Jobs)' : 'Jobs',
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.history_outlined),
            activeIcon: const Icon(Icons.history),
            label: isHi ? 'ट्रिप्स' : 'Trips',
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.account_balance_wallet_outlined),
            activeIcon: const Icon(Icons.account_balance_wallet),
            label: isHi ? 'कमाई' : 'Earnings',
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.person_outline),
            activeIcon: const Icon(Icons.person),
            label: isHi ? 'प्रोफ़ाइल' : 'Account',
          ),
        ],
      ),
    );
  }

  // ==========================================
  // TAB 0: HOME
  // ==========================================
  Widget _buildHomeTab(RunnerAppState state) {
    final isHi = state.isHindi;
    final activeMission = state.activeMission;

    return SafeArea(
      child: RefreshIndicator(
        onRefresh: () async {
          await state.fetchProfile();
          await state.fetchJobs();
          await state.fetchFinances();
        },
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // Approval Warning Banner
            if (!state.isApproved)
              Container(
                margin: const EdgeInsets.only(bottom: 14),
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                decoration: BoxDecoration(
                  color: Colors.amber.shade100,
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: Colors.amber.shade400),
                ),
                child: Row(
                  children: [
                    Icon(Icons.pending_actions, color: Colors.amber.shade900, size: 22),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Text(
                        isHi
                            ? 'आपकी प्रोफ़ाइल सत्यापन प्रक्रियाधीन है। सुपर एडमिन द्वारा अनुमोदन के बाद ही आप ऑनलाइन ड्यूटी पर जा सकेंगे।'
                            : 'Your profile is pending admin approval. You can go online once approved.',
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

            // Duty Status Bar
            Container(
              margin: const EdgeInsets.only(bottom: 14),
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
              decoration: BoxDecoration(
                color: state.isOnline ? GBColors.success.withValues(alpha: 0.08) : GBColors.error.withValues(alpha: 0.08),
                borderRadius: BorderRadius.circular(10),
                border: Border.all(
                  color: state.isOnline ? GBColors.success.withValues(alpha: 0.3) : GBColors.error.withValues(alpha: 0.3),
                ),
              ),
              child: Row(
                children: [
                  Icon(
                    state.isOnline ? Icons.check_circle : Icons.pause_circle,
                    size: 18,
                    color: state.isOnline ? GBColors.success : GBColors.error,
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      state.isOnline
                          ? (isHi ? 'ड्यूटी चालू है — नए ऑर्डर स्वीकार किए जा रहे हैं।' : 'Duty is Online — Accepting delivery tasks.')
                          : (isHi ? 'ड्यूटी बंद है — नए ऑर्डर प्राप्त करने के लिए स्विच ऑन करें।' : 'Duty is Offline — Toggle switch to go online.'),
                      style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w700,
                        color: state.isOnline ? GBColors.success : GBColors.error,
                      ),
                    ),
                  ),
                ],
              ),
            ),

            // Daily Earnings Gradient Card
            Container(
              padding: const EdgeInsets.all(18),
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [Color(0xFF2E7D32), Color(0xFF1B5E20)],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(16),
                boxShadow: [
                  BoxShadow(color: Colors.black.withValues(alpha: 0.12), blurRadius: 6, offset: const Offset(0, 2)),
                ],
              ),
              child: Column(
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            isHi ? 'आज की कुल डिलीवरी कमाई' : "Today's Delivery Earnings",
                            style: const TextStyle(color: Colors.white70, fontSize: 12),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            '₹${state.todayEarningsTotal.toStringAsFixed(0)}',
                            style: const TextStyle(color: Colors.white, fontSize: 32, fontWeight: FontWeight.w900),
                          ),
                        ],
                      ),
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.end,
                        children: [
                          Text(
                            isHi ? 'पूरी की गई ट्रिप' : 'Completed Trips',
                            style: const TextStyle(color: Colors.white70, fontSize: 12),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            '${state.completedTrips}',
                            style: const TextStyle(color: Colors.white, fontSize: 28, fontWeight: FontWeight.w900),
                          ),
                        ],
                      ),
                    ],
                  ),
                  const Divider(color: Colors.white24, height: 24),
                  Row(
                    children: [
                      const Icon(Icons.star, color: Colors.amber, size: 16),
                      const SizedBox(width: 4),
                      Text(
                        '⭐ 4.9 ${isHi ? "रेटिंग" : "Rating"}',
                        style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w700, fontSize: 12),
                      ),
                      const Spacer(),
                      Text(
                        isHi ? 'दैनिक बैंक/यूपीआई सेटलमेंट' : 'Daily Payout Settlement',
                        style: const TextStyle(color: Colors.lightGreenAccent, fontWeight: FontWeight.w700, fontSize: 12),
                      ),
                    ],
                  ),
                ],
              ),
            ),

            const SizedBox(height: 16),

            // Active Mission Section
            if (activeMission != null) ...[
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: GBColors.primary.withValues(alpha: 0.08),
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(color: GBColors.primary.withValues(alpha: 0.4), width: 1.5),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.all(8),
                          decoration: const BoxDecoration(
                            color: GBColors.primary,
                            shape: BoxShape.circle,
                          ),
                          child: const Icon(Icons.two_wheeler, color: Colors.white, size: 20),
                        ),
                        const SizedBox(width: 10),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                isHi ? 'सक्रिय डिलीवरी मिशन प्रगति पर है' : 'Active Delivery Mission in Progress',
                                style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 14, color: GBColors.primary),
                              ),
                              Text(
                                '#${activeMission.id.length > 8 ? activeMission.id.substring(0, 8) : activeMission.id}',
                                style: const TextStyle(fontSize: 11, color: Colors.grey),
                              ),
                            ],
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                          decoration: BoxDecoration(
                            color: GBColors.primary,
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: Text(
                            '₹${(activeMission.runnerPayout ?? activeMission.deliveryFee).toStringAsFixed(0)}',
                            style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w800, fontSize: 13),
                          ),
                        ),
                      ],
                    ),
                    const Divider(height: 20),
                    Row(
                      children: [
                        const Icon(Icons.storefront, size: 16, color: Colors.grey),
                        const SizedBox(width: 6),
                        Expanded(
                          child: Text(
                            activeMission.storeName,
                            style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 6),
                    Row(
                      children: [
                        const Icon(Icons.location_on, size: 16, color: Colors.grey),
                        const SizedBox(width: 6),
                        Expanded(
                          child: Text(
                            activeMission.deliveryAddress,
                            style: const TextStyle(fontSize: 12, color: Colors.grey),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 14),
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton.icon(
                        style: ElevatedButton.styleFrom(
                          backgroundColor: GBColors.primary,
                          padding: const EdgeInsets.symmetric(vertical: 12),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                        ),
                        icon: const Icon(Icons.navigation, color: Colors.white, size: 18),
                        label: Text(
                          isHi ? 'डिलीवरी प्रबंधन खोलें (Active Mission)' : 'Manage Delivery Workflow',
                          style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 14, color: Colors.white),
                        ),
                        onPressed: () {
                          Navigator.of(context).push(
                            MaterialPageRoute(
                              builder: (_) => RunnerActiveDeliveryScreen(order: activeMission),
                            ),
                          );
                        },
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),
            ] else ...[
              // Clean Empty Mission Banner (NO fake orders!)
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: Theme.of(context).cardColor,
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(color: Colors.grey.shade300),
                ),
                child: Column(
                  children: [
                    Icon(
                      state.isOnline ? Icons.two_wheeler : Icons.pause_circle_outline,
                      size: 40,
                      color: state.isOnline ? GBColors.primary : Colors.grey,
                    ),
                    const SizedBox(height: 10),
                    Text(
                      state.isOnline
                          ? (isHi ? 'ड्यूटी चालू है — नए ऑर्डर की प्रतीक्षा की जा रही है' : 'You are Online — Waiting for new orders')
                          : (isHi ? 'ड्यूटी बंद है' : 'You are Offline'),
                      textAlign: TextAlign.center,
                      style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 14),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      state.isOnline
                          ? (isHi
                              ? 'जैसे ही आस-पास की किराना दुकान ऑर्डर तैयार करेगी, आपको असाइनमेंट सूचना प्राप्त होगी।'
                              : 'Orders from nearby village shops will appear in the Jobs tab once packed.')
                          : (isHi ? 'ऑर्डर प्राप्त करने के लिए ऊपर दाईं ओर स्विच ऑन करें।' : 'Toggle the duty switch above to start receiving tasks.'),
                      textAlign: TextAlign.center,
                      style: const TextStyle(fontSize: 12, color: Colors.grey),
                    ),
                    if (state.isOnline) ...[
                      const SizedBox(height: 12),
                      OutlinedButton.icon(
                        onPressed: () => state.fetchJobs(),
                        icon: const Icon(Icons.refresh, size: 16),
                        label: Text(isHi ? 'ताज़ा करें' : 'Refresh Jobs'),
                      ),
                    ],
                  ],
                ),
              ),
              const SizedBox(height: 16),
            ],

            // 5-Tier Distance Payouts Guide
            Card(
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        const Icon(Icons.timeline, color: GBColors.primary, size: 20),
                        const SizedBox(width: 8),
                        Text(
                          isHi ? 'पारदर्शी 5-स्तरीय दूरी पेआउट दरें' : '5-Tier Distance Delivery Payouts',
                          style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 14),
                        ),
                      ],
                    ),
                    const Divider(height: 20),
                    _buildTierRow('0 - 1.0 km', '₹10.00', isHi ? 'गाँव आंतरिक' : 'Intra-village'),
                    _buildTierRow('1.0 - 2.0 km', '₹14.00', isHi ? 'निकटवर्ती टोला' : 'Nearby Tola'),
                    _buildTierRow('2.0 - 4.0 km', '₹18.00', isHi ? 'पड़ोसी गाँव' : 'Neighboring village'),
                    _buildTierRow('4.0 - 6.0 km', '₹22.00', isHi ? 'ब्लॉक क्लस्टर' : 'Block cluster'),
                    _buildTierRow('6.0 - 8.0 km', '₹28.00', isHi ? 'अधिकतम पायलट सीमा' : 'Max pilot boundary'),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTierRow(String distance, String payout, String note) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(distance, style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 12)),
          Text(note, style: const TextStyle(fontSize: 11, color: Colors.grey)),
          Text(payout, style: const TextStyle(fontWeight: FontWeight.w800, color: GBColors.primary, fontSize: 13)),
        ],
      ),
    );
  }

  // ==========================================
  // TAB 1: JOBS (Available & Actionable)
  // ==========================================
  Widget _buildJobsTab(RunnerAppState state) {
    final isHi = state.isHindi;
    final availableJobs = state.availableJobs;

    return SafeArea(
      child: RefreshIndicator(
        onRefresh: () async {
          await state.fetchJobs();
        },
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  isHi ? 'उपलब्ध डिलीवरी कार्य' : 'Available Delivery Jobs',
                  style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16),
                ),
                IconButton(
                  icon: const Icon(Icons.refresh, size: 20),
                  onPressed: () => state.fetchJobs(),
                ),
              ],
            ),
            const SizedBox(height: 12),
            if (availableJobs.isEmpty)
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 40),
                decoration: BoxDecoration(
                  color: Theme.of(context).cardColor,
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(color: Colors.grey.shade300),
                ),
                child: Center(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(Icons.inbox_outlined, size: 48, color: Colors.grey.shade400),
                      const SizedBox(height: 12),
                      Text(
                        isHi ? 'वर्तमान में कोई नया डिलीवरी कार्य उपलब्ध नहीं है' : 'No Delivery Jobs Available',
                        style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 15),
                      ),
                      const SizedBox(height: 6),
                      Text(
                        isHi
                            ? 'जैसे ही किराना दुकानदार नया ऑर्डर पैक करेंगे, कार्य यहाँ दिखाई देगा।'
                            : 'Jobs will appear here once local shopkeepers pack customer orders.',
                        textAlign: TextAlign.center,
                        style: const TextStyle(fontSize: 12, color: Colors.grey),
                      ),
                    ],
                  ),
                ),
              )
            else
              ...availableJobs.map((order) => _buildAvailableJobCard(state, order)),
          ],
        ),
      ),
    );
  }

  Widget _buildAvailableJobCard(RunnerAppState state, GBOrder order) {
    final isHi = state.isHindi;
    final displayId = order.id.length > 8 ? order.id.substring(0, 8) : order.id;
    final isCod = order.paymentMethod.toUpperCase() == 'COD';
    final payout = order.runnerPayout ?? order.deliveryFee;

    return Card(
      margin: const EdgeInsets.only(bottom: 14),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('#$displayId', style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 14)),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: GBColors.primary.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(6),
                  ),
                  child: Text(
                    '${isHi ? "पेआउट" : "Payout"}: ₹${payout.toStringAsFixed(0)}',
                    style: const TextStyle(fontWeight: FontWeight.w800, color: GBColors.primary, fontSize: 12),
                  ),
                ),
              ],
            ),
            const Divider(height: 16),
            Row(
              children: [
                const Icon(Icons.storefront, size: 16, color: GBColors.primary),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    order.storeName,
                    style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 6),
            Row(
              children: [
                const Icon(Icons.location_on, size: 16, color: GBColors.secondary),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    order.deliveryAddress,
                    style: const TextStyle(fontSize: 12, color: Colors.grey),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color: isCod ? Colors.red.withValues(alpha: 0.1) : Colors.green.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    isCod ? 'COD (नकद)' : 'PREPAID',
                    style: TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.w700,
                      color: isCod ? Colors.red : Colors.green,
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                Text(
                  '${order.items.length} ${isHi ? "सामग्री" : "items"}',
                  style: const TextStyle(fontSize: 12, color: Colors.grey),
                ),
                if (order.distanceKm != null) ...[
                  const SizedBox(width: 8),
                  Text(
                    '• ${order.distanceKm!.toStringAsFixed(1)} km',
                    style: const TextStyle(fontSize: 12, color: Colors.grey, fontWeight: FontWeight.w600),
                  ),
                ],
              ],
            ),
            const SizedBox(height: 12),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                style: ElevatedButton.styleFrom(
                  backgroundColor: GBColors.primary,
                  padding: const EdgeInsets.symmetric(vertical: 10),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                ),
                onPressed: _isActing ? null : () => _handleAction(state, order.id, 'ACCEPT'),
                child: Text(
                  isHi ? 'डिलीवरी स्वीकार करें' : 'Accept Delivery Mission',
                  style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 13, color: Colors.white),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  // ==========================================
  // TAB 2: TRIPS HISTORY (Zero Fake Data)
  // ==========================================
  Widget _buildTripsTab(RunnerAppState state) {
    final isHi = state.isHindi;
    final trips = state.trips;

    return SafeArea(
      child: RefreshIndicator(
        onRefresh: () async {
          await state.fetchFinances();
        },
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  isHi ? 'पूर्ण की गई ट्रिप्स' : 'Completed Delivery Trips',
                  style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16),
                ),
                Text(
                  '${trips.length} ${isHi ? "कुल ट्रिप" : "Trips"}',
                  style: const TextStyle(color: Colors.grey, fontSize: 12, fontWeight: FontWeight.w600),
                ),
              ],
            ),
            const SizedBox(height: 12),
            if (trips.isEmpty)
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 40),
                decoration: BoxDecoration(
                  color: Theme.of(context).cardColor,
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(color: Colors.grey.shade300),
                ),
                child: Center(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(Icons.history_outlined, size: 48, color: Colors.grey.shade400),
                      const SizedBox(height: 12),
                      Text(
                        isHi ? 'अभी तक कोई पूर्ण ट्रिप दर्ज नहीं हुई है' : 'No Completed Trips Yet',
                        style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 15),
                      ),
                      const SizedBox(height: 6),
                      Text(
                        isHi
                            ? 'आपके द्वारा सफलतापूर्वक डिलीवर की गई सभी ट्रिप्स और उनकी कमाई यहाँ प्रदर्शित होंगी।'
                            : 'All successfully delivered orders and their verified payouts will appear here.',
                        textAlign: TextAlign.center,
                        style: const TextStyle(fontSize: 12, color: Colors.grey),
                      ),
                    ],
                  ),
                ),
              )
            else
              ...trips.map((trip) => _buildRealTripCard(trip, isHi)),
          ],
        ),
      ),
    );
  }

  Widget _buildRealTripCard(Map<String, dynamic> trip, bool isHi) {
    final orderId = (trip['order_id'] as String?) ?? '';
    final displayId = orderId.length > 8 ? orderId.substring(0, 8) : orderId;
    final storeName = (trip['store_name'] as String?) ?? (isHi ? 'किराना दुकान' : 'Store');
    final customerAddress = (trip['customer_address'] as String?) ?? '';
    final distanceKm = trip['distance_km'] != null ? '${trip['distance_km']} km' : '1.5 km';
    final payout = (trip['payout'] as num?)?.toDouble() ?? (trip['delivery_fee'] as num?)?.toDouble() ?? 14.0;
    final isCod = trip['payment_method'] == 'COD';
    final deliveredAt = (trip['delivered_at'] as String?) ?? '';

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('#$displayId', style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 13)),
                Text(
                  '₹${payout.toStringAsFixed(0)}',
                  style: const TextStyle(fontWeight: FontWeight.w900, color: GBColors.primary, fontSize: 14),
                ),
              ],
            ),
            const SizedBox(height: 6),
            Text(storeName, style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13)),
            if (customerAddress.isNotEmpty)
              Text(customerAddress, style: const TextStyle(fontSize: 12, color: Colors.grey)),
            const Divider(height: 16),
            Row(
              children: [
                Text('${isHi ? "दूरी" : "Distance"}: $distanceKm', style: const TextStyle(fontSize: 11, color: Colors.grey)),
                const SizedBox(width: 10),
                if (deliveredAt.isNotEmpty)
                  Text(
                    deliveredAt.length > 10 ? deliveredAt.substring(0, 10) : deliveredAt,
                    style: const TextStyle(fontSize: 11, color: Colors.grey),
                  ),
                const Spacer(),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color: isCod ? Colors.red.withValues(alpha: 0.1) : Colors.green.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    isCod ? 'COD' : 'PREPAID',
                    style: TextStyle(
                      fontSize: 10,
                      fontWeight: FontWeight.w700,
                      color: isCod ? Colors.red : Colors.green,
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  // ==========================================
  // TAB 3: EARNINGS & REMITTANCE (Zero Multiplier)
  // ==========================================
  Widget _buildEarningsTab(RunnerAppState state) {
    final isHi = state.isHindi;

    return SafeArea(
      child: RefreshIndicator(
        onRefresh: () async {
          await state.fetchFinances();
        },
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // Weekly / Total Ledger
            Card(
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          isHi ? 'इस सप्ताह की कुल डिलीवरी कमाई' : 'Weekly Delivery Earnings',
                          style: const TextStyle(color: Colors.grey, fontSize: 13, fontWeight: FontWeight.w600),
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                          decoration: BoxDecoration(
                            color: GBColors.primary.withValues(alpha: 0.1),
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: Text(
                            isHi ? 'T+1 स्वचालित' : 'Auto T+1',
                            style: const TextStyle(color: GBColors.primary, fontSize: 11, fontWeight: FontWeight.bold),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Text(
                      '₹${state.weeklyEarnings.toStringAsFixed(0)}',
                      style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 32, color: GBColors.primary),
                    ),
                    const Divider(height: 24),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(isHi ? 'आज की कमाई:' : "Today's Earnings:", style: const TextStyle(fontSize: 13, color: Colors.grey)),
                        Text('₹${state.todayEarningsTotal.toStringAsFixed(0)}', style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 14)),
                      ],
                    ),
                    const SizedBox(height: 6),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(isHi ? 'कुल संचयी कमाई:' : 'Total Lifetime Earnings:', style: const TextStyle(fontSize: 13, color: Colors.grey)),
                        Text('₹${state.totalDeliveryEarnings.toStringAsFixed(0)}', style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 14)),
                      ],
                    ),
                    const Divider(height: 24),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(isHi ? 'जुड़ी यूपीआई आईडी:' : 'Linked UPI ID:', style: const TextStyle(fontSize: 13, color: Colors.grey)),
                        Text(
                          state.linkedUpiId.isNotEmpty ? state.linkedUpiId : (isHi ? 'दर्ज नहीं' : 'Not linked'),
                          style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 13),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 14),

            // COD Remittance Tracker
            Card(
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        const Icon(Icons.payments_outlined, color: Colors.red, size: 22),
                        const SizedBox(width: 8),
                        Text(
                          isHi ? 'सीओडी नकद संग्रह व जमा' : 'COD Cash Remittance',
                          style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 14),
                        ),
                      ],
                    ),
                    const Divider(height: 20),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(isHi ? 'वर्तमान नकद दायित्व (Cash in Hand):' : 'Current Cash in Hand:', style: const TextStyle(fontSize: 13)),
                        Text(
                          '₹${state.cashCollectedToRemit.toStringAsFixed(0)}',
                          style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 18, color: Colors.red),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Text(
                      isHi
                          ? 'ग्राहकों से प्राप्त सभी सीओडी राशि उसी दिन हब में जमा या सिस्टम में सेटल करना अनिवार्य है।'
                          : 'All COD cash collected from customers must be reconciled and remitted daily.',
                      style: const TextStyle(fontSize: 11, color: Colors.grey),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  // ==========================================
  // TAB 4: ACCOUNT / PROFILE
  // ==========================================
  Widget _buildAccountTab(RunnerAppState state) {
    final isHi = state.isHindi;

    return SafeArea(
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Profile Header
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [Color(0xFF1B5E20), Color(0xFF2E7D32)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(16),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Container(
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(
                        color: Colors.white.withValues(alpha: 0.2),
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(Icons.two_wheeler, color: Colors.white, size: 28),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                      decoration: BoxDecoration(
                        color: Colors.white.withValues(alpha: 0.25),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: const Row(
                        children: [
                          Icon(Icons.star, color: Colors.amber, size: 16),
                          SizedBox(width: 4),
                          Text('4.9', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13)),
                        ],
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                Text(
                  state.runnerProfile?['full_name'] as String? ?? state.currentUser?.name ?? (isHi ? 'डिलीवरी साथी' : 'Delivery Partner'),
                  style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w800, fontSize: 18),
                ),
                const SizedBox(height: 4),
                Text(
                  '${isHi ? "वाहन" : "Vehicle"}: ${state.runnerProfile?["vehicle_type"] ?? "Motorcycle / Cycle"} (${state.runnerProfile?["vehicle_number"] ?? "Registered"})',
                  style: const TextStyle(color: Colors.white70, fontSize: 13),
                ),
                const Divider(color: Colors.white24, height: 24),
                Row(
                  children: [
                    Text(
                      state.isApproved
                          ? (isHi ? '✓ सत्यापित साथी' : '✓ Verified Partner')
                          : (isHi ? 'सत्यापन प्रक्रियाधीन' : 'Pending Verification'),
                      style: TextStyle(
                        color: state.isApproved ? Colors.lightGreenAccent : Colors.amberAccent,
                        fontWeight: FontWeight.bold,
                        fontSize: 12,
                      ),
                    ),
                    const Spacer(),
                    Text(
                      state.runnerProfile?['block'] != null
                          ? '${state.runnerProfile!['block']} Cluster'
                          : (isHi ? 'पायलट ज़ोन' : 'Pilot Zone'),
                      style: const TextStyle(color: Colors.white70, fontSize: 12),
                    ),
                  ],
                ),
              ],
            ),
          ),

          const SizedBox(height: 16),

          // Support & Emergency
          Card(
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            child: Column(
              children: [
                ListTile(
                  leading: const Icon(Icons.emergency, color: Colors.red),
                  title: Text(isHi ? 'आपातकालीन सहायता हेल्पलाइन' : 'Emergency Partner Support'),
                  subtitle: const Text('+91 98000 00000'),
                  trailing: const Icon(Icons.phone, color: Colors.red),
                  onTap: () async {
                    final uri = Uri.parse('tel:9800000000');
                    if (await canLaunchUrl(uri)) await launchUrl(uri);
                  },
                ),
              ],
            ),
          ),

          const SizedBox(height: 14),

          // Settings: Language & Theme
          Card(
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            child: Column(
              children: [
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
                const Divider(height: 1),
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
              ],
            ),
          ),

          const SizedBox(height: 20),

          // Logout Button
          OutlinedButton.icon(
            style: OutlinedButton.styleFrom(
              foregroundColor: GBColors.error,
              side: const BorderSide(color: GBColors.error),
              padding: const EdgeInsets.symmetric(vertical: 12),
            ),
            icon: const Icon(Icons.logout),
            label: Text(
              isHi ? 'खाते से लॉग आउट करें' : 'Log Out Account',
              style: const TextStyle(fontWeight: FontWeight.w800),
            ),
            onPressed: () {
              state.logout();
              Navigator.of(context).pushAndRemoveUntil(
                MaterialPageRoute(builder: (_) => const RunnerAuthScreen()),
                (r) => false,
              );
            },
          ),
          const SizedBox(height: 24),
        ],
      ),
    );
  }
}
