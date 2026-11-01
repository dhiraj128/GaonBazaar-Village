import 'dart:async';
import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import 'package:localization/localization.dart';
import 'package:shared_models/shared_models.dart';
import '../state/app_state.dart';

class OrderTrackingScreen extends StatefulWidget {
  final GBOrder order;

  const OrderTrackingScreen({super.key, required this.order});

  @override
  State<OrderTrackingScreen> createState() => _OrderTrackingScreenState();
}

class _OrderTrackingScreenState extends State<OrderTrackingScreen> {
  late GBOrder _order;
  int _secondsRemaining = 0;
  Timer? _timer;
  bool _isCancelling = false;

  @override
  void initState() {
    super.initState();
    _order = widget.order;
    _secondsRemaining = _order.cancelSecondsRemaining;
    if (_secondsRemaining > 0 && _order.status == 'PLACED') {
      _timer = Timer.periodic(const Duration(seconds: 1), (t) {
        if (_secondsRemaining > 0) {
          setState(() => _secondsRemaining--);
        } else {
          t.cancel();
          setState(() {});
        }
      });
    }
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  Future<void> _handleCancel() async {
    setState(() => _isCancelling = true);
    final state = AppStateProvider.of(context);
    final response = await state.apiClient.cancelOrder(
      _order.id,
      'Customer cancelled within 180s',
    );
    setState(() => _isCancelling = false);

    if (response.isSuccess && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('ऑर्डर सफलतापूर्वक रद्द कर दिया गया।')),
      );
      Navigator.of(context).pop();
    } else if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(response.errorMessage ?? 'रद्द करने की समय सीमा समाप्त हो चुकी है।'),
          backgroundColor: GBColors.error,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final loc = GBLocalizations.of(context);
    final isDark = Theme.of(context).brightness == Brightness.dark;

    final stages = [
      {'status': 'PLACED', 'title_hi': 'ऑर्डर दर्ज हुआ', 'title_en': 'Order Placed'},
      {'status': 'ACCEPTED', 'title_hi': 'दुकानदार ने स्वीकार किया', 'title_en': 'Store Accepted'},
      {'status': 'PACKED', 'title_hi': 'सामान पैक हुआ', 'title_en': 'Packed & Ready'},
      {'status': 'RUNNER_ASSIGNED', 'title_hi': 'डिलीवरी साथी तय हुआ', 'title_en': 'Runner Assigned'},
      {'status': 'PICKED_UP', 'title_hi': 'सामान दुकान से उठाया', 'title_en': 'Picked Up by Runner'},
      {'status': 'OUT_FOR_DELIVERY', 'title_hi': 'रास्ते में है (Out for Delivery)', 'title_en': 'Out for Delivery'},
      {'status': 'DELIVERED', 'title_hi': 'पहुँचा दिया (Delivered)', 'title_en': 'Delivered'},
    ];

    int currentStageIndex = 0;
    for (int i = 0; i < stages.length; i++) {
      if (stages[i]['status'] == _order.status) {
        currentStageIndex = i;
        break;
      }
    }
    if (_order.status == 'DELIVERED') currentStageIndex = 6;

