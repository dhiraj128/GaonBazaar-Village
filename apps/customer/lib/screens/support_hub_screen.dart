import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import 'package:localization/localization.dart';
import '../state/app_state.dart';

class SupportHubScreen extends StatefulWidget {
  const SupportHubScreen({super.key});

  @override
  State<SupportHubScreen> createState() => _SupportHubScreenState();
}

class _SupportHubScreenState extends State<SupportHubScreen> {
  final TextEditingController _chatController = TextEditingController();
  final List<Map<String, dynamic>> _chatMessages = [];
  List<Map<String, dynamic>> _myTickets = [];
  bool _isLoadingTickets = false;
  bool _isChatLoading = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final loc = GBLocalizations.of(context);
      _chatMessages.add({
        'isUser': false,
        'text': loc.isHindi
            ? 'नमस्ते! मैं गाँव बाज़ार ग्राहक सहायता सहायक हूँ। आप मुझसे अपने ऑर्डर की स्थिति, गुम सामान, या रिफ़ंड नीति के बारे में पूछ सकते हैं।'
            : 'Hello! I am your GaonBazaar Customer Support Assistant. Ask me about your order status, missing items, or refund guidelines.',
      });
      _loadTickets();
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
      final reply = res.data!['reply'] as String? ?? 'Support team has been alerted.';
      setState(() {
        _chatMessages.add({'isUser': false, 'text': reply});
      });
    } else {
      setState(() {
        _chatMessages.add({'isUser': false, 'text': loc.tr('network_error')});
      });
    }
  }

  void _openCreateTicketDialog() {
    final loc = GBLocalizations.of(context);
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final state = AppStateProvider.of(context);

    final subjects = [
      loc.isHindi ? 'डिलीवरी में देरी (Delayed delivery)' : 'Delayed delivery',
      loc.isHindi ? 'सामान कम मिला (Missing item)' : 'Missing item',
      loc.isHindi ? 'गलत सामान मिला (Wrong item)' : 'Wrong item',
      loc.isHindi ? 'सामान खराब या टूटा मिला (Damaged item)' : 'Damaged item',
      loc.isHindi ? 'भुगतान समस्या (Payment issue)' : 'Payment issue',
      loc.isHindi ? 'खाता या ऐप समस्या (Account issue)' : 'Account issue',
    ];

    String selectedSubject = subjects[0];
    final messageController = TextEditingController();
    bool isSubmitting = false;

    showDialog(
      context: context,
      builder: (ctx) {
        return StatefulBuilder(
          builder: (dialogCtx, setDialogState) {
            return AlertDialog(
              backgroundColor: isDark ? GBColors.surfaceDark : Colors.white,
              title: Text(loc.tr('report_an_issue'), style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16)),
              content: SingleChildScrollView(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(loc.tr('ticket_subject'), style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13)),
                    const SizedBox(height: 6),
                    DropdownButtonFormField<String>(
                      initialValue: selectedSubject,
                      isExpanded: true,
                      decoration: InputDecoration(
                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                        contentPadding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                      ),
                      items: subjects.map((s) => DropdownMenuItem(value: s, child: Text(s, style: const TextStyle(fontSize: 12)))).toList(),
                      onChanged: (val) {
                        if (val != null) setDialogState(() => selectedSubject = val);
                      },
                    ),
                    const SizedBox(height: 14),
                    Text(loc.tr('ticket_message'), style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13)),
                    const SizedBox(height: 6),
                    TextField(
                      controller: messageController,
                      maxLines: 3,
                      decoration: InputDecoration(
                        hintText: loc.isHindi ? 'अपनी समस्या विस्तार से लिखें...' : 'Describe your issue in detail...',
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
                  style: ElevatedButton.styleFrom(backgroundColor: GBColors.primary, foregroundColor: Colors.white),
                  onPressed: isSubmitting
                      ? null
                      : () async {
                          final msg = messageController.text.trim();
                          if (msg.isEmpty) return;

                          final messenger = ScaffoldMessenger.of(context);
                          final nav = Navigator.of(ctx);
                          final successText = loc.tr('ticket_created_success');

                          setDialogState(() => isSubmitting = true);
                          final res = await state.apiClient.createSupportTicket(
                            subject: selectedSubject,
                            message: msg,
                          );
                          setDialogState(() => isSubmitting = false);

                          if (res.isSuccess) {
                            nav.pop();
                            messenger.showSnackBar(
                              SnackBar(content: Text(successText)),
                            );
                            _loadTickets();
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

  @override
  Widget build(BuildContext context) {
    final loc = GBLocalizations.of(context);
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          tooltip: loc.isHindi ? 'पीछे जाएं' : 'Back',
          onPressed: () => Navigator.of(context).pop(),
        ),
        title: Text(loc.tr('support_hub_title'), style: const TextStyle(fontWeight: FontWeight.w800)),
      ),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          children: [
            // 1. AI Support Chat Card
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
                        child: const Icon(Icons.support_agent, color: GBColors.primary, size: 22),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(loc.tr('support_ai_chat'), style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 14)),
                            Text(loc.tr('support_ai_subtitle'), style: TextStyle(fontSize: 11, color: isDark ? GBColors.textMutedDark : GBColors.textMutedLight)),
                          ],
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 14),

                  // Chat Message Feed
                  Container(
                    height: 180,
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

                  const SizedBox(height: 10),

                  // Quick AI Prompts
                  Wrap(
                    spacing: 6,
                    children: [
                      ActionChip(
                        label: Text(loc.tr('where_is_my_order'), style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600)),
                        onPressed: () => _handleChatSubmit(loc.tr('where_is_my_order')),
                      ),
                      ActionChip(
                        label: Text(loc.isHindi ? 'सामान कम मिला' : 'Missing item', style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600)),
                        onPressed: () => _handleChatSubmit(loc.isHindi ? 'सामान कम मिला' : 'Missing item'),
                      ),
                    ],
                  ),
                  const SizedBox(height: 10),

                  // Chat Input Bar
                  Row(
                    children: [
                      Expanded(
                        child: TextField(
                          controller: _chatController,
                          onSubmitted: _handleChatSubmit,
                          decoration: InputDecoration(
                            hintText: loc.isHindi ? 'सहायता से सवाल पूछें...' : 'Ask support a question...',
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

            const SizedBox(height: 16),

            // 2. Report Issue Button
            GBPrimaryButton(
              label: loc.tr('report_an_issue'),
              onPressed: _openCreateTicketDialog,
            ),

            const SizedBox(height: 20),

            // 3. My Support Tickets Section
            Text(
              loc.tr('my_support_tickets'),
              style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w800),
            ),
            const SizedBox(height: 10),
            if (_isLoadingTickets)
              const Center(child: Padding(padding: EdgeInsets.all(16), child: GBLoadingState()))
            else if (_myTickets.isEmpty)
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: isDark ? GBColors.cardDark : Colors.white,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: isDark ? GBColors.borderDark : GBColors.borderLight),
                ),
                child: Center(
                  child: Text(
                    loc.isHindi ? 'अभी कोई सहायता टिकट दर्ज नहीं है।' : 'No support tickets raised yet.',
                    style: TextStyle(fontSize: 12, color: isDark ? GBColors.textMutedDark : GBColors.textMutedLight),
                  ),
                ),
              )
            else
              ...List.generate(_myTickets.length, (i) {
                final t = _myTickets[i];
                final status = t['status'] as String? ?? 'OPEN';
                return Container(
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
                          color: status == 'OPEN' ? Colors.orange.withAlpha(30) : GBColors.primary.withAlpha(30),
                          borderRadius: BorderRadius.circular(6),
                        ),
                        child: Text(
                          status,
                          style: TextStyle(
                            fontSize: 10,
                            fontWeight: FontWeight.w800,
                            color: status == 'OPEN' ? Colors.orange : GBColors.primary,
                          ),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(t['subject'] as String? ?? 'Ticket', style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13)),
                            const SizedBox(height: 2),
                            Text(t['message'] as String? ?? '', maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 11, color: Colors.grey)),
                          ],
                        ),
                      ),
                    ],
                  ),
                );
              }),

            const SizedBox(height: 16),

            // Emergency Support Contact
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: GBColors.primary.withAlpha(15),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: GBColors.primary.withAlpha(50)),
              ),
              child: Row(
                children: [
                  const Icon(Icons.phone_in_talk, color: GBColors.primary, size: 20),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      loc.tr('call_emergency_support'),
                      style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: GBColors.primary),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
