import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import '../state/runner_state.dart';
import 'runner_auth_screen.dart';

class RunnerDashboardScreen extends StatefulWidget {
  const RunnerDashboardScreen({super.key});

  @override
  State<RunnerDashboardScreen> createState() => _RunnerDashboardScreenState();
}

class _RunnerDashboardScreenState extends State<RunnerDashboardScreen> {
  final TextEditingController _otpCtrl = TextEditingController();
  bool _isVerifyingOtp = false;

  void _confirmPickup() {
    final state = RunnerStateProvider.of(context);
    state.updateJobStatus('PICKED_UP');
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('सामान दुकान से उठाया गया। अब ग्राहक के पास डिलीवरी के लिए निकलें।')),
    );
  }

  void _markOutForDelivery() {
    final state = RunnerStateProvider.of(context);
    state.updateJobStatus('OUT_FOR_DELIVERY');
  }

  void _completeDelivery() {
    final state = RunnerStateProvider.of(context);
    final job = state.activeJob;
    if (job == null) return;

    final enteredOtp = _otpCtrl.text.trim();
    if (enteredOtp != job['delivery_otp']) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('गलत डिलीवरी ओटीपी! कृपया ग्राहक से सही 4-अंकीय कोड लें।'),
          backgroundColor: GBColors.error,
        ),
      );
      return;
    }

    setState(() => _isVerifyingOtp = true);

    Future.delayed(const Duration(milliseconds: 600), () {
      if (!mounted) return;
      setState(() => _isVerifyingOtp = false);
      state.updateJobStatus('DELIVERED');

      showDialog(
        context: context,
        builder: (ctx) => AlertDialog(
          title: const Text('डिलीवरी सफल! (Delivered)'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('सामान सफलतापूर्वक सुपुर्द कर दिया गया है।'),
              const SizedBox(height: 10),
              Text('आपकी कमाई: ₹${job['payout']}', style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16, color: GBColors.primary)),
              if (job['is_cod'] == true) ...[
                const SizedBox(height: 8),
                Text('नकद संग्रह (COD Cash Collected): ₹${job['cod_amount']}', style: const TextStyle(fontWeight: FontWeight.w700, color: Colors.blue)),
              ],
            ],
          ),
          actions: [
            ElevatedButton(
              onPressed: () {
                Navigator.of(ctx).pop();
                state.clearJob();
              },
              child: const Text('अगला काम देखें'),
            ),
          ],
        ),
      );
    });
  }

  @override
  Widget build(BuildContext context) {
    final state = RunnerStateProvider.of(context);
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final job = state.activeJob;

    return Scaffold(
      appBar: AppBar(
        title: const Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('गाँव बाज़ार डिलीवरी साथी', style: TextStyle(fontWeight: FontWeight.w800, fontSize: 16)),
            Text('मीनापुर पायलट (Minapur Zone)', style: TextStyle(fontSize: 11, color: Colors.grey)),
          ],
        ),
        actions: [
          Row(
            children: [
              Text(
                state.isOnline ? 'ड्यूटी ऑन' : 'ड्यूटी ऑफ',
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w700,
                  color: state.isOnline ? GBColors.success : GBColors.error,
                ),
              ),
              Switch(
                value: state.isOnline,
                activeColor: GBColors.success,
                onChanged: (v) => state.toggleOnline(),
              ),
            ],
          ),
        ],
      ),
      drawer: Drawer(
        child: ListView(
          padding: EdgeInsets.zero,
          children: [
            DrawerHeader(
              decoration: const BoxDecoration(color: Color(0xFF1B5E20)),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  const Icon(Icons.two_wheeler, color: Colors.white, size: 36),
                  const SizedBox(height: 8),
                  Text(state.currentUser?.name ?? 'Santosh Kumar', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w800, fontSize: 16)),
                  const Text('बाइक नंबर: BR-06-AB-1234', style: TextStyle(color: Colors.white70, fontSize: 12)),
                ],
              ),
            ),
            ListTile(
              leading: const Icon(Icons.currency_rupee),
              title: const Text('कमाई व ट्रिप हिस्ट्री'),
              subtitle: Text('आज की कमाई: ₹${state.todayEarnings.toStringAsFixed(0)}'),
              onTap: () => Navigator.of(context).pop(),
            ),
            ListTile(
              leading: const Icon(Icons.headset_mic_outlined),
              title: const Text('डिलीवरी हेल्पलाइन'),
              subtitle: const Text('1800-GAON-BAZAAR'),
              onTap: () => Navigator.of(context).pop(),
            ),
            const Divider(),
            ListTile(
              leading: const Icon(Icons.logout, color: GBColors.error),
              title: const Text('लॉग आउट (Logout)', style: TextStyle(color: GBColors.error, fontWeight: FontWeight.w700)),
              onTap: () {
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
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // Daily Earnings Card
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [Color(0xFF2E7D32), Color(0xFF1B5E20)],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(14),
                boxShadow: [
                  BoxShadow(color: Colors.black.withOpacity(0.12), blurRadius: 6, offset: const Offset(0, 2)),
                ],
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('आज की कमाई (Today)', style: TextStyle(color: Colors.white70, fontSize: 12)),
                      const SizedBox(height: 4),
                      Text('₹${state.todayEarnings.toStringAsFixed(0)}', style: const TextStyle(color: Colors.white, fontSize: 28, fontWeight: FontWeight.w900)),
                    ],
                  ),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      const Text('पूरी की गई डिलीवरी', style: TextStyle(color: Colors.white70, fontSize: 12)),
                      const SizedBox(height: 4),
                      Text('${state.completedTrips} Trips', style: const TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.w800)),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Active Job Section
            if (job != null) ...[
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: isDark ? GBColors.cardDark : Colors.white,
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(color: isDark ? GBColors.borderDark : GBColors.borderLight),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text('सक्रिय डिलीवरी #${job['id']}', style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 15)),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                          decoration: BoxDecoration(
                            color: GBColors.primary.withOpacity(0.1),
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: Text(
                            'कमाई: ₹${job['payout']}',
                            style: const TextStyle(fontWeight: FontWeight.w800, color: GBColors.primary, fontSize: 12),
                          ),
                        ),
                      ],
                    ),
                    const Divider(height: 20),

                    // Pickup Store Information
                    Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Icon(Icons.storefront, color: GBColors.primary, size: 20),
                        const SizedBox(width: 10),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Text('पिकअप दुकान (Pickup Store):', style: TextStyle(fontSize: 11, color: Colors.grey)),
                              Text(job['store_name'] as String, style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13)),
                              Text('${job['store_village']}, ${job['store_landmark']}', style: const TextStyle(fontSize: 12)),
                            ],
                          ),
                        ),
                        IconButton(
                          icon: const Icon(Icons.call, color: GBColors.primary),
                          onPressed: () {
                            ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('दुकानदार: +91 9800000001')));
                          },
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),

                    // Drop Customer Information
                    Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Icon(Icons.person_pin_circle, color: GBColors.secondary, size: 20),
                        const SizedBox(width: 10),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Text('ग्राहक का पता (Drop Customer):', style: TextStyle(fontSize: 11, color: Colors.grey)),
                              Text(job['customer_name'] as String, style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13)),
                              Text(job['customer_village'] as String, style: const TextStyle(fontSize: 12)),
                              if (job['is_cod'] == true)
                                Text('नकद संग्रह (Collect Cash): ₹${job['cod_amount']}', style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w800, color: Colors.red)),
                            ],
                          ),
                        ),
                        IconButton(
                          icon: const Icon(Icons.call, color: GBColors.primary),
                          onPressed: () {
                            ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('ग्राहक: +91 ${job['customer_phone']}')));
                          },
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),

                    // Actions based on job stage
                    if (job['status'] == 'ASSIGNED') ...[
                      GBPrimaryButton(
                        label: 'सामान दुकान से उठाया (Confirm Pickup)',
                        onPressed: _confirmPickup,
                      ),
                    ] else if (job['status'] == 'PICKED_UP') ...[
                      GBPrimaryButton(
                        label: 'ग्राहक की ओर रवाना (Out for Delivery)',
                        backgroundColor: GBColors.secondary,
                        onPressed: _markOutForDelivery,
                      ),
                    ] else if (job['status'] == 'OUT_FOR_DELIVERY') ...[
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: GBColors.primary.withOpacity(0.08),
                          borderRadius: BorderRadius.circular(10),
                          border: Border.all(color: GBColors.primary),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text('ग्राहक का 4-अंकीय ओटीपी दर्ज करें (Enter OTP):', style: TextStyle(fontWeight: FontWeight.w700, fontSize: 12)),
                            const SizedBox(height: 8),
                            TextField(
                              controller: _otpCtrl,
                              keyboardType: TextInputType.number,
                              maxLength: 4,
                              textAlign: TextAlign.center,
                              style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w900, letterSpacing: 8),
                              decoration: const InputDecoration(
                                hintText: '----',
                                counterText: '',
                                filled: true,
                                fillColor: Colors.white,
                              ),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 12),
                      GBPrimaryButton(
                        label: 'डिलीवरी पूर्ण करें (Complete Delivery)',
                        isLoading: _isVerifyingOtp,
                        onPressed: _completeDelivery,
                      ),
                    ],
                  ],
                ),
              ),
            ] else ...[
              // No active job state
              Center(
                child: Padding(
                  padding: const EdgeInsets.symmetric(vertical: 40),
                  child: Column(
                    children: [
                      Icon(Icons.radar, size: 60, color: GBColors.primary.withOpacity(0.6)),
                      const SizedBox(height: 14),
                      const Text('नई डिलीवरी की प्रतीक्षा में...', style: TextStyle(fontWeight: FontWeight.w800, fontSize: 16)),
                      const SizedBox(height: 4),
                      const Text('मीनापुर ८ किमी दायरे में नया ऑर्डर आने पर तुरंत सूचना दी जाएगी।', textAlign: TextAlign.center, style: TextStyle(color: Colors.grey, fontSize: 12)),
                    ],
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
