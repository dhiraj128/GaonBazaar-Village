import 'dart:async';
import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import 'package:shared_models/shared_models.dart';
import 'package:api_client/api_client.dart';
import 'package:url_launcher/url_launcher.dart';

class OrderChatScreen extends StatefulWidget {
  final GBApiClient apiClient;
  final String orderId;
  final String currentRole; // 'customer' or 'runner'
  final String partnerName;
  final String? partnerPhone;

  const OrderChatScreen({
    super.key,
    required this.apiClient,
    required this.orderId,
    required this.currentRole,
    required this.partnerName,
    this.partnerPhone,
  });

  @override
  State<OrderChatScreen> createState() => _OrderChatScreenState();
}

class _OrderChatScreenState extends State<OrderChatScreen> {
  final TextEditingController _msgController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  List<GBOrderMessage> _messages = [];
  bool _isLoading = true;
  bool _isSending = false;
  Timer? _pollTimer;

  @override
  void initState() {
    super.initState();
    _fetchMessages();
    _pollTimer = Timer.periodic(const Duration(seconds: 4), (_) => _fetchMessages(silent: true));
  }

  @override
  void dispose() {
    _pollTimer?.cancel();
    _msgController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  Future<void> _fetchMessages({bool silent = false}) async {
    if (!silent) setState(() => _isLoading = true);
    final res = await widget.apiClient.getOrderMessages(widget.orderId);
    if (!mounted) return;
    if (res.isSuccess && res.data != null) {
      final newLen = res.data!.length;
      final oldLen = _messages.length;
      setState(() {
        _messages = res.data!;
        _isLoading = false;
      });
      if (newLen > oldLen) {
        _scrollToBottom();
      }
    } else {
      if (!silent) setState(() => _isLoading = false);
    }
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 250),
          curve: Curves.easeOut,
        );
      }
    });
  }

  Future<void> _sendText() async {
    final text = _msgController.text.trim();
    if (text.isEmpty || _isSending) return;

    _msgController.clear();
    setState(() => _isSending = true);

    final res = await widget.apiClient.sendOrderMessage(
      widget.orderId,
      messageType: 'TEXT',
      content: text,
    );

    if (!mounted) return;
    setState(() => _isSending = false);

    if (res.isSuccess && res.data != null) {
      setState(() => _messages.add(res.data!));
      _scrollToBottom();
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(res.errorMessage ?? 'Failed to send message'), backgroundColor: GBColors.error),
      );
    }
  }

  Future<void> _openGoogleMapsDirections(double lat, double lng) async {
    final uri = Uri.parse('https://www.google.com/maps/dir/?api=1&destination=$lat,$lng');
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    } else {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Could not open Google Maps')),
        );
      }
    }
  }

  Future<void> _callPartner() async {
    final phone = widget.partnerPhone ?? '9800000000';
    final uri = Uri.parse('tel:$phone');
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri);
    } else {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Calling $phone...')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      appBar: AppBar(
        titleSpacing: 0,
        title: Row(
          children: [
            CircleAvatar(
              radius: 18,
              backgroundColor: GBColors.primary.withAlpha(40),
              child: const Icon(Icons.person, color: GBColors.primary, size: 20),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    widget.partnerName,
                    style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 15),
                    overflow: TextOverflow.ellipsis,
                  ),
                  const Text(
                    'Customer • Online',
                    style: TextStyle(fontSize: 11, color: GBColors.success, fontWeight: FontWeight.w600),
                  ),
                ],
              ),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.phone_in_talk, color: GBColors.primary),
            tooltip: 'Call Customer',
            onPressed: _callPartner,
          ),
        ],
      ),
      body: SafeArea(
        child: Column(
          children: [
            Expanded(
              child: _isLoading
                  ? const Center(child: CircularProgressIndicator())
                  : _messages.isEmpty
                      ? Center(
                          child: Column(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Icon(Icons.chat_bubble_outline, size: 48, color: Colors.grey.shade400),
                              const SizedBox(height: 10),
                              const Text(
                                'No messages yet',
                                style: TextStyle(fontWeight: FontWeight.w700, color: Colors.grey),
                              ),
                              const SizedBox(height: 4),
                              const Text(
                                'Coordinate drop-off directions or delivery updates here',
                                style: TextStyle(fontSize: 12, color: Colors.grey),
                              ),
                            ],
                          ),
                        )
                      : ListView.builder(
                          controller: _scrollController,
                          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                          itemCount: _messages.length,
                          itemBuilder: (ctx, idx) {
                            final m = _messages[idx];
                            final isMe = m.senderRole == widget.currentRole;
                            return _buildMessageBubble(m, isMe, isDark);
                          },
                        ),
            ),
            Container(
              padding: const EdgeInsets.fromLTRB(10, 8, 10, 10),
              decoration: BoxDecoration(
                color: isDark ? GBColors.cardDark : Colors.white,
                border: Border(top: BorderSide(color: isDark ? GBColors.borderDark : Colors.grey.shade200)),
              ),
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _msgController,
                      textCapitalization: TextCapitalization.sentences,
                      decoration: InputDecoration(
                        hintText: 'Type reply to customer...',
                        hintStyle: const TextStyle(fontSize: 13),
                        contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(24)),
                        filled: true,
                        fillColor: isDark ? GBColors.backgroundDark : Colors.grey.shade100,
                      ),
                      onSubmitted: (_) => _sendText(),
                    ),
                  ),
                  const SizedBox(width: 8),
                  CircleAvatar(
                    radius: 22,
                    backgroundColor: GBColors.primary,
                    child: IconButton(
                      icon: _isSending
                          ? const SizedBox(
                              width: 18,
                              height: 18,
                              child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
                            )
                          : const Icon(Icons.send, color: Colors.white, size: 18),
                      onPressed: _isSending ? null : _sendText,
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

  Widget _buildMessageBubble(GBOrderMessage m, bool isMe, bool isDark) {
    if (m.messageType == 'LOCATION_PIN' || m.messageType == 'LIVE_LOCATION_START') {
      return Align(
        alignment: isMe ? Alignment.centerRight : Alignment.centerLeft,
        child: Container(
          margin: const EdgeInsets.symmetric(vertical: 6),
          constraints: const BoxConstraints(maxWidth: 290),
          decoration: BoxDecoration(
            color: isMe ? GBColors.primary.withAlpha(25) : (isDark ? GBColors.cardDark : Colors.white),
            borderRadius: BorderRadius.circular(14),
            border: Border.all(color: GBColors.primary.withAlpha(90), width: 1.5),
            boxShadow: const [BoxShadow(color: Colors.black12, blurRadius: 4, offset: Offset(0, 1))],
          ),
          child: Padding(
            padding: const EdgeInsets.all(12),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const Icon(Icons.location_on, color: GBColors.primary, size: 20),
                    const SizedBox(width: 6),
                    Expanded(
                      child: Text(
                        m.locationTitle ?? 'Customer Shared Location Pin',
                        style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 13),
                      ),
                    ),
                  ],
                ),
                if (m.latitude != null && m.longitude != null) ...[
                  const SizedBox(height: 6),
                  Text(
                    '${m.latitude!.toStringAsFixed(4)}, ${m.longitude!.toStringAsFixed(4)}',
                    style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Colors.grey),
                  ),
                  const SizedBox(height: 10),
                  SizedBox(
                    width: double.infinity,
                    height: 36,
                    child: ElevatedButton.icon(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: GBColors.primary,
                        foregroundColor: Colors.white,
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                        padding: const EdgeInsets.symmetric(horizontal: 10),
                      ),
                      icon: const Icon(Icons.navigation, size: 16),
                      label: const Text(
                        'Open in Google Maps',
                        style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold),
                      ),
                      onPressed: () => _openGoogleMapsDirections(m.latitude!, m.longitude!),
                    ),
                  ),
                ],
              ],
            ),
          ),
        ),
      );
    }

    return Align(
      alignment: isMe ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 4),
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        constraints: const BoxConstraints(maxWidth: 270),
        decoration: BoxDecoration(
          color: isMe
              ? GBColors.primary
              : (isDark ? GBColors.cardDark : Colors.grey.shade200),
          borderRadius: BorderRadius.only(
            topLeft: const Radius.circular(14),
            topRight: const Radius.circular(14),
            bottomLeft: Radius.circular(isMe ? 14 : 2),
            bottomRight: Radius.circular(isMe ? 2 : 14),
          ),
        ),
        child: Column(
          crossAxisAlignment: isMe ? CrossAxisAlignment.end : CrossAxisAlignment.start,
          children: [
            Text(
              m.content ?? '',
              style: TextStyle(
                color: isMe ? Colors.white : (isDark ? Colors.white : Colors.black87),
                fontSize: 13,
                fontWeight: FontWeight.w500,
              ),
            ),
            const SizedBox(height: 3),
            Text(
              '${m.senderName} • ${m.createdAt.hour.toString().padLeft(2, '0')}:${m.createdAt.minute.toString().padLeft(2, '0')}',
              style: TextStyle(
                color: isMe ? Colors.white70 : Colors.grey.shade600,
                fontSize: 10,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
