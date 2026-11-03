import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import 'package:localization/localization.dart';
import '../state/app_state.dart';

class TicketDetailsScreen extends StatefulWidget {
  final String ticketId;

  const TicketDetailsScreen({super.key, required this.ticketId});

  @override
  State<TicketDetailsScreen> createState() => _TicketDetailsScreenState();
}

class _TicketDetailsScreenState extends State<TicketDetailsScreen> {
  final TextEditingController _replyController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  Map<String, dynamic>? _ticket;
  List<dynamic> _messages = [];
  bool _isLoading = true;
  bool _isSendingReply = false;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _fetchDetails();
  }

  @override
  void dispose() {
    _replyController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  Future<void> _fetchDetails() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    final state = AppStateProvider.of(context);
    final res = await state.apiClient.getTicketDetails(widget.ticketId);

    if (!mounted) return;

    if (res.isSuccess && res.data != null) {
      setState(() {
        _ticket = res.data!;
        _messages = (_ticket!['messages'] as List?) ?? [];
        _isLoading = false;
      });
      _scrollToBottom();
    } else {
      setState(() {
        _isLoading = false;
        _errorMessage = res.errorMessage ?? 'Could not load ticket details';
      });
    }
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  Future<void> _sendReply() async {
    final text = _replyController.text.trim();
    if (text.isEmpty || _isSendingReply) return;

    setState(() => _isSendingReply = true);
    final state = AppStateProvider.of(context);
    final res = await state.apiClient.replyToTicket(widget.ticketId, text);

    if (!mounted) return;
    setState(() => _isSendingReply = false);

    if (res.isSuccess && res.data != null) {
      _replyController.clear();
      setState(() {
        _messages.add(res.data!);
        if (_ticket != null && _ticket!['status'] == 'CLOSED') {
          _ticket!['status'] = 'OPEN';
        }
      });
      _scrollToBottom();
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(res.errorMessage ?? 'Failed to send reply'),
          backgroundColor: GBColors.error,
        ),
      );
    }
  }

  Future<void> _toggleTicketStatus(String newStatus) async {
    final state = AppStateProvider.of(context);
    final res = await state.apiClient.updateCustomerTicketStatus(widget.ticketId, newStatus);
    if (!mounted) return;

    if (res.isSuccess) {
      setState(() {
        if (_ticket != null) _ticket!['status'] = newStatus;
      });
      final loc = GBLocalizations.of(context);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            newStatus == 'CLOSED'
                ? (loc.isHindi ? 'टिकट बंद कर दिया गया।' : 'Ticket closed.')
                : (loc.isHindi ? 'टिकट पुनः खोल दिया गया।' : 'Ticket reopened.'),
          ),
          backgroundColor: GBColors.success,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final loc = GBLocalizations.of(context);
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final isHi = loc.isHindi;

    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          tooltip: isHi ? 'पीछे जाएं' : 'Back',
          onPressed: () => Navigator.of(context).pop(),
        ),
        title: Text(
          isHi ? 'टिकट विवरण' : 'Ticket Conversation',
          style: const TextStyle(fontWeight: FontWeight.w800),
        ),
        actions: [
          if (_ticket != null && _ticket!['status'] == 'OPEN')
            TextButton(
              onPressed: () => _toggleTicketStatus('CLOSED'),
              child: Text(
                isHi ? 'टिकट बंद करें' : 'Close Ticket',
                style: const TextStyle(color: Colors.orange, fontWeight: FontWeight.bold),
              ),
            ),
          if (_ticket != null && _ticket!['status'] == 'CLOSED')
            TextButton(
              onPressed: () => _toggleTicketStatus('OPEN'),
              child: Text(
                isHi ? 'पुनः खोलें' : 'Reopen',
                style: const TextStyle(color: GBColors.primary, fontWeight: FontWeight.bold),
              ),
            ),
        ],
      ),
      body: SafeArea(
        child: _isLoading
            ? const Center(child: CircularProgressIndicator())
            : _errorMessage != null
                ? Center(
                    child: Padding(
                      padding: const EdgeInsets.all(24),
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          const Icon(Icons.error_outline, size: 48, color: GBColors.error),
                          const SizedBox(height: 12),
                          Text(
                            _errorMessage!,
                            textAlign: TextAlign.center,
                            style: const TextStyle(fontSize: 14),
                          ),
                          const SizedBox(height: 16),
                          ElevatedButton(
                            style: ElevatedButton.styleFrom(backgroundColor: GBColors.primary, foregroundColor: Colors.white),
                            onPressed: _fetchDetails,
                            child: Text(isHi ? 'पुनः प्रयास करें' : 'Retry'),
                          ),
                        ],
                      ),
                    ),
                  )
                : Column(
                    children: [
                      // Header Card
                      Container(
                        width: double.infinity,
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: isDark ? GBColors.cardDark : Colors.white,
                          border: Border(
                            bottom: BorderSide(
                              color: isDark ? GBColors.borderDark : GBColors.borderLight,
                            ),
                          ),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                  decoration: BoxDecoration(
                                    color: (_ticket!['status'] == 'OPEN'
                                            ? Colors.orange
                                            : (_ticket!['status'] == 'RESOLVED' ? GBColors.success : Colors.grey))
                                        .withAlpha(25),
                                    borderRadius: BorderRadius.circular(6),
                                  ),
                                  child: Text(
                                    _ticket!['status'] ?? 'OPEN',
                                    style: TextStyle(
                                      fontSize: 11,
                                      fontWeight: FontWeight.w800,
                                      color: _ticket!['status'] == 'OPEN'
                                          ? Colors.orange
                                          : (_ticket!['status'] == 'RESOLVED' ? GBColors.success : Colors.grey),
                                    ),
                                  ),
                                ),
                                const SizedBox(width: 8),
                                Expanded(
                                  child: Text(
                                    '#${_ticket!['id']?.toString().substring(0, 8) ?? ''}',
                                    style: const TextStyle(fontFamily: 'monospace', fontSize: 12, color: Colors.grey),
                                  ),
                                ),
                                if (_ticket!['order_id'] != null)
                                  Container(
                                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                                    decoration: BoxDecoration(
                                      color: GBColors.primary.withAlpha(15),
                                      borderRadius: BorderRadius.circular(6),
                                    ),
                                    child: Text(
                                      'Order: #${_ticket!['order_id']?.toString().substring(0, 8)}',
                                      style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: GBColors.primary),
                                    ),
                                  ),
                              ],
                            ),
                            const SizedBox(height: 8),
                            Text(
                              _ticket!['subject'] ?? '',
                              style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w800),
                            ),
                            if (_ticket!['resolution_notes'] != null && _ticket!['resolution_notes'].toString().isNotEmpty) ...[
                              const SizedBox(height: 8),
                              Container(
                                padding: const EdgeInsets.all(10),
                                decoration: BoxDecoration(
                                  color: GBColors.success.withAlpha(15),
                                  borderRadius: BorderRadius.circular(8),
                                  border: Border.all(color: GBColors.success.withAlpha(40)),
                                ),
                                child: Row(
                                  children: [
                                    const Icon(Icons.check_circle, size: 16, color: GBColors.success),
                                    const SizedBox(width: 8),
                                    Expanded(
                                      child: Text(
                                        '${isHi ? "समाधान: " : "Resolution: "}${_ticket!['resolution_notes']}',
                                        style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: GBColors.success),
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ],
                          ],
                        ),
                      ),

                      // Messages Stream
                      Expanded(
                        child: ListView.builder(
                          controller: _scrollController,
                          padding: const EdgeInsets.all(16),
                          itemCount: _messages.length,
                          itemBuilder: (context, index) {
                            final m = _messages[index];
                            final senderRole = m['sender_role'] as String? ?? 'customer';
                            final isAdmin = senderRole == 'admin' || senderRole == 'support';
                            final msgText = m['message'] as String? ?? '';
                            final timeStr = m['created_at'] != null && m['created_at'].toString().length >= 16
                                ? m['created_at'].toString().substring(11, 16)
                                : '';

                            return Align(
                              alignment: isAdmin ? Alignment.centerLeft : Alignment.centerRight,
                              child: Container(
                                margin: const EdgeInsets.only(bottom: 12),
                                constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.78),
                                padding: const EdgeInsets.all(12),
                                decoration: BoxDecoration(
                                  color: isAdmin
                                      ? (isDark ? GBColors.cardDark : Colors.grey.shade100)
                                      : GBColors.primary,
                                  borderRadius: BorderRadius.circular(14),
                                  border: isAdmin ? Border.all(color: isDark ? GBColors.borderDark : GBColors.borderLight) : null,
                                ),
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Row(
                                      mainAxisSize: MainAxisSize.min,
                                      children: [
                                        Icon(
                                          isAdmin ? Icons.support_agent : Icons.person,
                                          size: 13,
                                          color: isAdmin ? GBColors.primary : Colors.white70,
                                        ),
                                        const SizedBox(width: 4),
                                        Text(
                                          isAdmin ? (isHi ? 'सहायता प्रतिनिधि' : 'Support Specialist') : (isHi ? 'आप' : 'You'),
                                          style: TextStyle(
                                            fontSize: 10,
                                            fontWeight: FontWeight.w700,
                                            color: isAdmin ? GBColors.primary : Colors.white70,
                                          ),
                                        ),
                                        const SizedBox(width: 8),
                                        Text(
                                          timeStr,
                                          style: TextStyle(
                                            fontSize: 10,
                                            color: isAdmin ? Colors.grey : Colors.white60,
                                          ),
                                        ),
                                      ],
                                    ),
                                    const SizedBox(height: 6),
                                    Text(
                                      msgText,
                                      style: TextStyle(
                                        fontSize: 13,
                                        color: isAdmin ? (isDark ? Colors.white : Colors.black87) : Colors.white,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            );
                          },
                        ),
                      ),

                      // Reply Input Bar
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: isDark ? GBColors.cardDark : Colors.white,
                          border: Border(
                            top: BorderSide(
                              color: isDark ? GBColors.borderDark : GBColors.borderLight,
                            ),
                          ),
                        ),
                        child: Row(
                          children: [
                            Expanded(
                              child: TextField(
                                controller: _replyController,
                                decoration: InputDecoration(
                                  hintText: isHi ? 'उत्तर लिखें...' : 'Type a reply...',
                                  hintStyle: const TextStyle(fontSize: 13),
                                  contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                                  border: OutlineInputBorder(
                                    borderRadius: BorderRadius.circular(22),
                                    borderSide: BorderSide(color: isDark ? GBColors.borderDark : GBColors.borderLight),
                                  ),
                                ),
                              ),
                            ),
                            const SizedBox(width: 8),
                            _isSendingReply
                                ? const SizedBox(
                                    width: 36,
                                    height: 36,
                                    child: Padding(
                                      padding: EdgeInsets.all(8),
                                      child: CircularProgressIndicator(strokeWidth: 2),
                                    ),
                                  )
                                : IconButton(
                                    style: IconButton.styleFrom(
                                      backgroundColor: GBColors.primary,
                                      foregroundColor: Colors.white,
                                    ),
                                    icon: const Icon(Icons.send, size: 18),
                                    onPressed: _sendReply,
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
