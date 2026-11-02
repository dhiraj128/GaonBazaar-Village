import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import 'package:shared_models/shared_models.dart';
import '../state/runner_state.dart';
import 'runner_auth_screen.dart';

class RunnerDashboardScreen extends StatefulWidget {
  const RunnerDashboardScreen({super.key});

  @override
  State<RunnerDashboardScreen> createState() => _RunnerDashboardScreenState();
}

class _RunnerDashboardScreenState extends State<RunnerDashboardScreen> {
  bool _isActing = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final state = RunnerStateProvider.of(context);
      state.fetchProfile();
      state.fetchJobs();
      state.fetchFinances();
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

              if (mounted) {
                showDialog(
                  context: context,
                  builder: (c) => AlertDialog(
                    icon: const Icon(Icons.celebration, color: GBColors.primary, size: 48),
                    title: Text(
                      isHi ? 'डिलीवरी सफलतापूर्वक संपन्न!' : 'Delivery Completed Successfully!',
                      style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 17),
                    ),
                    content: Column(
                      mainAxisSize: MainAxisSize.min,
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          isHi ? 'आपकी डिलीवरी शुल्क कमाई:' : 'Your delivery earning:',
                          style: const TextStyle(fontSize: 13),
                        ),
                        Text(
                          '₹${payout.toStringAsFixed(0)}',
                          style: const TextStyle(fontSize: 26, fontWeight: FontWeight.w900, color: GBColors.primary),
                        ),
                        if (isCod) ...[
                          const SizedBox(height: 8),
                          Text(
                            isHi
                                ? 'एकत्रित नकद राशि: ₹${codAmount.toStringAsFixed(0)} (आज रात कंपनी को जमा करें)'
                                : 'Collected Cash: ₹${codAmount.toStringAsFixed(0)} (Remit tonight)',
                            style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: Colors.blue),
                          ),
                        ],
                      ],
                    ),
                    actions: [
                      ElevatedButton(
                        style: ElevatedButton.styleFrom(backgroundColor: GBColors.primary),
                        onPressed: () => Navigator.of(c).pop(),
                        child: Text(isHi ? 'ठीक है' : 'OK'),
                      ),
                    ],
                  ),
                );
              }
            },
            child: Text(isHi ? 'डिलीवर करें' : 'Confirm Deliver'),
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
      drawer: Drawer(
        child: ListView(
          padding: EdgeInsets.zero,
          children: [
            DrawerHeader(
              decoration: const BoxDecoration(
                gradient: LinearGradient(
                  colors: [Color(0xFF1B5E20), Color(0xFF2E7D32)],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  const Icon(Icons.two_wheeler, color: Colors.white, size: 36),
                  const SizedBox(height: 8),
                  Text(
                    state.runnerProfile?['full_name'] as String? ?? state.currentUser?.name ?? 'Santosh Kumar',
                    style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w800, fontSize: 16),
                  ),
                  Text(
                    '${isHi ? "वाहन" : "Vehicle"}: ${state.runnerProfile?["vehicle_number"] ?? "BR-06-AB-1234"} • ⭐ 4.9',
                    style: const TextStyle(color: Colors.white70, fontSize: 12),
                  ),
                ],
              ),
            ),
            ListTile(
              leading: const Icon(Icons.currency_rupee),
              title: Text(isHi ? 'कमाई व ट्रिप हिस्ट्री' : 'Earnings & Trips'),
              subtitle: Text('${isHi ? "आज की कमाई" : "Today"}: ₹${state.todayEarnings.toStringAsFixed(0)}'),
              onTap: () {
                Navigator.of(context).pop();
                state.fetchFinances();
              },
            ),
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
              title: Text(isHi ? 'इमरजेंसी डिलीवरी हेल्पलाइन' : 'Emergency Helpline'),
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
                  MaterialPageRoute(builder: (_) => const RunnerAuthScreen()),
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
            // Approval Warning Banner if runner not yet approved
            if (!state.isApproved)
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
                            ? 'आपकी प्रोफ़ाइल सत्यापन प्रक्रियाधीन है। सुपर एडमिन द्वारा अनुमोदन के बाद ही आप ड्यूटी ऑनलाइन कर सकेंगे।'
                            : 'Your profile is pending admin approval. You can go online on duty once approved.',
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
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
              color: state.isOnline ? GBColors.success.withValues(alpha: 0.08) : GBColors.error.withValues(alpha: 0.08),
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

            // Pull to refresh body
            Expanded(
              child: RefreshIndicator(
                onRefresh: () async {
                  await state.fetchJobs();
                  await state.fetchFinances();
                },
                child: ListView(
                  padding: const EdgeInsets.all(16),
                  children: [
                    // Daily Earnings Card
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
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                isHi ? 'आज की डिलीवरी कमाई' : "Today's Earnings",
                                style: const TextStyle(color: Colors.white70, fontSize: 12),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                '₹${state.todayEarnings.toStringAsFixed(0)}',
                                style: const TextStyle(color: Colors.white, fontSize: 28, fontWeight: FontWeight.w900),
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
                                '${state.completedTrips} ${isHi ? "ट्रिप्स" : "Trips"}',
                                style: const TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.w800),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 16),

                    // Active Jobs List
                    _buildJobsSection(state),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

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
                  '${isHi ? "कमाई" : "Earn"}: ₹${order.deliveryFee.toStringAsFixed(0)}',
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
                  onPressed: () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text(isHi ? 'दुकान का गूगल मैप्स नेविगेशन: ${order.storeName}' : 'Store Google Maps: ${order.storeName}'),
                        duration: const Duration(seconds: 2),
                      ),
                    );
                  },
                ),
              ),
              const SizedBox(width: 8),
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
                  onPressed: () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text(isHi ? 'ग्राहक का गूगल मैप्स नेविगेशन: ${order.deliveryAddress}' : 'Customer Google Maps: ${order.deliveryAddress}'),
                        duration: const Duration(seconds: 2),
                      ),
                    );
                  },
                ),
              ),
              const SizedBox(width: 8),
              OutlinedButton(
                style: OutlinedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                ),
                child: const Icon(Icons.call, size: 16, color: GBColors.primary),
                onPressed: () {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('${isHi ? "कॉलिंग ग्राहक" : "Calling customer"}: +91 9800000000')),
                  );
                },
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
          _buildActionButtons(state, order.id, order.status, order.deliveryOtp, order.deliveryFee, isCod, order.totalAmount, isHi),
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