    return Scaffold(
      appBar: AppBar(
        title: Text(loc.tr('order_tracking'), style: const TextStyle(fontWeight: FontWeight.w800)),
      ),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // Status Card
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: isDark ? GBColors.cardDark : Colors.white,
                borderRadius: BorderRadius.circular(14),
                border: Border.all(
                  color: isDark ? GBColors.borderDark : GBColors.borderLight,
                ),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'Order #${_order.id.substring(0, 8).toUpperCase()}',
                        style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16),
                      ),
                      GBOrderStatusBadge(status: _order.status),
                    ],
                  ),
                  const SizedBox(height: 10),
                  Text(
                    _order.storeName,
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                      color: isDark ? GBColors.textSecondaryDark : GBColors.textSecondaryLight,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    _order.deliveryAddress,
                    style: TextStyle(
                      fontSize: 12,
                      color: isDark ? GBColors.textMutedDark : GBColors.textMutedLight,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Delivery OTP Card (Crucial for rural delivery handoff)
            if (_order.status != 'CANCELLED' && _order.status != 'DELIVERED')
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: GBColors.primary.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(color: GBColors.primary, width: 1.5),
                ),
                child: Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: const BoxDecoration(
                        color: GBColors.primary,
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(Icons.pin, color: Colors.white, size: 24),
                    ),
                    const SizedBox(width: 14),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            loc.tr('delivery_otp_code'),
                            style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
                          ),
                          Text(
                            _order.deliveryOtp,
                            style: const TextStyle(
                              fontSize: 26,
                              fontWeight: FontWeight.w900,
                              letterSpacing: 4,
                              color: GBColors.primary,
                            ),
                          ),
                          Text(
                            loc.tr('show_otp_to_runner'),
                            style: TextStyle(
                              fontSize: 11,
                              color: isDark ? GBColors.textMutedDark : GBColors.textMutedLight,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),

            const SizedBox(height: 20),

            // 7-Stage Order Pipeline
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: isDark ? GBColors.cardDark : Colors.white,
                borderRadius: BorderRadius.circular(14),
                border: Border.all(
                  color: isDark ? GBColors.borderDark : GBColors.borderLight,
                ),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'ऑर्डर स्थिति (Order Pipeline)',
                    style: TextStyle(fontWeight: FontWeight.w800, fontSize: 15),
                  ),
                  const SizedBox(height: 16),
                  ...List.generate(stages.length, (idx) {
                    final stage = stages[idx];
                    final isCompleted = idx <= currentStageIndex;
                    final isCurrent = idx == currentStageIndex;
                    final title = loc.isHindi ? stage['title_hi']! : stage['title_en']!;

                    return Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Column(
                          children: [
                            Container(
                              width: 22,
                              height: 22,
                              decoration: BoxDecoration(
                                shape: BoxShape.circle,
                                color: isCompleted ? GBColors.primary : Colors.grey.shade300,
                              ),
                              child: Center(
                                child: isCompleted
                                    ? const Icon(Icons.check, size: 14, color: Colors.white)
                                    : null,
                              ),
                            ),
                            if (idx < stages.length - 1)
                              Container(
                                width: 2,
                                height: 32,
                                color: isCompleted ? GBColors.primary : Colors.grey.shade300,
                              ),
                          ],
                        ),
                        const SizedBox(width: 14),
                        Padding(
                          padding: const EdgeInsets.only(top: 2),
                          child: Text(
                            title,
                            style: TextStyle(
                              fontSize: 14,
                              fontWeight: isCurrent ? FontWeight.w800 : FontWeight.w500,
                              color: isCompleted
                                  ? (isDark ? Colors.white : Colors.black87)
                                  : Colors.grey,
                            ),
                          ),
                        ),
                      ],
                    );
                  }),
                ],
              ),
            ),

            const SizedBox(height: 16),

            // 180s Cancellation Section
            if (_order.status == 'PLACED' && _secondsRemaining > 0)
              Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: GBColors.warning.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: GBColors.warning.withOpacity(0.5)),
                ),
                child: Column(
                  children: [
                    Row(
                      children: [
                        const Icon(Icons.timer_outlined, color: GBColors.warning, size: 20),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            'ऑर्डर रद्द करने के लिए शेष समय: ${_secondsRemaining}s',
                            style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 10),
                    OutlinedButton(
                      onPressed: _isCancelling ? null : _handleCancel,
                      style: OutlinedButton.styleFrom(
                        foregroundColor: GBColors.error,
                        side: const BorderSide(color: GBColors.error),
                        minimumSize: const Size.fromHeight(40),
                      ),
                      child: _isCancelling
                          ? const SizedBox(
                              width: 16,
                              height: 16,
                              child: CircularProgressIndicator(strokeWidth: 2, color: GBColors.error),
                            )
                          : Text(loc.tr('cancel_order')),
                    ),
                  ],
                ),
              ),

            const SizedBox(height: 24),

            // Contact Actions
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text('दुकानदार का नंबर: +91 9800000001')),
                      );
                    },
                    icon: const Icon(Icons.phone, size: 18),
                    label: Text(loc.tr('call_store')),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text('सहायता हेल्पलाइन: 1800-GAON-BAZAAR')),
                      );
                    },
                    icon: const Icon(Icons.help_outline, size: 18),
                    label: Text(loc.tr('need_help')),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
