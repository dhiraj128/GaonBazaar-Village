import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:design_system/design_system.dart';
import 'package:url_launcher/url_launcher.dart';
import 'order_chat_screen.dart';
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
    final loc = GBLocalizations.of(context);
    setState(() => _isCancelling = true);
    final state = AppStateProvider.of(context);
    final response = await state.apiClient.cancelOrder(
      _order.id,
      'Customer cancelled within 180s',
    );
    setState(() => _isCancelling = false);

    if (response.isSuccess && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(loc.tr('order_cancelled_success'))),
      );
      state.fetchOrders();
      Navigator.of(context).pop();
    } else if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(response.errorMessage ?? loc.tr('cancel_window_closed')),
          backgroundColor: GBColors.error,
        ),
      );
    }
  }

  void _openOrderHelpDialog() {
    final loc = GBLocalizations.of(context);
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final state = AppStateProvider.of(context);

    final issues = [
      loc.isHindi ? 'डिलीवरी में देरी (Delayed delivery)' : 'Delayed delivery',
      loc.isHindi ? 'सामान कम मिला (Missing item)' : 'Missing item',
      loc.isHindi ? 'गलत सामान मिला (Wrong item)' : 'Wrong item',
      loc.isHindi ? 'सामान खराब या टूटा मिला (Damaged item)' : 'Damaged item',
      loc.isHindi ? 'भुगतान से जुड़ी समस्या (Payment problem)' : 'Payment problem',
      loc.isHindi ? 'डिलीवरी साथी से जुड़ी समस्या (Delivery partner issue)' : 'Delivery partner issue',
      loc.isHindi ? 'रद्दीकरण या रिफ़ंड अनुरोध (Refund request)' : 'Refund request',
    ];

    String selectedCategory = issues[0];
    final messageController = TextEditingController();
    bool isSubmitting = false;

    showDialog(
      context: context,
      builder: (ctx) {
        return StatefulBuilder(
          builder: (dialogCtx, setDialogState) {
            return AlertDialog(
              backgroundColor: isDark ? GBColors.surfaceDark : Colors.white,
              title: Row(
                children: [
                  const Icon(Icons.help_outline, color: GBColors.primary),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      '${loc.tr('need_help')} (#${_order.id.length > 6 ? _order.id.substring(_order.id.length - 6) : _order.id})',
                      style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w800),
                    ),
                  ),
                ],
              ),
              content: SingleChildScrollView(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      loc.tr('ticket_subject'),
                      style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13),
                    ),
                    const SizedBox(height: 6),
                    DropdownButtonFormField<String>(
                      initialValue: selectedCategory,
                      isExpanded: true,
                      decoration: InputDecoration(
                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                        contentPadding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                      ),
                      items: issues.map((cat) {
                        return DropdownMenuItem(value: cat, child: Text(cat, style: const TextStyle(fontSize: 12)));
                      }).toList(),
                      onChanged: (val) {
                        if (val != null) setDialogState(() => selectedCategory = val);
                      },
                    ),
                    const SizedBox(height: 14),
                    Text(
                      loc.tr('ticket_message'),
                      style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13),
                    ),
                    const SizedBox(height: 6),
                    TextField(
                      controller: messageController,
                      maxLines: 3,
                      decoration: InputDecoration(
                        hintText: loc.isHindi ? 'अपनी समस्या का विवरण यहाँ लिखें...' : 'Describe your issue in detail...',
                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                        contentPadding: const EdgeInsets.all(10),
                      ),
                    ),
                  ],
                ),
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.of(ctx).pop(),
                  child: Text(loc.tr('cancel')),
                ),
                ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: GBColors.primary,
                    foregroundColor: Colors.white,
                  ),
                  onPressed: isSubmitting
                      ? null
                      : () async {
                          final msg = messageController.text.trim();
                          if (msg.isEmpty) return;

                          setDialogState(() => isSubmitting = true);
                          final res = await state.apiClient.createSupportTicket(
                            orderId: _order.id,
                            subject: selectedCategory,
                            message: msg,
                          );
                          setDialogState(() => isSubmitting = false);

                          if (res.isSuccess && mounted) {
                            Navigator.of(ctx).pop();
                            ScaffoldMessenger.of(context).showSnackBar(
                              SnackBar(content: Text(loc.tr('ticket_created_success'))),
                            );
                          }
                        },
                  child: isSubmitting
                      ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                      : Text(loc.tr('submit_ticket')),
                ),
              ],
            );
          },
        );
      },
    );
  }

  Future<void> _callStore() async {
    final uri = Uri.parse('tel:9800000001');
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri);
    } else {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Calling ${_order.storeName}...')),
        );
      }
    }
  }

  Future<void> _callRunner() async {
    final phone = _order.runnerPhone ?? '9800000003';
    final uri = Uri.parse('tel:$phone');
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri);
    } else {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Calling delivery partner ($phone)...')),
        );
      }
    }
  }

  void _openChatWithPartner() {
    final state = AppStateProvider.of(context);
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (_) => OrderChatScreen(
          apiClient: state.apiClient,
          orderId: _order.id,
          currentRole: 'customer',
          partnerName: _order.runnerName ?? 'Delivery Partner',
          partnerPhone: _order.runnerPhone ?? '9800000003',
        ),
      ),
    );
  }

  String _getMonthName(int month, bool isHi) {
    const en = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const hi = ['', 'जनवरी', 'फ़रवरी', 'मार्च', 'अप्रैल', 'मई', 'जून', 'जुलाई', 'अगस्त', 'सितंबर', 'अक्टूबर', 'नवंबर', 'दिसंबर'];
    return isHi ? hi[month] : en[month];
  }

  String _formatTime(DateTime dt) {
    final hr = dt.hour > 12 ? dt.hour - 12 : (dt.hour == 0 ? 12 : dt.hour);
    final ampm = dt.hour >= 12 ? 'PM' : 'AM';
    return '$hr:${dt.minute.toString().padLeft(2, '0')} $ampm';
  }

  void _shareDeliveryLocation() {
    final loc = GBLocalizations.of(context);
    final isHi = loc.isHindi;
    final mapLink = 'https://www.google.com/maps/search/?api=1&query=${Uri.encodeComponent("${_order.deliveryAddress}, Minapur, Muzaffarpur, Bihar")}';

    Clipboard.setData(ClipboardData(text: mapLink));

    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
      builder: (ctx) => Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.share_location, color: GBColors.primary, size: 26),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    isHi ? 'डिलीवरी लोकेशन शेयर करें' : 'Share Delivery Location',
                    style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              isHi
                  ? 'डिलीवरी पार्टनर को सटीक ग्रामीण पते पर पहुँचने हेतु यह Google Maps लिंक शेयर करें:'
                  : 'Share this Google Maps directions link with your delivery partner for exact rural doorstep delivery:',
              style: const TextStyle(fontSize: 13, color: Colors.grey),
            ),
            const SizedBox(height: 14),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: GBColors.primary.withAlpha(20),
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: GBColors.primary.withAlpha(60)),
              ),
              child: Row(
                children: [
                  const Icon(Icons.link, color: GBColors.primary, size: 20),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      mapLink,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: GBColors.primary),
                    ),
                  ),
                  const SizedBox(width: 8),
                  const Icon(Icons.check_circle, color: GBColors.success, size: 18),
                ],
              ),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF25D366), foregroundColor: Colors.white),
                    icon: const Icon(Icons.message, size: 18),
                    label: Text(isHi ? 'व्हाट्सएप शेयर' : 'Share WhatsApp'),
                    onPressed: () {
                      Navigator.of(ctx).pop();
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(content: Text(isHi ? 'लोकेशन लिंक क्लिपबोर्ड पर कॉपी हो गया!' : 'Location link copied to clipboard!')),
                      );
                    },
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: OutlinedButton.icon(
                    icon: const Icon(Icons.copy, size: 18),
                    label: Text(isHi ? 'लिंक कॉपी करें' : 'Copy Link'),
                    onPressed: () {
                      Navigator.of(ctx).pop();
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(content: Text(isHi ? 'Google Maps लिंक कॉपी हो गया!' : 'Google Maps link copied!')),
                      );
                    },
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final loc = GBLocalizations.of(context);
    final isDark = Theme.of(context).brightness == Brightness.dark;

    final stages = [
      {'status': 'PLACED', 'label': loc.tr('order_status_placed')},
      {'status': 'ACCEPTED', 'label': loc.tr('order_status_accepted')},
      {'status': 'PACKED', 'label': loc.tr('order_status_packed')},
      {'status': 'RUNNER_ASSIGNED', 'label': loc.tr('order_status_assigned')},
      {'status': 'PICKED_UP', 'label': loc.tr('order_status_picked')},
      {'status': 'OUT_FOR_DELIVERY', 'label': loc.tr('order_status_out')},
      {'status': 'DELIVERED', 'label': loc.tr('order_status_delivered')},
    ];

    int currentStageIndex = 0;
    for (int i = 0; i < stages.length; i++) {
      if (stages[i]['status'] == _order.status) {
        currentStageIndex = i;
        break;
      }
    }
    if (_order.status == 'DELIVERED') currentStageIndex = 6;

    final isOutForDelivery = _order.status == 'OUT_FOR_DELIVERY' ||
        _order.status == 'RUNNER_ASSIGNED' ||
        _order.status == 'PICKED_UP';

    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          tooltip: loc.isHindi ? 'पीछे जाएं' : 'Back',
          onPressed: () => Navigator.of(context).pop(),
        ),
        title: Text(loc.tr('order_tracking'), style: const TextStyle(fontWeight: FontWeight.w800)),
      ),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // Order ID & Status Header Card
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
                        '${loc.tr('order_id')}${_order.id.length > 8 ? _order.id.substring(0, 8) : _order.id}',
                        style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                        decoration: BoxDecoration(
                          color: GBColors.primary.withAlpha(25),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Text(
                          _order.status,
                          style: const TextStyle(
                            color: GBColors.primary,
                            fontWeight: FontWeight.w800,
                            fontSize: 12,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text(
                    '${_order.storeName} • ${_order.deliveryAddress}',
                    style: TextStyle(
                      fontSize: 13,
                      color: isDark ? GBColors.textMutedDark : GBColors.textMutedLight,
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 16),

            // 4-Digit Delivery Verification PIN Card
            if (_order.status != 'DELIVERED' && _order.status != 'CANCELLED')
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: GBColors.primary.withAlpha(20),
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(color: GBColors.primary.withAlpha(80)),
                ),
                child: Column(
                  children: [
                    Text(
                      loc.tr('delivery_otp_code'),
                      style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13, color: GBColors.primary),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      _order.deliveryOtp,
                      style: const TextStyle(
                        fontSize: 32,
                        fontWeight: FontWeight.w900,
                        letterSpacing: 8,
                        color: GBColors.primary,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      loc.tr('show_otp_to_runner'),
                      textAlign: TextAlign.center,
                      style: const TextStyle(fontSize: 12, color: Colors.black87),
                    ),
                  ],
                ),
              ),

            const SizedBox(height: 16),

            // Real Customer - Runner Chat & Location Sharing Card
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
                    children: [
                      const Icon(Icons.chat_bubble_outline, color: GBColors.primary, size: 20),
                      const SizedBox(width: 8),
                      Text(
                        loc.isHindi ? 'डिलीवरी साथी से संपर्क एवं लाइव लोकेशन' : 'Contact Runner & Share Live Location',
                        style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 14),
                      ),
                    ],
                  ),
                  const SizedBox(height: 6),
                  Text(
                    loc.isHindi
                        ? 'सटीक घर/टोला पर डिलीवरी के लिए साथी को संदेश या वास्तविक जीपीएस पिन भेजें।'
                        : 'Chat with runner or share your exact live GPS pin for doorstep rural delivery.',
                    style: const TextStyle(fontSize: 12, color: Colors.grey),
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Expanded(
                        child: ElevatedButton.icon(
                          style: ElevatedButton.styleFrom(
                            backgroundColor: GBColors.primary,
                            foregroundColor: Colors.white,
                            padding: const EdgeInsets.symmetric(vertical: 11),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                          ),
                          icon: const Icon(Icons.chat, size: 17),
                          label: Text(
                            loc.isHindi ? 'साथी से चैट / जीपीएस पिन' : 'Chat & Share GPS Pin',
                            style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 12),
                          ),
                          onPressed: _openChatWithPartner,
                        ),
                      ),
                      const SizedBox(width: 8),
                      OutlinedButton.icon(
                        style: OutlinedButton.styleFrom(
                          foregroundColor: GBColors.primary,
                          side: const BorderSide(color: GBColors.primary),
                          padding: const EdgeInsets.symmetric(vertical: 11, horizontal: 12),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                        ),
                        icon: const Icon(Icons.phone_in_talk, size: 17),
                        label: Text(
                          loc.isHindi ? 'कॉल' : 'Call',
                          style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 12),
                        ),
                        onPressed: _callRunner,
                      ),
                    ],
                  ),
                ],
              ),
            ),

            if (isOutForDelivery) ...[
              const SizedBox(height: 16),
              // Assigned Runner Partner Info Card
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [
                      GBColors.primary.withOpacity(0.08),
                      GBColors.primary.withOpacity(0.03),
                    ],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(color: GBColors.primary.withOpacity(0.3)),
                ),
                child: Row(
                  children: [
                    Container(
                      width: 48,
                      height: 48,
                      decoration: const BoxDecoration(
                        color: GBColors.primary,
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(Icons.two_wheeler, color: Colors.white, size: 26),
                    ),
                    const SizedBox(width: 14),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            loc.isHindi ? 'डिलीवरी साथी: संतोष कुमार' : 'Delivery Partner: Santosh Kumar',
                            style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 14),
                          ),
                          const SizedBox(height: 2),
                          Text(
                            loc.isHindi ? 'हीरो स्प्लेंडर (BR-06-AB-1234) • ⭐ 4.9' : 'Hero Splendor (BR-06-AB-1234) • ⭐ 4.9',
                            style: const TextStyle(fontSize: 12, color: Colors.grey),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            loc.isHindi ? 'अनुमानित आगमन: 15-20 मिनट' : 'Estimated arrival: 15-20 mins',
                            style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: GBColors.primary),
                          ),
                        ],
                      ),
                    ),
                    IconButton(
                      icon: const Icon(Icons.phone_in_talk, color: GBColors.primary, size: 24),
                      onPressed: _callRunner,
                    ),
                  ],
                ),
              ),
            ],

            const SizedBox(height: 16),

            // Vertical Timeline of Order Lifecycle
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
                    'Timeline',
                    style: TextStyle(fontWeight: FontWeight.w800, fontSize: 15),
                  ),
                  const SizedBox(height: 16),
                  ...List.generate(stages.length, (index) {
                    final stage = stages[index];
                    final isCompleted = index <= currentStageIndex;
                    final isCurrent = index == currentStageIndex;
                    final label = stage['label'] as String;

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
                                color: isCompleted ? GBColors.primary : Colors.grey.withAlpha(60),
                              ),
                              child: isCompleted
                                  ? const Icon(Icons.check, size: 14, color: Colors.white)
                                  : null,
                            ),
                            if (index < stages.length - 1)
                              Container(
                                width: 2,
                                height: 32,
                                color: index < currentStageIndex ? GBColors.primary : Colors.grey.withAlpha(60),
                              ),
                          ],
                        ),
                        const SizedBox(width: 14),
                        Padding(
                          padding: const EdgeInsets.only(top: 2),
                          child: Text(
                            label,
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

            // Complete Itemized Order Details & Bill Summary Card
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
                        loc.isHindi ? 'ऑर्डर सामग्री एवं बिल विवरण' : 'Order Items & Bill Details',
                        style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 15),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                        decoration: BoxDecoration(
                          color: _order.paymentStatus == 'PAID'
                              ? GBColors.success.withAlpha(25)
                              : GBColors.warning.withAlpha(25),
                          borderRadius: BorderRadius.circular(6),
                        ),
                        child: Text(
                          _order.paymentStatus == 'PAID'
                              ? (loc.isHindi ? 'भुगतान संपन्न (PAID)' : 'PAID')
                              : (loc.isHindi ? 'भुगतान बकाया (PENDING)' : 'PENDING'),
                          style: TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.w800,
                            color: _order.paymentStatus == 'PAID' ? GBColors.success : GBColors.warning,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 10),
                  Text(
                    '${loc.isHindi ? "ऑर्डर का समय" : "Order Placed"}: ${_order.placedAt.day} ${_getMonthName(_order.placedAt.month, loc.isHindi)} ${_order.placedAt.year}, ${_formatTime(_order.placedAt)}',
                    style: TextStyle(fontSize: 12, color: isDark ? Colors.grey.shade400 : Colors.grey.shade700),
                  ),
                  const Divider(height: 18),
                  if (_order.items.isEmpty)
                    Padding(
                      padding: const EdgeInsets.symmetric(vertical: 8),
                      child: Text(
                        loc.isHindi ? 'किराना सामग्री पैक हो रही है' : 'Items being packed',
                        style: const TextStyle(fontSize: 13, color: Colors.grey),
                      ),
                    )
                  else
                    ..._order.items.map((item) {
                      return Padding(
                        padding: const EdgeInsets.symmetric(vertical: 4),
                        child: Row(
                          children: [
                            Container(
                              width: 24,
                              height: 24,
                              alignment: Alignment.center,
                              decoration: BoxDecoration(
                                color: GBColors.primary.withAlpha(25),
                                borderRadius: BorderRadius.circular(4),
                              ),
                              child: Text(
                                '${item.quantity}x',
                                style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: GBColors.primary),
                              ),
                            ),
                            const SizedBox(width: 10),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    loc.isHindi ? item.nameHi : item.nameEn,
                                    style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13),
                                  ),
                                  Text(
                                    '${item.unit} • ₹${item.unitPrice.toStringAsFixed(0)}',
                                    style: const TextStyle(fontSize: 11, color: Colors.grey),
                                  ),
                                ],
                              ),
                            ),
                            Text(
                              '₹${item.totalPrice.toStringAsFixed(0)}',
                              style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13),
                            ),
                          ],
                        ),
                      );
                    }),
                  const Divider(height: 18),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(loc.isHindi ? 'सामग्री उप-योग (Subtotal)' : 'Item Subtotal', style: const TextStyle(fontSize: 12)),
                      Text('₹${_order.subtotal.toStringAsFixed(0)}', style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600)),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(loc.isHindi ? 'डिलीवरी शुल्क' : 'Delivery Fee', style: const TextStyle(fontSize: 12)),
                      Text('₹${_order.deliveryFee.toStringAsFixed(0)}', style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600)),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(loc.isHindi ? 'प्लेटफ़ॉर्म शुल्क' : 'Platform Fee', style: const TextStyle(fontSize: 12)),
                      Text('₹${_order.platformFee.toStringAsFixed(0)}', style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600)),
                    ],
                  ),
                  const Divider(height: 16),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        loc.isHindi ? 'कुल राशि (Grand Total)' : 'Grand Total',
                        style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w800),
                      ),
                      Text(
                        '₹${_order.totalAmount.toStringAsFixed(0)}',
                        style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w900, color: GBColors.primary),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      Icon(
                        _order.paymentMethod == 'COD' ? Icons.payments_outlined : Icons.credit_card,
                        size: 16,
                        color: Colors.grey,
                      ),
                      const SizedBox(width: 6),
                      Text(
                        '${loc.isHindi ? "भुगतान विधि" : "Payment"}: ${_order.paymentMethod == "COD" ? (loc.isHindi ? "कैश ऑन डिलीवरी (COD)" : "Cash on Delivery (COD)") : "Online Payment"}',
                        style: const TextStyle(fontSize: 12, color: Colors.grey),
                      ),
                    ],
                  ),
                  if (_order.status == 'CANCELLED') ...[
                    const SizedBox(height: 8),
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: Colors.red.withAlpha(20),
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: Row(
                        children: [
                          const Icon(Icons.cancel, color: Colors.red, size: 16),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              _order.paymentStatus == 'REFUNDED'
                                  ? (loc.isHindi ? 'ऑर्डर रद्द: रिफ़ंड प्रक्रिया शुरू कर दी गई है।' : 'Order Cancelled: Refund initiated to original source.')
                                  : (loc.isHindi ? 'ऑर्डर रद्द कर दिया गया है।' : 'Order has been cancelled.'),
                              style: const TextStyle(fontSize: 12, color: Colors.red, fontWeight: FontWeight.bold),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ],
              ),
            ),

            const SizedBox(height: 16),

            // 180s Cancellation Section
            if (_order.status == 'PLACED' && _secondsRemaining > 0)
              Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: GBColors.warning.withAlpha(25),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: GBColors.warning.withAlpha(120)),
                ),
                child: Column(
                  children: [
                    Row(
                      children: [
                        const Icon(Icons.timer_outlined, color: GBColors.warning, size: 20),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            loc.isHindi
                                ? 'ऑर्डर रद्द करने के लिए शेष समय: ${_secondsRemaining} सेकंड'
                                : 'Time remaining to cancel: ${_secondsRemaining}s',
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

            // Contextual Contact Actions (Prioritizes Runner when Out for Delivery)
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: isOutForDelivery ? _callRunner : _callStore,
                    icon: const Icon(Icons.phone, size: 18),
                    label: Text(
                      isOutForDelivery ? loc.tr('call_runner') : loc.tr('call_store'),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: _openOrderHelpDialog,
                    icon: const Icon(Icons.help_outline, size: 18),
                    label: Text(
                      loc.tr('need_help'),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
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
}
