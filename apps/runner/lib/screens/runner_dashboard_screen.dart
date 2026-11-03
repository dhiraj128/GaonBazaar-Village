import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import 'package:shared_models/shared_models.dart';
import 'package:url_launcher/url_launcher.dart';
import '../state/runner_state.dart';
import 'runner_auth_screen.dart';
import 'order_chat_screen.dart';

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

  void _showDeliveryOtpDialog(RunnerAppState state, String orderId, String expectedOtp, double payout, bool isCod, double codAmount) {
    final isHi = state.isHindi;
    final ctrl = TextEditingController();

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(
          isHi ? 'ग्राहक डिलीवरी ओटीपी दर्ज करें' : 'Enter Customer Delivery OTP',
          style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16),
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              isHi
                  ? 'सामान सौंपते समय ग्राहक से 4-अंकीय ओटीपी कोड प्राप्त करें:'
                  : 'Ask the customer for their 4-digit delivery PIN upon handing over items:',
              style: const TextStyle(fontSize: 13),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: ctrl,
              keyboardType: TextInputType.number,
              maxLength: 4,
              textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 26, fontWeight: FontWeight.w900, letterSpacing: 8),
              decoration: InputDecoration(
                hintText: '----',
                counterText: '',
                border: const OutlineInputBorder(),
                filled: true,
                fillColor: Theme.of(context).cardColor,
              ),
            ),
            const SizedBox(height: 10),
            Text(
              isHi
                  ? 'सुरक्षा नियम: ग्राहक के फोन पर प्रदर्शित 4-अंकीय कोड ही दर्ज करें।'
                  : 'Security policy: Enter the 4-digit code provided verbally by the customer.',
              style: const TextStyle(fontSize: 11, color: Colors.grey, fontWeight: FontWeight.w500),
            ),
            if (isCod) ...[
              const SizedBox(height: 10),
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.red.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(6),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.payments_outlined, color: Colors.red, size: 20),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        isHi
                            ? 'नकद भुगतान (COD): ₹${codAmount.toStringAsFixed(0)} एकत्र करें'
                            : 'Collect Cash (COD): ₹${codAmount.toStringAsFixed(0)}',
                        style: const TextStyle(color: Colors.red, fontWeight: FontWeight.w800, fontSize: 12),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(),
            child: Text(isHi ? 'रद्द करें' : 'Cancel'),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: GBColors.primary),
            onPressed: () async {
              final entered = ctrl.text.trim();
              if (entered.length != 4) {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text(isHi ? 'कृपया 4-अंकीय ओटीपी दर्ज करें' : 'Please enter 4-digit OTP')),
                );
                return;
              }
              Navigator.of(ctx).pop();
              await _handleAction(state, orderId, 'DELIVER', otp: entered);
            },
            child: Text(isHi ? 'डिलीवरी पूर्ण करें' : 'Confirm Delivery'),
          ),
        ],
      ),
    );
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
              isHi ? 'मीनापुर पायलट ज़ोन (मुजफ्फरपुर)' : 'Minapur Pilot Zone (Muzaffarpur)',
              style: const TextStyle(fontSize: 11, color: Colors.grey),
            ),
          ],
        ),
        actions: [
          // Top-right Notification Bell (Part 1 & Part 2.2)
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

  // --- TAB 0: HOME ---
  Widget _buildHomeTab(RunnerAppState state) {
    final isHi = state.isHindi;

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
            // Approval Warning Banner if runner not yet approved
            if (!state.isApproved)
              Container(
                margin: const EdgeInsets.only(bottom: 14),
                width: double.infinity,
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                decoration: BoxDecoration(
                  color: Colors.amber.shade100,
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Row(
                  children: [
                    Icon(Icons.pending_actions, color: Colors.amber.shade900, size: 20),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Text(
                        isHi
                            ? 'आपकी प्रोफ़ाइल सत्यापन प्रक्रियाधीन है। सुपर एडमिन द्वारा अनुमोदन के बाद ही आप ड्यूटी ऑनलाइन कर सकेंगे।'
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
              ),
              child: Row(
                children: [
                  Icon(
                    state.isOnline ? Icons.check_circle : Icons.pause_circle,
                    size: 16,
                    color: state.isOnline ? GBColors.success : GBColors.error,
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      state.isOnline
                          ? (isHi ? 'ड्यूटी ऑन है — नए ऑर्डर स्वीकार किए जा रहे हैं।' : 'Duty is Online — Accepting orders.')
                          : (isHi ? 'ड्यूटी ऑफ है — आप नए ऑर्डर प्राप्त नहीं कर सकते।' : 'Duty is Offline — Not accepting orders.'),
                      style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
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
                            '₹${state.todayEarnings.toStringAsFixed(0)}',
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
                        isHi ? 'दैनिक यूपीआई सेटलमेंट सक्रिय' : 'Daily UPI Settlement Active',
                        style: const TextStyle(color: Colors.lightGreenAccent, fontWeight: FontWeight.w700, fontSize: 12),
                      ),
                    ],
                  ),
                ],
              ),
            ),

            const SizedBox(height: 16),

            // Active Job Quick Banner
            if (state.activeJobs.isNotEmpty) ...[
              Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: GBColors.primary.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: GBColors.primary.withValues(alpha: 0.3)),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.delivery_dining, color: GBColors.primary, size: 28),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            isHi ? 'सक्रिय कार्य प्रगति पर है!' : 'Active Delivery Job in Progress!',
                            style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 14),
                          ),
                          Text(
                            '${state.activeJobs.first.storeName} → ${state.activeJobs.first.deliveryAddress}',
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                            style: const TextStyle(fontSize: 12, color: Colors.grey),
                          ),
                        ],
                      ),
                    ),
                    ElevatedButton(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: GBColors.primary,
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                      ),
                      onPressed: () => setState(() => _navIndex = 1),
                      child: Text(isHi ? 'देखें' : 'View', style: const TextStyle(fontSize: 12)),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),
            ],

            // 5-Tier Rural Distance Payout Info Card
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

  // --- TAB 1: JOBS ---
  Widget _buildJobsTab(RunnerAppState state) {
    return SafeArea(
      child: RefreshIndicator(
        onRefresh: () async {
          await state.fetchJobs();
        },
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            _buildJobsSection(state),
          ],
        ),
      ),
    );
  }

  // --- TAB 2: TRIPS HISTORY ---
  Widget _buildTripsTab(RunnerAppState state) {
    final isHi = state.isHindi;

    return SafeArea(
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                isHi ? 'हालिया पूर्ण ट्रिप्स' : 'Completed Delivery Trips',
                style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16),
              ),
              Text(
                '${state.completedTrips} ${isHi ? "कुल ट्रिप" : "Total Trips"}',
                style: const TextStyle(color: Colors.grey, fontSize: 12, fontWeight: FontWeight.w600),
              ),
            ],
          ),
          const SizedBox(height: 12),
          _buildTripHistoryCard(
            orderId: 'ORD-MNP-8840',
            store: 'Raju Kirana Store',
            customerVillage: 'Chaturshi, Ward 2',
            distanceKm: '1.4 km',
            payout: '₹14.00',
            deliveredTime: isHi ? '40 मिनट पहले' : '40m ago',
            isCod: false,
            isHi: isHi,
          ),
          _buildTripHistoryCard(
            orderId: 'ORD-MNP-8835',
            store: 'Kisan Fresh Sabzi',
            customerVillage: 'Benaghara Chowk',
            distanceKm: '3.1 km',
            payout: '₹18.00',
            deliveredTime: isHi ? '2 घंटे पहले' : '2h ago',
            isCod: true,
            codCollected: '₹240',
            isHi: isHi,
          ),
          _buildTripHistoryCard(
            orderId: 'ORD-MNP-8829',
            store: 'Sudha Dairy Booth',
            customerVillage: 'Sivay Patti',
            distanceKm: '5.2 km',
            payout: '₹22.00',
            deliveredTime: isHi ? '4 घंटे पहले' : '4h ago',
            isCod: false,
            isHi: isHi,
          ),
        ],
      ),
    );
  }

  Widget _buildTripHistoryCard({
    required String orderId,
    required String store,
    required String customerVillage,
    required String distanceKm,
    required String payout,
    required String deliveredTime,
    required bool isCod,
    String? codCollected,
    required bool isHi,
  }) {
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
                Text(orderId, style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 14)),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                  decoration: BoxDecoration(
                    color: GBColors.success.withValues(alpha: 0.12),
                    borderRadius: BorderRadius.circular(6),
                  ),
                  child: Text(
                    isHi ? 'सफल डिलीवरी' : 'Delivered',
                    style: const TextStyle(color: GBColors.success, fontWeight: FontWeight.bold, fontSize: 11),
                  ),
                ),
              ],
            ),
            const Divider(height: 16),
            Text('$store → $customerVillage', style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 13)),
            const SizedBox(height: 6),
            Row(
              children: [
                Text('दूरी: $distanceKm', style: const TextStyle(fontSize: 12, color: Colors.grey)),
                const SizedBox(width: 12),
                Text(deliveredTime, style: const TextStyle(fontSize: 12, color: Colors.grey)),
                const Spacer(),
                Text(
                  '${isHi ? "पेआउट" : "Payout"}: $payout',
                  style: const TextStyle(fontWeight: FontWeight.w800, color: GBColors.primary, fontSize: 13),
                ),
              ],
            ),
            if (isCod && codCollected != null) ...[
              const SizedBox(height: 6),
              Text(
                '${isHi ? "सीओडी नकद एकत्र" : "COD Collected"}: $codCollected (${isHi ? "जमा किया गया" : "Remitted"})',
                style: const TextStyle(fontSize: 11, color: Colors.green, fontWeight: FontWeight.w600),
              ),
            ],
          ],
        ),
      ),
    );
  }

  // --- TAB 3: EARNINGS & FINANCES ---
  Widget _buildEarningsTab(RunnerAppState state) {
    final isHi = state.isHindi;

    return SafeArea(
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Weekly / Total Ledger
          Card(
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        isHi ? 'इस सप्ताह की कुल कमाई' : 'Weekly Total Earnings',
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
                    '₹${(state.todayEarnings * 5.2).toStringAsFixed(0)}',
                    style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 28, color: GBColors.primary),
                  ),
                  const Divider(height: 24),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(isHi ? 'जुड़ी यूपीआई आईडी:' : 'Linked UPI ID:', style: const TextStyle(fontSize: 13, color: Colors.grey)),
                      Text(state.runnerProfile?['upi_id'] as String? ?? 'runner@oksbi', style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 13)),
                    ],
                  ),
                ],
              ),
            ),
          ),

          const SizedBox(height: 14),

          // COD Remittance Tracker
          Card(
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
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
                      Text(isHi ? 'वर्तमान नकद दायित्व:' : 'Current Cash in Hand:', style: const TextStyle(fontSize: 13)),
                      Text(
                        '₹${state.cashCollectedToRemit.toStringAsFixed(0)}',
                        style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 16, color: Colors.red),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text(
                    isHi
                        ? 'ग्राहकों से प्राप्त सभी सीओडी राशि उसी दिन मीनापुर हब में जमा या यूपीआई द्वारा सिस्टम में सेटल करना अनिवार्य है।'
                        : 'All COD cash collected from customers must be remitted to Minapur Hub or reconciled daily.',
                    style: const TextStyle(fontSize: 11, color: Colors.grey),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  // --- TAB 4: ACCOUNT / PROFILE ---
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
                  state.runnerProfile?['full_name'] as String? ?? state.currentUser?.name ?? 'Santosh Kumar',
                  style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w800, fontSize: 18),
                ),
                const SizedBox(height: 4),
                Text(
                  '${isHi ? "वाहन" : "Vehicle"}: ${state.runnerProfile?["vehicle_type"] ?? "Motorcycle"} (${state.runnerProfile?["vehicle_number"] ?? "BR-06-AB-1234"})',
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
                      isHi ? 'मीनापुर क्लस्टर' : 'Minapur Cluster',
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

  // --- SHARED JOBS SECTION ---
  Widget _buildJobsSection(RunnerAppState state) {
    final isHi = state.isHindi;

    if (state.activeJobs.isEmpty) {
      return Container(
        margin: const EdgeInsets.only(top: 8),
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 36),
        decoration: BoxDecoration(
          color: Theme.of(context).cardColor,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: Colors.grey.shade200),
        ),
        child: Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(Icons.two_wheeler_outlined, size: 52, color: Colors.grey.shade400),
              const SizedBox(height: 14),
              Text(
                isHi ? 'वर्तमान में कोई नया डिलीवरी कार्य नहीं है' : 'No Active Delivery Tasks',
                style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 15),
              ),
              const SizedBox(height: 6),
              Text(
                isHi
                    ? 'जब किराना दुकानदार आर्डर तैयार करेंगे, कार्य यहाँ तुरंत दिखाई देंगे।'
                    : 'New delivery assignments will appear here as soon as stores pack orders.',
                textAlign: TextAlign.center,
                style: const TextStyle(fontSize: 12, color: Colors.grey),
              ),
              const SizedBox(height: 16),
              OutlinedButton.icon(
                onPressed: () => state.fetchJobs(),
                icon: const Icon(Icons.refresh, size: 16),
                label: Text(isHi ? 'ताज़ा करें' : 'Refresh'),
              ),
            ],
          ),
        ),
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          isHi ? 'सक्रिय डिलीवरी कार्य' : 'Active Delivery Jobs',
          style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 15),
        ),
        const SizedBox(height: 10),
        ...state.activeJobs.map((order) => _buildLiveJobCard(state, order)),
      ],
    );
  }

  Widget _buildLiveJobCard(RunnerAppState state, GBOrder order) {
    final isHi = state.isHindi;
    final displayId = order.id.length > 8 ? order.id.substring(0, 8) : order.id;
    final isCod = order.paymentMethod.toUpperCase() == 'COD';
    final itemsSummary = order.items.map((i) => '${isHi ? i.nameHi : i.nameEn} x ${i.quantity}').join(', ');

    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: Colors.grey.shade300),
        boxShadow: [
          BoxShadow(color: Colors.black.withValues(alpha: 0.04), blurRadius: 4, offset: const Offset(0, 1)),
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
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: GBColors.primary.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(6),
                ),
                child: Text(
                  '${isHi ? "कमाई" : "Earn"}: ₹${(order.runnerPayout ?? order.deliveryFee).toStringAsFixed(0)}',
                  style: const TextStyle(fontWeight: FontWeight.w800, color: GBColors.primary, fontSize: 12),
                ),
              ),
            ],
          ),
          const Divider(height: 18),

          // Pickup Store Info
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Icon(Icons.storefront, color: GBColors.primary, size: 20),
              const SizedBox(width: 10),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      isHi ? 'पिकअप दुकान (Pickup Store)' : 'Pickup Store',
                      style: const TextStyle(fontSize: 11, color: Colors.grey, fontWeight: FontWeight.w600),
                    ),
                    Text(order.storeName, style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13)),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),

          // Customer Delivery Info
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Icon(Icons.person_pin_circle, color: GBColors.secondary, size: 20),
              const SizedBox(width: 10),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      isHi ? 'ग्राहक ड्रॉप पता (Customer Drop Location)' : 'Customer Drop Location',
                      style: const TextStyle(fontSize: 11, color: Colors.grey, fontWeight: FontWeight.w600),
                    ),
                    Text(order.deliveryAddress, style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13)),
                    if (isCod) ...[
                      const SizedBox(height: 4),
                      Text(
                        '${isHi ? "नकद संग्रह (COD)" : "Collect Cash"}: ₹${order.totalAmount.toStringAsFixed(0)}',
                        style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w800, color: Colors.red),
                      ),
                    ],
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),

          // Google Maps Navigation Action Buttons
          Row(
            children: [
              Expanded(
                child: OutlinedButton.icon(
                  style: OutlinedButton.styleFrom(
                    foregroundColor: GBColors.primary,
                    side: const BorderSide(color: GBColors.primary),
                    padding: const EdgeInsets.symmetric(vertical: 8),
                  ),
                  icon: const Icon(Icons.storefront, size: 16),
                  label: Text(
                    isHi ? 'दुकान का रास्ता' : 'Store Map',
                    style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w700),
                  ),
                  onPressed: () async {
                    final uri = Uri.parse('https://www.google.com/maps/dir/?api=1&destination=26.2230,85.3520');
                    if (await canLaunchUrl(uri)) {
                      await launchUrl(uri, mode: LaunchMode.externalApplication);
                    } else {
                      if (context.mounted) {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text('Opening Google Maps...')),
                        );
                      }
                    }
                  },
                ),
              ),
              const SizedBox(width: 6),
              Expanded(
                child: OutlinedButton.icon(
                  style: OutlinedButton.styleFrom(
                    foregroundColor: GBColors.secondary,
                    side: const BorderSide(color: GBColors.secondary),
                    padding: const EdgeInsets.symmetric(vertical: 8),
                  ),
                  icon: const Icon(Icons.navigation, size: 16),
                  label: Text(
                    isHi ? 'ग्राहक का रास्ता' : 'Drop Map',
                    style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w700),
                  ),
                  onPressed: () async {
                    final uri = Uri.parse('https://www.google.com/maps/dir/?api=1&destination=26.2210,85.3500');
                    if (await canLaunchUrl(uri)) {
                      await launchUrl(uri, mode: LaunchMode.externalApplication);
                    } else {
                      if (context.mounted) {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text('Opening Google Maps...')),
                        );
                      }
                    }
                  },
                ),
              ),
              const SizedBox(width: 6),
              Tooltip(
                message: 'Chat with Customer',
                child: OutlinedButton(
                  style: OutlinedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
                  ),
                  child: const Icon(Icons.chat_bubble_outline, size: 16, color: GBColors.primary),
                  onPressed: () {
                    Navigator.of(context).push(
                      MaterialPageRoute(
                        builder: (_) => OrderChatScreen(
                          apiClient: state.apiClient,
                          orderId: order.id,
                          currentRole: 'runner',
                          partnerName: 'Customer',
                          partnerPhone: '9800000000',
                        ),
                      ),
                    );
                  },
                ),
              ),
              const SizedBox(width: 6),
              Tooltip(
                message: 'Call Customer',
                child: OutlinedButton(
                  style: OutlinedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
                  ),
                  child: const Icon(Icons.call, size: 16, color: GBColors.primary),
                  onPressed: () async {
                    final uri = Uri.parse('tel:9800000000');
                    if (await canLaunchUrl(uri)) {
                      await launchUrl(uri);
                    }
                  },
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),

          Text(
            itemsSummary.isNotEmpty ? itemsSummary : (isHi ? 'सामग्री विवरण' : 'Items'),
            style: const TextStyle(fontSize: 12, color: Colors.black87),
          ),
          const SizedBox(height: 14),

          // Action Buttons
          _buildActionButtons(state, order.id, order.status, order.deliveryOtp, order.runnerPayout ?? order.deliveryFee, isCod, order.totalAmount, isHi),
        ],
      ),
    );
  }

  Widget _buildActionButtons(
    RunnerAppState state,
    String orderId,
    String status,
    String deliveryOtp,
    double payout,
    bool isCod,
    double codAmount,
    bool isHi,
  ) {
    if (_isActing) {
      return const Center(child: Padding(padding: EdgeInsets.all(8), child: CircularProgressIndicator(strokeWidth: 2)));
    }

    if (status == 'PACKED') {
      return GBPrimaryButton(
        label: isHi ? 'डिलीवरी स्वीकार करें' : 'Accept Delivery Job',
        onPressed: () => _handleAction(state, orderId, 'ACCEPT'),
      );
    } else if (status == 'RUNNER_ASSIGNED') {
      return GBPrimaryButton(
        label: isHi ? 'सामान दुकान से उठाया' : 'Picked Up from Store',
        backgroundColor: GBColors.primary,
        onPressed: () => _handleAction(state, orderId, 'PICKUP'),
      );
    } else if (status == 'PICKED_UP') {
      return GBPrimaryButton(
        label: isHi ? 'ग्राहक की ओर रवाना' : 'Out for Delivery',
        backgroundColor: GBColors.secondary,
        onPressed: () => _handleAction(state, orderId, 'OUT_FOR_DELIVERY'),
      );
    } else if (status == 'OUT_FOR_DELIVERY') {
      return GBPrimaryButton(
        label: isHi ? 'ओटीपी सत्यापित कर डिलीवर करें' : 'Verify OTP & Complete Delivery',
        backgroundColor: GBColors.primaryDark,
        onPressed: () => _showDeliveryOtpDialog(state, orderId, deliveryOtp, payout, isCod, codAmount),
      );
    } else {
      return Container(
        padding: const EdgeInsets.symmetric(vertical: 8),
        alignment: Alignment.center,
        child: Text(
          isHi ? 'डिलीवरी संपन्न' : 'Delivered',
          style: const TextStyle(color: GBColors.success, fontWeight: FontWeight.w800),
        ),
      );
    }
  }
}
