import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import 'package:localization/localization.dart';
import 'package:shared_models/shared_models.dart';
import 'package:url_launcher/url_launcher.dart';
import '../state/vendor_state.dart';

class VendorPickingPackingScreen extends StatefulWidget {
  final GBOrder order;

  const VendorPickingPackingScreen({super.key, required this.order});

  @override
  State<VendorPickingPackingScreen> createState() => _VendorPickingPackingScreenState();
}

class _VendorPickingPackingScreenState extends State<VendorPickingPackingScreen> {
  late Map<String, bool> _pickedItems;
  late Map<String, bool> _outOfStockItems;
  bool _isActing = false;

  @override
  void initState() {
    super.initState();
    _pickedItems = {for (var item in widget.order.items) item.id: widget.order.status != 'PLACED' && widget.order.status != 'ACCEPTED'};
    _outOfStockItems = {for (var item in widget.order.items) item.id: false};
  }

  bool get _allRequiredPicked {
    for (var item in widget.order.items) {
      final isOut = _outOfStockItems[item.id] == true;
      final isPicked = _pickedItems[item.id] == true;
      if (!isOut && !isPicked) {
        return false;
      }
    }
    return true;
  }

  int get _pickedCount {
    return _pickedItems.values.where((p) => p).length;
  }

  Future<void> _handleAction(VendorAppState state, String action) async {
    setState(() => _isActing = true);
    final success = await state.handleOrderAction(widget.order.id, action);
    if (!mounted) return;
    setState(() => _isActing = false);

    final loc = GBLocalizations.of(context);
    if (success) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(loc.isHindi ? 'ऑर्डर स्थिति अपडेट हो गई' : 'Order status updated successfully'),
          backgroundColor: GBColors.success,
        ),
      );
      Navigator.of(context).pop();
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(loc.isHindi ? 'कार्रवाई विफल रही' : 'Action failed. Please try again.'),
          backgroundColor: GBColors.error,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = VendorStateProvider.of(context);
    final loc = GBLocalizations.of(context);
    final isHi = loc.isHindi;
    final isDark = Theme.of(context).brightness == Brightness.dark;

    final canPack = widget.order.status == 'ACCEPTED' || widget.order.status == 'PLACED';
    final isPacked = widget.order.status == 'PACKED' || widget.order.status == 'RUNNER_ASSIGNED';

    return Scaffold(
      appBar: AppBar(
        title: Text(
          isHi ? 'सामान पिकिंग व पैकिंग' : 'Picking & Packing',
          style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 17),
        ),
        elevation: 1,
      ),
      body: Column(
        children: [
          // Header Summary Card
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
            decoration: BoxDecoration(
              color: isDark ? const Color(0xFF1E293B) : const Color(0xFFF1F5F9),
              border: Border(bottom: BorderSide(color: isDark ? Colors.white12 : Colors.black12)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'ऑर्डर #${widget.order.id.toUpperCase()}',
                      style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 15),
                    ),
                    _buildStatusBadge(widget.order.status, isHi),
                  ],
                ),
                const SizedBox(height: 6),
                Row(
                  children: [
                    Icon(Icons.location_on_outlined, size: 16, color: isDark ? Colors.white70 : Colors.black54),
                    const SizedBox(width: 4),
                    Expanded(
                      child: Text(
                        widget.order.deliveryAddress,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: TextStyle(fontSize: 12, color: isDark ? Colors.white70 : Colors.black54),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 10),
                // Progress Bar
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      isHi ? 'पैक की गई वस्तुएँ:' : 'Packed Items:',
                      style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
                    ),
                    Text(
                      '$_pickedCount / ${widget.order.items.length}',
                      style: TextStyle(
                        fontSize: 13,
                        fontWeight: FontWeight.w800,
                        color: _allRequiredPicked ? GBColors.success : GBColors.warning,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 6),
                ClipRRect(
                  borderRadius: BorderRadius.circular(4),
                  child: LinearProgressIndicator(
                    value: widget.order.items.isEmpty ? 1.0 : (_pickedCount / widget.order.items.length),
                    backgroundColor: isDark ? Colors.white10 : Colors.black12,
                    valueColor: AlwaysStoppedAnimation<Color>(
                      _allRequiredPicked ? GBColors.success : GBColors.warning,
                    ),
                    minHeight: 6,
                  ),
                ),
              ],
            ),
          ),

          // Items Checklist
          Expanded(
            child: ListView.separated(
              padding: const EdgeInsets.all(16),
              itemCount: widget.order.items.length,
              separatorBuilder: (_, __) => const SizedBox(height: 10),
              itemBuilder: (context, index) {
                final item = widget.order.items[index];
                final isPicked = _pickedItems[item.id] == true;
                final isOut = _outOfStockItems[item.id] == true;

                return Card(
                  elevation: 1,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                    side: BorderSide(
                      color: isPicked
                          ? GBColors.success.withValues(alpha: 0.5)
                          : (isOut ? Colors.red.withValues(alpha: 0.5) : (isDark ? Colors.white12 : Colors.black12)),
                      width: isPicked || isOut ? 1.5 : 1.0,
                    ),
                  ),
                  child: Padding(
                    padding: const EdgeInsets.all(12),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.center,
                      children: [
                        // Thumbnail Image
                        ClipRRect(
                          borderRadius: BorderRadius.circular(8),
                          child: item.imageUrl != null && item.imageUrl!.startsWith('http')
                              ? Image.network(
                                  item.imageUrl!,
                                  width: 56,
                                  height: 56,
                                  fit: BoxFit.cover,
                                  errorBuilder: (_, __, ___) => _buildFallbackThumbnail(),
                                )
                              : _buildFallbackThumbnail(),
                        ),
                        const SizedBox(width: 12),
                        // Title & Details
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                isHi ? item.nameHi : item.nameEn,
                                style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 14),
                              ),
                              const SizedBox(height: 2),
                              Text(
                                '${item.unit} • ₹${item.unitPrice.toStringAsFixed(0)}',
                                style: TextStyle(fontSize: 12, color: isDark ? Colors.white60 : Colors.black54),
                              ),
                              const SizedBox(height: 4),
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                                decoration: BoxDecoration(
                                  color: GBColors.primary.withValues(alpha: 0.1),
                                  borderRadius: BorderRadius.circular(4),
                                ),
                                child: Text(
                                  'मात्रा: ${item.quantity} ${item.unit}',
                                  style: const TextStyle(
                                    color: GBColors.primary,
                                    fontWeight: FontWeight.w800,
                                    fontSize: 11,
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(width: 8),
                        // Picking Action Toggle
                        Column(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            InkWell(
                              onTap: () {
                                setState(() {
                                  if (isOut) {
                                    _outOfStockItems[item.id] = false;
                                  }
                                  _pickedItems[item.id] = !isPicked;
                                });
                              },
                              borderRadius: BorderRadius.circular(8),
                              child: Container(
                                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                                decoration: BoxDecoration(
                                  color: isPicked
                                      ? GBColors.success
                                      : (isDark ? Colors.white10 : Colors.black12),
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                child: Row(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    Icon(
                                      isPicked ? Icons.check_circle : Icons.radio_button_unchecked,
                                      size: 16,
                                      color: isPicked ? Colors.white : (isDark ? Colors.white70 : Colors.black54),
                                    ),
                                    const SizedBox(width: 4),
                                    Text(
                                      isPicked ? (isHi ? 'पैक' : 'Packed') : (isHi ? 'पैक करें' : 'Pack'),
                                      style: TextStyle(
                                        color: isPicked ? Colors.white : (isDark ? Colors.white70 : Colors.black87),
                                        fontWeight: FontWeight.w700,
                                        fontSize: 12,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                );
              },
            ),
          ),

          // Assigned Runner Card (if runner assigned)
          if (widget.order.runnerName != null) ...[
            Container(
              margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: isDark ? const Color(0xFF1E293B) : const Color(0xFFE8F5E9),
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: GBColors.primary.withValues(alpha: 0.3)),
              ),
              child: Row(
                children: [
                  const CircleAvatar(
                    backgroundColor: GBColors.primary,
                    radius: 18,
                    child: Icon(Icons.delivery_dining, color: Colors.white, size: 20),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          isHi ? 'डिलीवरी साथी आवंटित' : 'Assigned Runner',
                          style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: Colors.grey),
                        ),
                        Text(
                          widget.order.runnerName!,
                          style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 13),
                        ),
                      ],
                    ),
                  ),
                  if (widget.order.runnerPhone != null)
                    IconButton(
                      icon: const Icon(Icons.phone, color: GBColors.primary),
                      onPressed: () async {
                        final uri = Uri.parse('tel:${widget.order.runnerPhone}');
                        if (await canLaunchUrl(uri)) {
                          await launchUrl(uri);
                        }
                      },
                    ),
                ],
              ),
            ),
          ],

          // Bottom Action Bar
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Theme.of(context).cardColor,
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withValues(alpha: 0.05),
                  blurRadius: 10,
                  offset: const Offset(0, -4),
                ),
              ],
            ),
            child: SafeArea(
              child: canPack
                  ? ElevatedButton(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: _allRequiredPicked ? GBColors.primary : Colors.grey,
                        minimumSize: const Size.fromHeight(50),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                      ),
                      onPressed: _allRequiredPicked && !_isActing
                          ? () => _handleAction(state, 'PACK')
                          : null,
                      child: _isActing
                          ? const SizedBox(
                              height: 20,
                              width: 20,
                              child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
                            )
                          : Text(
                              isHi
                                  ? 'पैकिंग पूर्ण करें और तैयार करें'
                                  : 'Complete Packing & Mark Ready',
                              style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 15),
                            ),
                    )
                  : (isPacked
                      ? ElevatedButton.icon(
                          style: ElevatedButton.styleFrom(
                            backgroundColor: GBColors.primary,
                            minimumSize: const Size.fromHeight(50),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                          ),
                          icon: const Icon(Icons.handshake_outlined),
                          label: Text(
                            isHi ? 'डिलीवरी साथी को सौंपें' : 'Hand Over to Runner',
                            style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 15),
                          ),
                          onPressed: !_isActing ? () => _handleAction(state, 'HANDOFF') : null,
                        )
                      : Container(
                          padding: const EdgeInsets.all(12),
                          alignment: Alignment.center,
                          child: Text(
                            isHi ? 'ऑर्डर की स्थिति: ${widget.order.status}' : 'Order Status: ${widget.order.status}',
                            style: const TextStyle(fontWeight: FontWeight.w700),
                          ),
                        )),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFallbackThumbnail() {
    return Container(
      width: 56,
      height: 56,
      color: Colors.grey.withValues(alpha: 0.15),
      child: const Icon(Icons.shopping_bag_outlined, color: Colors.grey, size: 28),
    );
  }

  Widget _buildStatusBadge(String status, bool isHi) {
    Color bg = Colors.blue.withValues(alpha: 0.1);
    Color txt = Colors.blue;
    String label = status;

    switch (status) {
      case 'PLACED':
        bg = Colors.amber.withValues(alpha: 0.15);
        txt = Colors.amber.shade900;
        label = isHi ? 'नया ऑर्डर' : 'New Order';
        break;
      case 'ACCEPTED':
        bg = Colors.blue.withValues(alpha: 0.15);
        txt = Colors.blue.shade800;
        label = isHi ? 'स्वीकृत' : 'Accepted';
        break;
      case 'PACKED':
        bg = Colors.purple.withValues(alpha: 0.15);
        txt = Colors.purple.shade800;
        label = isHi ? 'पैक हो गया' : 'Packed';
        break;
      case 'RUNNER_ASSIGNED':
        bg = Colors.orange.withValues(alpha: 0.15);
        txt = Colors.orange.shade900;
        label = isHi ? 'साथी आ रहा है' : 'Runner Assigned';
        break;
      case 'PICKED_UP':
      case 'OUT_FOR_DELIVERY':
        bg = Colors.teal.withValues(alpha: 0.15);
        txt = Colors.teal.shade800;
        label = isHi ? 'रास्ते में' : 'Out for Delivery';
        break;
      case 'DELIVERED':
        bg = Colors.green.withValues(alpha: 0.15);
        txt = Colors.green.shade800;
        label = isHi ? 'पूर्ण' : 'Delivered';
        break;
      case 'CANCELLED':
        bg = Colors.red.withValues(alpha: 0.15);
        txt = Colors.red.shade800;
        label = isHi ? 'रद्द' : 'Cancelled';
        break;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(color: bg, borderRadius: BorderRadius.circular(6)),
      child: Text(label, style: TextStyle(color: txt, fontWeight: FontWeight.w800, fontSize: 11)),
    );
  }
}
