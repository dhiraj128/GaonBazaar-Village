import 'dart:async';
import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import 'package:localization/localization.dart';
import 'package:shared_models/shared_models.dart';
import 'package:api_client/api_client.dart';
import 'package:geolocator/geolocator.dart';
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
  bool _isSharingLiveLocation = false;
  Timer? _pollTimer;
  Timer? _liveLocationTimer;

  @override
  void initState() {
    super.initState();
    _fetchMessages();
    // Poll for new messages every 4 seconds while screen is open
    _pollTimer = Timer.periodic(const Duration(seconds: 4), (_) => _fetchMessages(silent: true));
  }

  @override
  void dispose() {
    _pollTimer?.cancel();
    _liveLocationTimer?.cancel();
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

  Future<void> _attachGpsPin() async {
    final loc = GBLocalizations.of(context);
    final isHi = loc.isHindi;

    try {
      LocationPermission perm = await Geolocator.checkPermission();
      if (perm == LocationPermission.denied) {
        perm = await Geolocator.requestPermission();
      }
      if (perm == LocationPermission.deniedForever || perm == LocationPermission.denied) {
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(isHi ? 'स्थान की अनुमति आवश्यक है' : 'Location permission required to share GPS pin'),
            backgroundColor: GBColors.warning,
          ),
        );
        return;
      }

      final pos = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high,
        timeLimit: const Duration(seconds: 8),
      );

      if (!mounted) return;

      // Show preview confirmation bottom sheet
      final confirmed = await showModalBottomSheet<bool>(
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
                  const Icon(Icons.pin_drop, color: GBColors.primary, size: 28),
                  const SizedBox(width: 10),
                  Text(
                    isHi ? 'वर्तमान जीपीएस पिन साझा करें' : 'Share GPS Location Pin',
                    style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16),
                  ),
                ],
              ),
              const SizedBox(height: 14),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.grey.shade100,
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: Colors.grey.shade300),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '${pos.latitude.toStringAsFixed(5)}, ${pos.longitude.toStringAsFixed(5)}',
                      style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 14),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      isHi ? 'यह पिन डिलीवरी साथी को वास्तविक स्थान तक पहुंचने में मदद करेगा।' : 'This precise GPS pin guides the partner directly to your exact spot.',
                      style: const TextStyle(fontSize: 12, color: Colors.grey),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 20),
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton(
                      onPressed: () => Navigator.of(ctx).pop(false),
                      child: Text(isHi ? 'रद्द करें' : 'Cancel'),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: ElevatedButton(
                      style: ElevatedButton.styleFrom(backgroundColor: GBColors.primary, foregroundColor: Colors.white),
                      onPressed: () => Navigator.of(ctx).pop(true),
                      child: Text(isHi ? 'भेजें' : 'Send Pin'),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      );

      if (confirmed == true && mounted) {
        setState(() => _isSending = true);
        final res = await widget.apiClient.sendOrderMessage(
          widget.orderId,
          messageType: 'LOCATION_PIN',
          content: isHi ? 'ग्राहक का वर्तमान जीपीएस पिन' : 'Customer live GPS pin',
          latitude: pos.latitude,
          longitude: pos.longitude,
          locationTitle: 'Accurate Delivery GPS Pin',
        );
        setState(() => _isSending = false);
        if (res.isSuccess && res.data != null) {
          setState(() => _messages.add(res.data!));
          _scrollToBottom();
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('GPS error: $e'), backgroundColor: GBColors.error),
        );
      }
    }
  }

  void _toggleLiveLocation() {
    final loc = GBLocalizations.of(context);
    final isHi = loc.isHindi;

    if (_isSharingLiveLocation) {
      // Stop live location
      _liveLocationTimer?.cancel();
      setState(() => _isSharingLiveLocation = false);
      widget.apiClient.sendOrderMessage(
        widget.orderId,
        messageType: 'LIVE_LOCATION_STOP',
        content: isHi ? 'लाइव लोकेशन साझा करना समाप्त किया' : 'Live location sharing stopped',
      );
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(isHi ? 'लाइव लोकेशन बंद कर दी गई' : 'Live location sharing stopped')),
      );
    } else {
      // Start live location
      setState(() => _isSharingLiveLocation = true);
      _sendLiveLocationUpdate();
      _liveLocationTimer = Timer.periodic(const Duration(seconds: 15), (_) => _sendLiveLocationUpdate());
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(isHi ? 'लाइव लोकेशन सक्रिय (15 सेकंड पर अपडेट)' : 'Live location sharing active'),
          backgroundColor: GBColors.success,
        ),
      );
    }
  }

  Future<void> _sendLiveLocationUpdate() async {
    try {
      final pos = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high,
        timeLimit: const Duration(seconds: 5),
      );
      await widget.apiClient.sendOrderMessage(
        widget.orderId,
        messageType: 'LIVE_LOCATION_START',
        content: 'Live location stream active',
        latitude: pos.latitude,
        longitude: pos.longitude,
        locationTitle: 'Moving Live Pin',
      );
      _fetchMessages(silent: true);
    } catch (_) {}
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
    final phone = widget.partnerPhone ?? '9800000003';
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
    final loc = GBLocalizations.of(context);
    final isHi = loc.isHindi;
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      appBar: AppBar(
        titleSpacing: 0,
        title: Row(
          children: [
            CircleAvatar(
              radius: 18,
              backgroundColor: GBColors.primary.withAlpha(40),
              child: Icon(
                widget.currentRole == 'customer' ? Icons.two_wheeler : Icons.person,
                color: GBColors.primary,
                size: 20,
              ),
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
                  Text(
                    widget.currentRole == 'customer'
                        ? (isHi ? 'डिलीवरी साथी • ऑनलाइन' : 'Delivery Partner • Online')
                        : (isHi ? 'ग्राहक • ऑनलाइन' : 'Customer • Online'),
                    style: const TextStyle(fontSize: 11, color: GBColors.success, fontWeight: FontWeight.w600),
                  ),
                ],
              ),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.phone_in_talk, color: GBColors.primary),
            tooltip: isHi ? 'कॉल करें' : 'Call',
            onPressed: _callPartner,
          ),
        ],
      ),
      body: SafeArea(
        child: Column(
          children: [
            // Live Location Active Warning Banner
            if (_isSharingLiveLocation)
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                color: GBColors.success.withAlpha(25),
                child: Row(
                  children: [
                    const Icon(Icons.share_location, color: GBColors.success, size: 20),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Text(
                        isHi ? 'आपकी लाइव लोकेशन साझा की जा रही है' : 'Live location is currently being shared',
                        style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: GBColors.success),
                      ),
                    ),
                    TextButton(
                      style: TextButton.styleFrom(
                        foregroundColor: GBColors.error,
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      ),
                      onPressed: _toggleLiveLocation,
                      child: Text(
                        isHi ? 'बंद करें' : 'Stop Sharing',
                        style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12),
                      ),
                    ),
                  ],
                ),
              ),

            // Message List
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
                              Text(
                                isHi ? 'बातचीत शुरू करें' : 'Start conversation',
                                style: const TextStyle(fontWeight: FontWeight.w700, color: Colors.grey),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                isHi
                                    ? 'पते या लैंडमार्क के बारे में संदेश या जीपीएस पिन भेजें'
                                    : 'Send instructions or attach an exact GPS pin for drop-off',
                                style: const TextStyle(fontSize: 12, color: Colors.grey),
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
                            return _buildMessageBubble(m, isMe, isDark, isHi);
                          },
                        ),
            ),

            // Bottom action row & text input
            Container(
              padding: const EdgeInsets.fromLTRB(10, 8, 10, 10),
              decoration: BoxDecoration(
                color: isDark ? GBColors.cardDark : Colors.white,
                border: Border(top: BorderSide(color: isDark ? GBColors.borderDark : Colors.grey.shade200)),
              ),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  // Location Attachment Quick Actions
                  Row(
                    children: [
                      ActionChip(
                        avatar: const Icon(Icons.pin_drop, size: 16, color: GBColors.primary),
                        label: Text(
                          isHi ? 'जीपीएस पिन भेजें' : 'Attach GPS Pin',
                          style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold),
                        ),
                        onPressed: _attachGpsPin,
                      ),
                      const SizedBox(width: 8),
                      ActionChip(
                        avatar: Icon(
                          _isSharingLiveLocation ? Icons.stop_circle : Icons.share_location,
                          size: 16,
                          color: _isSharingLiveLocation ? GBColors.error : GBColors.primary,
                        ),
                        label: Text(
                          _isSharingLiveLocation
                              ? (isHi ? 'लाइव शेयर रोकें' : 'Stop Live Share')
                              : (isHi ? 'लाइव शेयर करें' : 'Share Live Location'),
                          style: TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.bold,
                            color: _isSharingLiveLocation ? GBColors.error : null,
                          ),
                        ),
                        onPressed: _toggleLiveLocation,
                      ),
                    ],
                  ),
                  const SizedBox(height: 6),
                  Row(
                    children: [
                      Expanded(
                        child: TextField(
                          controller: _msgController,
                          textCapitalization: TextCapitalization.sentences,
                          decoration: InputDecoration(
                            hintText: isHi ? 'संदेश लिखें...' : 'Type a message...',
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
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMessageBubble(GBOrderMessage m, bool isMe, bool isDark, bool isHi) {
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
                        m.locationTitle ?? (isHi ? 'जीपीएस लोकेशन पिन' : 'GPS Location Pin'),
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
                      label: Text(
                        isHi ? 'गूगल मैप्स नेविगेशन खोलें' : 'Navigate in Google Maps',
                        style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold),
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
