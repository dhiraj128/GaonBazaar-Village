import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import 'package:localization/localization.dart';
import '../state/app_state.dart';
import 'order_tracking_screen.dart';
import 'ticket_details_screen.dart';

class SupportHubScreen extends StatefulWidget {
  const SupportHubScreen({super.key});

  @override
  State<SupportHubScreen> createState() => _SupportHubScreenState();
}

class _SupportHubScreenState extends State<SupportHubScreen> {
  final TextEditingController _chatController = TextEditingController();
  final List<Map<String, dynamic>> _chatMessages = [];
  List<Map<String, dynamic>> _myTickets = [];
  List<Map<String, dynamic>> _refundRecords = [];
  bool _isLoadingTickets = false;
  bool _isLoadingRefunds = false;
  bool _isChatLoading = false;
  String _selectedSection = 'WHERE_IS_ORDER'; // WHERE_IS_ORDER, REPORT_ISSUE, MY_TICKETS, REFUNDS, CONTACT

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final loc = GBLocalizations.of(context);
      _chatMessages.add({
        'isUser': false,
        'text': loc.isHindi
            ? 'नमस्ते! मैं गाँव बाज़ार सहायता सहायक हूँ। आप अपने हालिया ऑर्डर, रिफ़ंड, या सामान की समस्या के बारे में पूछ सकते हैं।'
            : 'Hello! I am your GaonBazaar Support Assistant. Ask about your orders, refunds, or product issues.',
      });
      _loadTickets();
      _loadRefunds();
      if (mounted) setState(() {});
    });
  }

  Future<void> _loadTickets() async {
    setState(() => _isLoadingTickets = true);
    final state = AppStateProvider.of(context);
    final res = await state.apiClient.getCustomerTickets();
    if (res.isSuccess && res.data != null) {
      _myTickets = res.data!;
    }
    if (mounted) setState(() => _isLoadingTickets = false);
  }

  Future<void> _loadRefunds() async {
    setState(() => _isLoadingRefunds = true);
    final state = AppStateProvider.of(context);
    final res = await state.apiClient.getRefundStatus();
    if (res.isSuccess && res.data != null) {
      _refundRecords = res.data!;
    }
    if (mounted) setState(() => _isLoadingRefunds = false);
  }

  Future<void> _handleChatSubmit(String query) async {
    final text = query.trim();
    if (text.isEmpty) return;

    setState(() {
      _chatMessages.add({'isUser': true, 'text': text});
      _isChatLoading = true;
    });
    _chatController.clear();

    final loc = GBLocalizations.of(context);
    final state = AppStateProvider.of(context);
    final res = await state.apiClient.querySupportAI(
      query: text,
      language: state.isHindi ? 'hi' : 'en',
    );

    if (!mounted) return;
    setState(() => _isChatLoading = false);

    if (res.isSuccess && res.data != null) {
      final reply = res.data!['reply'] as String? ?? 'Support team has recorded your inquiry.';
      setState(() {
        _chatMessages.add({'isUser': false, 'text': reply});
      });
    } else {
      setState(() {
        _chatMessages.add({'isUser': false, 'text': loc.tr('network_error')});
      });
    }
  }

  void _openCreateTicketDialog({String? preselectedOrderId}) {
    final loc = GBLocalizations.of(context);
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final state = AppStateProvider.of(context);
    final isHi = loc.isHindi;

    final categories = [
      {'id': 'DELAYED_DELIVERY', 'title': isHi ? 'डिलीवरी में देरी (Delayed Delivery)' : 'Delayed Delivery'},
      {'id': 'MISSING_ITEM', 'title': isHi ? 'सामान कम मिला (Missing Item)' : 'Missing Item'},
      {'id': 'DAMAGED_ITEM', 'title': isHi ? 'सामान खराब या टूटा (Damaged Item)' : 'Damaged Item'},
      {'id': 'WRONG_ITEM', 'title': isHi ? 'गलत सामान मिला (Wrong Product)' : 'Wrong Product'},
      {'id': 'REFUND_REQUEST', 'title': isHi ? 'रिफ़ंड पूछताछ (Refund Inquiry)' : 'Refund Inquiry'},
      {'id': 'GENERAL_HELP', 'title': isHi ? 'अन्य सहायता (General Assistance)' : 'General Assistance'},
    ];

    String selectedCategory = categories[0]['id']!;
    String? selectedOrderId = preselectedOrderId ?? (state.orders.isNotEmpty ? state.orders.first.id : null);
    final subjectCtrl = TextEditingController(text: categories[0]['title']);
    final messageCtrl = TextEditingController();
    bool isSubmitting = false;

    showDialog(
      context: context,
      builder: (ctx) {
        return StatefulBuilder(
          builder: (dialogCtx, setDialogState) {
            return AlertDialog(
              backgroundColor: isDark ? GBColors.surfaceDark : Colors.white,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
              title: Text(
                isHi ? 'समस्या दर्ज करें' : 'Report an Issue',
                style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16),
              ),
              content: SingleChildScrollView(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Order selection
                    if (state.orders.isNotEmpty) ...[
                      Text(isHi ? 'संबंधित ऑर्डर' : 'Related Order', style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 12)),
                      const SizedBox(height: 6),
                      DropdownButtonFormField<String>(
                        value: selectedOrderId,
                        isExpanded: true,
                        decoration: InputDecoration(
                          border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                          contentPadding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                        ),
                        items: [
                          DropdownMenuItem<String>(
                            value: null,
                            child: Text(isHi ? 'कोई ऑर्डर नहीं (सामान्य)' : 'No specific order', style: const TextStyle(fontSize: 12)),
                          ),
                          ...state.orders.map((o) => DropdownMenuItem(
                                value: o.id,
                                child: Text('Order #${o.id.substring(0, o.id.length > 8 ? 8 : o.id.length)} (₹${o.totalAmount.toStringAsFixed(0)})', style: const TextStyle(fontSize: 12)),
                              )),
                        ],
                        onChanged: (val) => setDialogState(() => selectedOrderId = val),
                      ),
                      const SizedBox(height: 12),
                    ],

                    // Category selection
                    Text(isHi ? 'समस्या का प्रकार' : 'Issue Category', style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 12)),
                    const SizedBox(height: 6),
                    DropdownButtonFormField<String>(
                      value: selectedCategory,
                      isExpanded: true,
                      decoration: InputDecoration(
                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                        contentPadding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                      ),
                      items: categories
                          .map((c) => DropdownMenuItem(
                                value: c['id']!,
                                child: Text(c['title']!, style: const TextStyle(fontSize: 12)),
                              ))
                          .toList(),
                      onChanged: (val) {
                        if (val != null) {
                          setDialogState(() {
                            selectedCategory = val;
                            final matched = categories.firstWhere((c) => c['id'] == val);
                            subjectCtrl.text = matched['title']!;
                          });
                        }
                      },
                    ),
                    const SizedBox(height: 12),

                    // Detailed message
                    Text(isHi ? 'विवरण' : 'Description', style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 12)),
                    const SizedBox(height: 6),
                    TextField(
                      controller: messageCtrl,
                      maxLines: 3,
                      decoration: InputDecoration(
                        hintText: isHi ? 'समस्या का पूरा विवरण लिखें...' : 'Describe what happened in detail...',
                        hintStyle: const TextStyle(fontSize: 12),
                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                        contentPadding: const EdgeInsets.all(10),
                      ),
                    ),
                  ],
                ),
              ),
              actions: [
                TextButton(
                  onPressed: isSubmitting ? null : () => Navigator.of(ctx).pop(),
                  child: Text(isHi ? 'रद्द करें' : 'Cancel'),
                ),
                ElevatedButton(
                  style: ElevatedButton.styleFrom(backgroundColor: GBColors.primary, foregroundColor: Colors.white),
                  onPressed: isSubmitting
                      ? null
                      : () async {
                          final msg = messageCtrl.text.trim();
                          if (msg.isEmpty) return;

                          setDialogState(() => isSubmitting = true);
                          final res = await state.apiClient.createSupportTicket(
                            orderId: selectedOrderId,
                            category: selectedCategory,
                            subject: subjectCtrl.text.trim(),
                            message: msg,
                          );
                          setDialogState(() => isSubmitting = false);

                          if (res.isSuccess && mounted) {
                            Navigator.of(ctx).pop();
                            ScaffoldMessenger.of(context).showSnackBar(
                              SnackBar(
                                content: Text(
                                  isHi
                                      ? 'सहायता टिकट #${res.data!['id']?.toString().substring(0, 8)} सफलतापूर्वक दर्ज हुआ।'
                                      : 'Support ticket #${res.data!['id']?.toString().substring(0, 8)} created successfully.',
                                ),
                                backgroundColor: GBColors.success,
                              ),
                            );
                            _loadTickets();
                          } else if (mounted) {
                            ScaffoldMessenger.of(context).showSnackBar(
                              SnackBar(
                                content: Text(res.errorMessage ?? (isHi ? 'टिकट दर्ज नहीं हो सका।' : 'Failed to create ticket.')),
                                backgroundColor: GBColors.error,
                              ),
                            );
                          }
                        },
                  child: isSubmitting
                      ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                      : Text(isHi ? 'टिकट भेजें' : 'Submit Ticket'),
                ),
              ],
            );
          },
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final loc = GBLocalizations.of(context);
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final isHi = loc.isHindi;
    final state = AppStateProvider.of(context);

    // Get active order if any
    final activeOrders = state.orders.where((o) => o.status != 'DELIVERED' && o.status != 'CANCELLED').toList();
    final latestActive = activeOrders.isNotEmpty ? activeOrders.first : null;

    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          tooltip: isHi ? 'पीछे जाएं' : 'Back',
          onPressed: () => Navigator.of(context).pop(),
        ),
        title: Text(
          isHi ? 'सहायता केंद्र' : 'Customer Support Hub',
          style: const TextStyle(fontWeight: FontWeight.w800),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            tooltip: isHi ? 'ताज़ा करें' : 'Refresh',
            onPressed: () {
              _loadTickets();
              _loadRefunds();
            },
          ),
        ],
      ),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          children: [
            // Quick Navigation Filter Pills
            SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                children: [
                  _buildNavPill(
                    id: 'WHERE_IS_ORDER',
                    icon: Icons.local_shipping_outlined,
                    label: isHi ? 'ऑर्डर ट्रैकिंग' : 'Track Order',
                  ),
                  const SizedBox(width: 8),
                  _buildNavPill(
                    id: 'REPORT_ISSUE',
                    icon: Icons.report_problem_outlined,
                    label: isHi ? 'समस्या दर्ज करें' : 'Report Issue',
                  ),
                  const SizedBox(width: 8),
                  _buildNavPill(
                    id: 'MY_TICKETS',
                    icon: Icons.confirmation_number_outlined,
                    label: isHi ? 'मेरे टिकट (${_myTickets.length})' : 'My Tickets (${_myTickets.length})',
                  ),
                  const SizedBox(width: 8),
                  _buildNavPill(
                    id: 'REFUNDS',
                    icon: Icons.currency_rupee_outlined,
                    label: isHi ? 'रिफ़ंड स्थिति' : 'Refund Status',
                  ),
                  const SizedBox(width: 8),
                  _buildNavPill(
                    id: 'CONTACT',
                    icon: Icons.headset_mic_outlined,
                    label: isHi ? 'सीधा संपर्क' : 'Contact Us',
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // 1. Where Is My Order Active Banner
            if (latestActive != null) ...[
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: GBColors.primary.withAlpha(15),
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(color: GBColors.primary.withAlpha(40)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        const Icon(Icons.delivery_dining, color: GBColors.primary, size: 24),
                        const SizedBox(width: 8),
                        Text(
                          isHi ? 'सक्रिय ऑर्डर प्रगति' : 'Active Order Progress',
                          style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 15, color: GBColors.primary),
                        ),
                        const Spacer(),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                          decoration: BoxDecoration(color: GBColors.primary, borderRadius: BorderRadius.circular(6)),
                          child: Text(
                            latestActive.status,
                            style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: Colors.white),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Text(
                      '${isHi ? "ऑर्डर" : "Order"} #${latestActive.id.substring(0, latestActive.id.length > 8 ? 8 : latestActive.id.length)} • ₹${latestActive.totalAmount.toStringAsFixed(0)} • ${latestActive.items.length} ${isHi ? "सामान" : "items"}',
                      style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600),
                    ),
                    if (latestActive.deliveryOtp.isNotEmpty) ...[
                      const SizedBox(height: 4),
                      Text(
                        '${isHi ? "डिलीवरी पिन: " : "Delivery PIN: "}${latestActive.deliveryOtp}',
                        style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: GBColors.primary),
                      ),
                    ],
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        Expanded(
                          child: ElevatedButton.icon(
                            style: ElevatedButton.styleFrom(
                              backgroundColor: GBColors.primary,
                              foregroundColor: Colors.white,
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                            ),
                            icon: const Icon(Icons.navigation, size: 16),
                            label: Text(isHi ? 'लाइव ट्रैकिंग देखें' : 'Track Live', style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
                            onPressed: () {
                              Navigator.of(context).push(
                                MaterialPageRoute(builder: (_) => OrderTrackingScreen(order: latestActive)),
                              );
                            },
                          ),
                        ),
                        const SizedBox(width: 10),
                        OutlinedButton(
                          style: OutlinedButton.styleFrom(
                            side: const BorderSide(color: GBColors.primary),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                          ),
                          onPressed: () => _openCreateTicketDialog(preselectedOrderId: latestActive.id),
                          child: Text(isHi ? 'शिकायत करें' : 'Complain', style: const TextStyle(fontSize: 12, color: GBColors.primary)),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),
            ],

            // 2. Action Hub: Report Issue & AI Chat Section
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
                    children: [
                      Container(
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: GBColors.primary.withAlpha(25),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: const Icon(Icons.smart_toy_outlined, color: GBColors.primary, size: 22),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              isHi ? 'गाँव बाज़ार स्मार्ट सहायता' : 'GaonBazaar Smart Assistant',
                              style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 14),
                            ),
                            Text(
                              isHi ? 'ऑर्डर, रिफ़ंड व नियमों की त्वरित जानकारी' : 'Quick answers on tracking, items & refunds',
                              style: TextStyle(fontSize: 11, color: isDark ? GBColors.textMutedDark : GBColors.textMutedLight),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),

                  // Chat Message Feed
                  Container(
                    height: 150,
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: isDark ? GBColors.surfaceDark : GBColors.surfaceLight,
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: ListView.builder(
                      itemCount: _chatMessages.length,
                      itemBuilder: (context, index) {
                        final msg = _chatMessages[index];
                        final isUser = msg['isUser'] as bool;
                        return Align(
                          alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
                          child: Container(
                            margin: const EdgeInsets.only(bottom: 8),
                            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                            decoration: BoxDecoration(
                              color: isUser ? GBColors.primary : (isDark ? GBColors.cardDark : Colors.white),
                              borderRadius: BorderRadius.circular(12),
                              border: isUser ? null : Border.all(color: Colors.grey.withAlpha(40)),
                            ),
                            child: Text(
                              msg['text'] as String,
                              style: TextStyle(
                                fontSize: 12,
                                color: isUser ? Colors.white : (isDark ? Colors.white : Colors.black87),
                              ),
                            ),
                          ),
                        );
                      },
                    ),
                  ),

                  if (_isChatLoading)
                    const Padding(
                      padding: EdgeInsets.symmetric(vertical: 4),
                      child: Center(child: SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: GBColors.primary))),
                    ),

                  const SizedBox(height: 8),

                  // Quick AI Prompts
                  Wrap(
                    spacing: 6,
                    children: [
                      ActionChip(
                        label: Text(isHi ? 'मेरा ऑर्डर कहाँ है?' : 'Where is my order?', style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600)),
                        onPressed: () => _handleChatSubmit(isHi ? 'मेरा ऑर्डर कहाँ है?' : 'Where is my order?'),
                      ),
                      ActionChip(
                        label: Text(isHi ? 'सामान कम मिला' : 'Missing item', style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600)),
                        onPressed: () => _handleChatSubmit(isHi ? 'सामान कम मिला' : 'Missing item'),
                      ),
                      ActionChip(
                        label: Text(isHi ? 'रिफ़ंड नियम' : 'Refund rules', style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600)),
                        onPressed: () => _handleChatSubmit(isHi ? 'रिफ़ंड नियम क्या हैं?' : 'What are the refund rules?'),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),

                  // Chat Input Bar
                  Row(
                    children: [
                      Expanded(
                        child: TextField(
                          controller: _chatController,
                          onSubmitted: _handleChatSubmit,
                          decoration: InputDecoration(
                            hintText: isHi ? 'सहायता से सवाल पूछें...' : 'Ask support a question...',
                            hintStyle: const TextStyle(fontSize: 12),
                            border: OutlineInputBorder(borderRadius: BorderRadius.circular(20)),
                            contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                          ),
                        ),
                      ),
                      const SizedBox(width: 8),
                      IconButton(
                        icon: const Icon(Icons.send, color: GBColors.primary, size: 20),
                        onPressed: () => _handleChatSubmit(_chatController.text),
                      ),
                    ],
                  ),
                ],
              ),
            ),

            const SizedBox(height: 14),

            // Report Issue Action Button
            SizedBox(
              width: double.infinity,
              height: 46,
              child: ElevatedButton.icon(
                style: ElevatedButton.styleFrom(
                  backgroundColor: GBColors.primary,
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
                icon: const Icon(Icons.add_comment_outlined, size: 20),
                label: Text(
                  isHi ? 'नई शिकायत / समस्या दर्ज करें' : 'Report an Issue / New Ticket',
                  style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 14),
                ),
                onPressed: () => _openCreateTicketDialog(),
              ),
            ),

            const SizedBox(height: 20),

            // 3. My Support Tickets Section
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  isHi ? 'मेरे सहायता टिकट' : 'My Support Tickets',
                  style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w800),
                ),
                TextButton(
                  onPressed: _loadTickets,
                  child: Text(isHi ? 'रिफ्रेश' : 'Refresh', style: const TextStyle(fontSize: 12)),
                ),
              ],
            ),
            const SizedBox(height: 6),
            if (_isLoadingTickets)
              const Center(child: Padding(padding: EdgeInsets.all(16), child: CircularProgressIndicator()))
            else if (_myTickets.isEmpty)
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: isDark ? GBColors.cardDark : Colors.white,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: isDark ? GBColors.borderDark : GBColors.borderLight),
                ),
                child: Center(
                  child: Column(
                    children: [
                      const Icon(Icons.check_circle_outline, size: 36, color: Colors.grey),
                      const SizedBox(height: 6),
                      Text(
                        isHi ? 'कोई खुला टिकट नहीं है।' : 'No active support tickets.',
                        style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        isHi ? 'यदि किसी ऑर्डर में समस्या हो तो ऊपर बटन से टिकट बनाएं।' : 'Use Report an Issue above if you need help with any order.',
                        style: const TextStyle(fontSize: 11, color: Colors.grey),
                      ),
                    ],
                  ),
                ),
              )
            else
              ...List.generate(_myTickets.length, (i) {
                final t = _myTickets[i];
                final status = (t['status'] as String? ?? 'OPEN').toUpperCase();
                final replyCount = (t['reply_count'] as num?)?.toInt() ?? 1;

                return InkWell(
                  onTap: () {
                    final ticketId = t['id']?.toString() ?? '';
                    if (ticketId.isNotEmpty) {
                      Navigator.of(context)
                          .push(
                            MaterialPageRoute(
                              builder: (_) => TicketDetailsScreen(ticketId: ticketId),
                            ),
                          )
                          .then((_) => _loadTickets());
                    }
                  },
                  borderRadius: BorderRadius.circular(12),
                  child: Container(
                    margin: const EdgeInsets.only(bottom: 10),
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(
                      color: isDark ? GBColors.cardDark : Colors.white,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: isDark ? GBColors.borderDark : GBColors.borderLight),
                    ),
                    child: Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                          decoration: BoxDecoration(
                            color: status == 'OPEN'
                                ? Colors.orange.withAlpha(25)
                                : (status == 'RESOLVED' ? GBColors.success.withAlpha(25) : Colors.grey.withAlpha(25)),
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: Text(
                            status,
                            style: TextStyle(
                              fontSize: 10,
                              fontWeight: FontWeight.w800,
                              color: status == 'OPEN'
                                  ? Colors.orange
                                  : (status == 'RESOLVED' ? GBColors.success : Colors.grey),
                            ),
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(t['subject'] as String? ?? 'Support Ticket', style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13)),
                              const SizedBox(height: 2),
                              Text(
                                t['message'] as String? ?? '',
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                                style: const TextStyle(fontSize: 11, color: Colors.grey),
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(width: 8),
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.end,
                          children: [
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                              decoration: BoxDecoration(
                                color: Colors.grey.withAlpha(25),
                                borderRadius: BorderRadius.circular(10),
                              ),
                              child: Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  const Icon(Icons.chat_bubble_outline, size: 11, color: Colors.grey),
                                  const SizedBox(width: 3),
                                  Text('$replyCount', style: const TextStyle(fontSize: 10, color: Colors.grey)),
                                ],
                              ),
                            ),
                            const SizedBox(height: 4),
                            const Icon(Icons.arrow_forward_ios, size: 12, color: Colors.grey),
                          ],
                        ),
                      ],
                    ),
                  ),
                );
              }),

            const SizedBox(height: 20),

            // 4. Refund & Replacement Status Section
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  isHi ? 'रिफ़ंड एवं रिप्लेसमेंट स्थिति' : 'Refund & Replacement Records',
                  style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w800),
                ),
                TextButton(
                  onPressed: _loadRefunds,
                  child: Text(isHi ? 'रिफ्रेश' : 'Refresh', style: const TextStyle(fontSize: 12)),
                ),
              ],
            ),
            const SizedBox(height: 6),
            if (_isLoadingRefunds)
              const Center(child: Padding(padding: EdgeInsets.all(12), child: CircularProgressIndicator()))
            else if (_refundRecords.isEmpty)
              Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: isDark ? GBColors.cardDark : Colors.white,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: isDark ? GBColors.borderDark : GBColors.borderLight),
                ),
                child: Center(
                  child: Text(
                    isHi ? 'कोई लंबित रिफ़ंड या विवादित ऑर्डर नहीं है।' : 'No pending refunds or disputed orders.',
                    style: TextStyle(fontSize: 12, color: isDark ? GBColors.textMutedDark : GBColors.textMutedLight),
                  ),
                ),
              )
            else
              ..._refundRecords.map((r) => Container(
                    margin: const EdgeInsets.only(bottom: 8),
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: isDark ? GBColors.cardDark : Colors.white,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: isDark ? GBColors.borderDark : GBColors.borderLight),
                    ),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Order #${r['order_id']?.toString().substring(0, 8)}',
                              style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 13),
                            ),
                            Text(
                              r['reason'] ?? 'Cancellation refund',
                              style: const TextStyle(fontSize: 11, color: Colors.grey),
                            ),
                          ],
                        ),
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.end,
                          children: [
                            Text(
                              '₹${r['refund_amount']}',
                              style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 14, color: GBColors.primary),
                            ),
                            Text(
                              r['status'] ?? 'PROCESSED',
                              style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: GBColors.success),
                            ),
                          ],
                        ),
                      ],
                    ),
                  )),

            const SizedBox(height: 20),

            // 5. Authentic Minapur Contact Support
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
                    children: [
                      const Icon(Icons.hub_outlined, color: GBColors.primary, size: 20),
                      const SizedBox(width: 8),
                      Text(
                        isHi ? 'मीनापुर परिचालन सहायता केंद्र' : 'Minapur Operational Support Hub',
                        style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 14),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text(
                    isHi
                        ? 'पता: ग्राम पंचायत भवन के पास, चतुरसी, मीनापुर ब्लॉक, मुजफ्फरपुर, बिहार - 843128'
                        : 'Location: Near Gram Panchayat Bhavan, Chaturshi, Minapur Block, Muzaffarpur, Bihar - 843128',
                    style: TextStyle(fontSize: 12, color: isDark ? Colors.white70 : Colors.black87),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    isHi
                        ? 'ईमेल: support@gaonbazaar.in • कार्य समय: सोम-रवि, प्रातः 07:00 से रात्रि 09:00 बजे'
                        : 'Email: support@gaonbazaar.in • Hours: Mon - Sun, 07:00 AM - 09:00 PM IST',
                    style: const TextStyle(fontSize: 11, color: Colors.grey),
                  ),
                  const SizedBox(height: 10),
                  Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: Colors.blue.withAlpha(15),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: Colors.blue.withAlpha(40)),
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.info_outline, size: 16, color: Colors.blue),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            isHi
                                ? 'फ़ोन हेल्पलाइन केवल दिन के कार्य समय (7:00 AM - 9:00 PM) में चालू रहती है। आपातकालीन सहायता हेतु ऊपर टिकट दर्ज करें।'
                                : 'Phone helpline operates during cluster daytime hours (7:00 AM - 9:00 PM IST). For immediate tracking, use the in-app ticket above.',
                            style: const TextStyle(fontSize: 11, color: Colors.blue),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),
          ],
        ),
      ),
    );
  }

  Widget _buildNavPill({
    required String id,
    required IconData icon,
    required String label,
  }) {
    final isSelected = _selectedSection == id;
    return InkWell(
      onTap: () {
        setState(() => _selectedSection = id);
        if (id == 'REPORT_ISSUE') {
          _openCreateTicketDialog();
        } else if (id == 'MY_TICKETS') {
          _loadTickets();
        } else if (id == 'REFUNDS') {
          _loadRefunds();
        }
      },
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        decoration: BoxDecoration(
          color: isSelected ? GBColors.primary : (Theme.of(context).brightness == Brightness.dark ? GBColors.cardDark : Colors.white),
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: isSelected ? GBColors.primary : Colors.grey.withAlpha(60)),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 14, color: isSelected ? Colors.white : GBColors.primary),
            const SizedBox(width: 6),
            Text(
              label,
              style: TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.w700,
                color: isSelected ? Colors.white : (Theme.of(context).brightness == Brightness.dark ? Colors.white : Colors.black87),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
