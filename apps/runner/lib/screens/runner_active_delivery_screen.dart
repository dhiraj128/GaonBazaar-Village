import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import 'package:shared_models/shared_models.dart';
import 'package:url_launcher/url_launcher.dart';
import '../state/runner_state.dart';
import 'order_chat_screen.dart';

class RunnerActiveDeliveryScreen extends StatefulWidget {
  final GBOrder order;

  const RunnerActiveDeliveryScreen({
    super.key,
    required this.order,
  });

  @override
  State<RunnerActiveDeliveryScreen> createState() => _RunnerActiveDeliveryScreenState();
}

class _RunnerActiveDeliveryScreenState extends State<RunnerActiveDeliveryScreen> {
  bool _isActing = false;
  late GBOrder _currentOrder;

  @override
  void initState() {
    super.initState();
    _currentOrder = widget.order;
  }

  Future<void> _launchMaps(double? lat, double? lng, String fallbackQuery) async {
    Uri uri;
    if (lat != null && lng != null && (lat != 0 || lng != 0)) {
      uri = Uri.parse('https://www.google.com/maps/dir/?api=1&destination=$lat,$lng');
    } else {
      uri = Uri.parse('https://www.google.com/maps/dir/?api=1&destination=${Uri.encodeComponent(fallbackQuery)}');
    }

    try {
      if (await canLaunchUrl(uri)) {
        await launchUrl(uri, mode: LaunchMode.externalApplication);
      } else {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Could not launch Google Maps')),
          );
        }
      }
    } catch (_) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Could not open map URL')),
        );
      }
    }
  }

  Future<void> _makeCall(String? phone) async {
    if (phone == null || phone.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Phone number not available')),
      );
      return;
    }
    final cleanPhone = phone.replaceAll(RegExp(r'[^0-9+]'), '');
    final uri = Uri.parse('tel:$cleanPhone');
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri);
    }
  }

  Future<void> _handleOrderAction(
    RunnerAppState state,
    String action, {
    String? otp,
  }) async {
    setState(() => _isActing = true);
    final res = await state.handleJobAction(_currentOrder.id, action, deliveryOtp: otp);
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

      // Check updated order in state
      final updated = state.activeJobs.where((o) => o.id == _currentOrder.id);
      if (updated.isNotEmpty) {
        setState(() {
          _currentOrder = updated.first;
        });
      }

      if (action.toUpperCase() == 'DELIVER') {
        Navigator.of(context).pop();
      }
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(res['error']?.toString() ?? (isHi ? 'कार्रवाई विफल रही' : 'Action failed')),
          backgroundColor: GBColors.error,
        ),
      );
    }
  }

  void _showDeliveryPinDialog(RunnerAppState state) {
    final isHi = state.isHindi;
    final ctrl = TextEditingController();
    final isCod = _currentOrder.paymentMethod.toUpperCase() == 'COD';

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(
          isHi ? 'ग्राहक डिलीवरी ओटीपी दर्ज करें' : 'Enter Customer Delivery PIN',
          style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16),
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              isHi
                  ? 'सामान सौंपते समय ग्राहक के फोन पर आया 4-अंकीय ओटीपी कोड दर्ज करें:'
                  : 'Ask customer for the 4-digit PIN upon handing over items:',
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
                  ? 'सुरक्षा नियम: बिना ओटीपी सत्यापन के डिलीवरी पूर्ण नहीं की जा सकती।'
                  : 'Security policy: Delivery requires valid 4-digit verification.',
              style: const TextStyle(fontSize: 11, color: Colors.grey, fontWeight: FontWeight.w500),
            ),
            if (isCod) ...[
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: Colors.red.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.red.withValues(alpha: 0.3)),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.payments_outlined, color: Colors.red, size: 22),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        isHi
                            ? 'नकद भुगतान (COD): ₹${_currentOrder.totalAmount.toStringAsFixed(0)} एकत्र करें'
                            : 'Collect Cash (COD): ₹${_currentOrder.totalAmount.toStringAsFixed(0)}',
                        style: const TextStyle(color: Colors.red, fontWeight: FontWeight.w800, fontSize: 13),
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
              await _handleOrderAction(state, 'DELIVER', otp: entered);
            },
            child: Text(isHi ? 'सत्यापित कर पूर्ण करें' : 'Verify & Complete'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final state = RunnerStateProvider.of(context);
    final isHi = state.isHindi;
    final order = _currentOrder;
    final isCod = order.paymentMethod.toUpperCase() == 'COD';
    final payout = order.runnerPayout ?? order.deliveryFee;

    // Delivery progress status
    final isPickedUp = ['PICKED_UP', 'OUT_FOR_DELIVERY', 'DELIVERED'].contains(order.status);
    final isOutForDelivery = ['OUT_FOR_DELIVERY', 'DELIVERED'].contains(order.status);
    final isDelivered = order.status == 'DELIVERED';

    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              isHi ? 'सक्रिय डिलीवरी मिशन' : 'Active Delivery Mission',
              style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16),
            ),
            Text(
              '#${order.id.length > 8 ? order.id.substring(0, 8) : order.id}',
              style: const TextStyle(fontSize: 12, color: Colors.grey),
            ),
          ],
        ),
        actions: [
          Container(
            margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
            decoration: BoxDecoration(
              color: GBColors.primary.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Row(
              children: [
                const Icon(Icons.currency_rupee, color: GBColors.primary, size: 14),
                Text(
                  payout.toStringAsFixed(0),
                  style: const TextStyle(fontWeight: FontWeight.w800, color: GBColors.primary, fontSize: 14),
                ),
              ],
            ),
          ),
        ],
      ),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // Operational Progression Stepper
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: Theme.of(context).cardColor,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.grey.shade300),
              ),
              child: Column(
                children: [
                  Row(
                    children: [
                      _buildStepCircle(1, isPickedUp, isHi ? 'दुकान पिकअप' : 'Store Pickup'),
                      Expanded(
                        child: Container(
                          height: 2,
                          color: isPickedUp ? GBColors.primary : Colors.grey.shade300,
                        ),
                      ),
                      _buildStepCircle(2, isOutForDelivery, isHi ? 'रास्ते में' : 'En Route'),
                      Expanded(
                        child: Container(
                          height: 2,
                          color: isDelivered ? GBColors.primary : Colors.grey.shade300,
                        ),
                      ),
                      _buildStepCircle(3, isDelivered, isHi ? 'ग्राहक डिलीवरी' : 'Delivered'),
                    ],
                  ),
                ],
              ),
            ),

            const SizedBox(height: 16),

            // Step 1: STORE PICKUP CARD
            Card(
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
              elevation: isPickedUp ? 1 : 3,
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.all(8),
                          decoration: BoxDecoration(
                            color: isPickedUp ? Colors.grey.shade200 : GBColors.primary.withValues(alpha: 0.15),
                            shape: BoxShape.circle,
                          ),
                          child: Icon(
                            Icons.storefront,
                            color: isPickedUp ? Colors.grey : GBColors.primary,
                            size: 22,
                          ),
                        ),
                        const SizedBox(width: 10),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                isHi ? 'चरण 1: किराना दुकान से पिकअप' : 'Step 1: Store Pickup',
                                style: TextStyle(
                                  fontSize: 12,
                                  fontWeight: FontWeight.w600,
                                  color: isPickedUp ? Colors.grey : GBColors.primary,
                                ),
                              ),
                              Text(
                                order.storeName,
                                style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16),
                              ),
                            ],
                          ),
                        ),
                        if (isPickedUp)
                          const Chip(
                            label: Text('✓ Picked Up', style: TextStyle(fontSize: 11, color: GBColors.success)),
                            backgroundColor: Color(0xFFE8F5E9),
                          ),
                      ],
                    ),
                    if (order.storeAddress != null && order.storeAddress!.isNotEmpty) ...[
                      const SizedBox(height: 6),
                      Text(
                        order.storeAddress!,
                        style: const TextStyle(fontSize: 12, color: Colors.grey),
                      ),
                    ],
                    const Divider(height: 20),

                    // Store Actions (Call & Navigate)
                    Row(
                      children: [
                        Expanded(
                          child: OutlinedButton.icon(
                            style: OutlinedButton.styleFrom(
                              foregroundColor: GBColors.primary,
                              side: const BorderSide(color: GBColors.primary),
                              padding: const EdgeInsets.symmetric(vertical: 10),
                            ),
                            icon: const Icon(Icons.navigation, size: 16),
                            label: Text(
                              isHi ? 'दुकान का रास्ता' : 'Store Map',
                              style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 12),
                            ),
                            onPressed: () => _launchMaps(
                              order.storeLatitude,
                              order.storeLongitude,
                              '${order.storeName}, ${order.storeAddress ?? ""}',
                            ),
                          ),
                        ),
                        const SizedBox(width: 10),
                        Expanded(
                          child: OutlinedButton.icon(
                            style: OutlinedButton.styleFrom(
                              foregroundColor: Colors.teal,
                              side: const BorderSide(color: Colors.teal),
                              padding: const EdgeInsets.symmetric(vertical: 10),
                            ),
                            icon: const Icon(Icons.phone, size: 16),
                            label: Text(
                              isHi ? 'दुकानदार को कॉल' : 'Call Store',
                              style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 12),
                            ),
                            onPressed: () => _makeCall(order.storePhone),
                          ),
                        ),
                      ],
                    ),

                    // Items Checklist
                    const SizedBox(height: 14),
                    Text(
                      isHi ? 'सामग्री सत्यापन सूची (${order.items.length} वस्तुएँ):' : 'Package Items (${order.items.length} items):',
                      style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13),
                    ),
                    const SizedBox(height: 8),
                    ...order.items.map((item) => Padding(
                          padding: const EdgeInsets.symmetric(vertical: 4),
                          child: Row(
                            children: [
                              const Icon(Icons.check_circle_outline, size: 16, color: GBColors.primary),
                              const SizedBox(width: 8),
                              Expanded(
                                child: Text(
                                  isHi ? item.nameHi : item.nameEn,
                                  style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w500),
                                ),
                              ),
                              Text(
                                '${item.quantity} x ₹${item.unitPrice.toStringAsFixed(0)}',
                                style: const TextStyle(fontSize: 12, color: Colors.grey, fontWeight: FontWeight.w600),
                              ),
                            ],
                          ),
                        )),

                    if (!isPickedUp) ...[
                      const SizedBox(height: 16),
                      SizedBox(
                        width: double.infinity,
                        child: ElevatedButton.icon(
                          style: ElevatedButton.styleFrom(
                            backgroundColor: GBColors.primary,
                            padding: const EdgeInsets.symmetric(vertical: 12),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                          ),
                          icon: const Icon(Icons.inventory_2, color: Colors.white),
                          label: Text(
                            isHi ? 'सामान प्राप्त किया (Confirm Pickup)' : 'Confirm Store Pickup',
                            style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 14, color: Colors.white),
                          ),
                          onPressed: _isActing ? null : () => _handleOrderAction(state, 'PICKUP'),
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            ),

            const SizedBox(height: 16),

            // Step 2 & 3: CUSTOMER DELIVERY CARD
            Card(
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
              elevation: isPickedUp ? 3 : 1,
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.all(8),
                          decoration: BoxDecoration(
                            color: isPickedUp ? GBColors.secondary.withValues(alpha: 0.15) : Colors.grey.shade200,
                            shape: BoxShape.circle,
                          ),
                          child: Icon(
                            Icons.location_on,
                            color: isPickedUp ? GBColors.secondary : Colors.grey,
                            size: 22,
                          ),
                        ),
                        const SizedBox(width: 10),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                isHi ? 'चरण 2: ग्राहक डिलीवरी' : 'Step 2: Customer Delivery',
                                style: TextStyle(
                                  fontSize: 12,
                                  fontWeight: FontWeight.w600,
                                  color: isPickedUp ? GBColors.secondary : Colors.grey,
                                ),
                              ),
                              Text(
                                order.customerName ?? (isHi ? 'गाँव ग्राहक' : 'Customer'),
                                style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16),
                              ),
                            ],
                          ),
                        ),
                        if (isDelivered)
                          const Chip(
                            label: Text('✓ Delivered', style: TextStyle(fontSize: 11, color: GBColors.success)),
                            backgroundColor: Color(0xFFE8F5E9),
                          ),
                      ],
                    ),
                    const SizedBox(height: 6),
                    Text(
                      order.deliveryAddress,
                      style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600),
                    ),
                    const Divider(height: 20),

                    // Customer Actions (Navigate, Call, Chat)
                    Row(
                      children: [
                        Expanded(
                          child: OutlinedButton.icon(
                            style: OutlinedButton.styleFrom(
                              foregroundColor: GBColors.secondary,
                              side: const BorderSide(color: GBColors.secondary),
                              padding: const EdgeInsets.symmetric(vertical: 10),
                            ),
                            icon: const Icon(Icons.navigation, size: 16),
                            label: Text(
                              isHi ? 'ग्राहक का रास्ता' : 'Drop Map',
                              style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 12),
                            ),
                            onPressed: () => _launchMaps(
                              order.deliveryLatitude,
                              order.deliveryLongitude,
                              order.deliveryAddress,
                            ),
                          ),
                        ),
                        const SizedBox(width: 8),
                        OutlinedButton.icon(
                          style: OutlinedButton.styleFrom(
                            foregroundColor: Colors.teal,
                            side: const BorderSide(color: Colors.teal),
                            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                          ),
                          icon: const Icon(Icons.phone, size: 16),
                          label: Text(
                            isHi ? 'कॉल' : 'Call',
                            style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 12),
                          ),
                          onPressed: () => _makeCall(order.customerPhone),
                        ),
                        const SizedBox(width: 8),
                        OutlinedButton(
                          style: OutlinedButton.styleFrom(
                            foregroundColor: GBColors.primary,
                            side: const BorderSide(color: GBColors.primary),
                            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 10),
                          ),
                          child: const Icon(Icons.chat_bubble_outline, size: 16),
                          onPressed: () {
                            Navigator.of(context).push(
                              MaterialPageRoute(
                                builder: (_) => OrderChatScreen(
                                  apiClient: state.apiClient,
                                  orderId: order.id,
                                  currentRole: 'runner',
                                  partnerName: order.customerName ?? 'Customer',
                                  partnerPhone: order.customerPhone ?? '',
                                ),
                              ),
                            );
                          },
                        ),
                      ],
                    ),

                    // COD Box
                    if (isCod) ...[
                      const SizedBox(height: 14),
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: Colors.red.withValues(alpha: 0.08),
                          borderRadius: BorderRadius.circular(10),
                          border: Border.all(color: Colors.red.withValues(alpha: 0.3)),
                        ),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Row(
                              children: [
                                const Icon(Icons.payments_outlined, color: Colors.red, size: 24),
                                const SizedBox(width: 10),
                                Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      isHi ? 'सीओडी नकद एकत्र करें' : 'Collect Cash on Delivery',
                                      style: const TextStyle(fontSize: 12, color: Colors.red, fontWeight: FontWeight.w700),
                                    ),
                                    Text(
                                      '₹${order.totalAmount.toStringAsFixed(0)}',
                                      style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w900, color: Colors.red),
                                    ),
                                  ],
                                ),
                              ],
                            ),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                              decoration: BoxDecoration(
                                color: Colors.red,
                                borderRadius: BorderRadius.circular(6),
                              ),
                              child: Text(
                                isHi ? 'नकद भुगतान' : 'CASH',
                                style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w800, fontSize: 11),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],

                    const SizedBox(height: 16),

                    // Action buttons depending on state
                    if (isPickedUp && !isOutForDelivery) ...[
                      SizedBox(
                        width: double.infinity,
                        child: ElevatedButton.icon(
                          style: ElevatedButton.styleFrom(
                            backgroundColor: GBColors.secondary,
                            padding: const EdgeInsets.symmetric(vertical: 12),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                          ),
                          icon: const Icon(Icons.two_wheeler, color: Colors.white),
                          label: Text(
                            isHi ? 'ग्राहक की ओर रवाना (Out for Delivery)' : 'Mark Out for Delivery',
                            style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 14, color: Colors.white),
                          ),
                          onPressed: _isActing ? null : () => _handleOrderAction(state, 'OUT_FOR_DELIVERY'),
                        ),
                      ),
                    ] else if (isOutForDelivery && !isDelivered) ...[
                      SizedBox(
                        width: double.infinity,
                        child: ElevatedButton.icon(
                          style: ElevatedButton.styleFrom(
                            backgroundColor: GBColors.primaryDark,
                            padding: const EdgeInsets.symmetric(vertical: 12),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                          ),
                          icon: const Icon(Icons.pin_outlined, color: Colors.white),
                          label: Text(
                            isHi ? 'ओटीपी सत्यापित कर डिलीवर करें' : 'Verify PIN & Complete Delivery',
                            style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 14, color: Colors.white),
                          ),
                          onPressed: _isActing ? null : () => _showDeliveryPinDialog(state),
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStepCircle(int step, bool isDone, String label) {
    return Column(
      children: [
        Container(
          width: 32,
          height: 32,
          decoration: BoxDecoration(
            color: isDone ? GBColors.primary : Colors.grey.shade300,
            shape: BoxShape.circle,
          ),
          alignment: Alignment.center,
          child: isDone
              ? const Icon(Icons.check, size: 18, color: Colors.white)
              : Text('$step', style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.white)),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: TextStyle(
            fontSize: 10,
            fontWeight: isDone ? FontWeight.w700 : FontWeight.w500,
            color: isDone ? GBColors.primary : Colors.grey,
          ),
        ),
      ],
    );
  }
}
