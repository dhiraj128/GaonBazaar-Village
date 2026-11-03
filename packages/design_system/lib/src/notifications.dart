import 'package:flutter/material.dart';
import 'colors.dart';

class GBNotificationBell extends StatelessWidget {
  final int unreadCount;
  final VoidCallback onTap;
  final Color? iconColor;

  const GBNotificationBell({
    super.key,
    required this.unreadCount,
    required this.onTap,
    this.iconColor,
  });

  @override
  Widget build(BuildContext context) {
    return Stack(
      alignment: Alignment.center,
      children: [
        IconButton(
          icon: Icon(
            unreadCount > 0 ? Icons.notifications_active_outlined : Icons.notifications_outlined,
            color: iconColor ?? GBColors.primary,
            size: 24,
          ),
          tooltip: 'Notifications',
          onPressed: onTap,
        ),
        if (unreadCount > 0)
          Positioned(
            top: 8,
            right: 8,
            child: Container(
              padding: const EdgeInsets.all(3),
              decoration: const BoxDecoration(
                color: GBColors.error,
                shape: BoxShape.circle,
              ),
              constraints: const BoxConstraints(
                minWidth: 16,
                minHeight: 16,
              ),
              child: Text(
                unreadCount > 9 ? '9+' : '$unreadCount',
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 9,
                  fontWeight: FontWeight.bold,
                ),
                textAlign: TextAlign.center,
              ),
            ),
          ),
      ],
    );
  }
}

class GBNotificationItemData {
  final String id;
  final String title;
  final String body;
  final String time;
  final bool isRead;
  final String type; // 'order', 'delivery', 'approval', 'payment', 'system'

  const GBNotificationItemData({
    required this.id,
    required this.title,
    required this.body,
    required this.time,
    this.isRead = false,
    this.type = 'system',
  });
}

void showGBNotificationSheet(
  BuildContext context, {
  required List<GBNotificationItemData> notifications,
  required VoidCallback onMarkAllRead,
  bool isHindi = true,
}) {
  showModalBottomSheet(
    context: context,
    isScrollControlled: true,
    backgroundColor: Colors.transparent,
    builder: (ctx) {
      return StatefulBuilder(
        builder: (context, setSheetState) {
          final isDark = Theme.of(context).brightness == Brightness.dark;
          final unreadCount = notifications.where((n) => !n.isRead).length;

          return Container(
            height: MediaQuery.of(context).size.height * 0.75,
            decoration: BoxDecoration(
              color: isDark ? const Color(0xFF1E293B) : Colors.white,
              borderRadius: const BorderRadius.vertical(top: Radius.circular(24)),
              boxShadow: const [
                BoxShadow(color: Colors.black26, blurRadius: 16, offset: Offset(0, -2)),
              ],
            ),
            child: Column(
              children: [
                // Top drag handle
                const SizedBox(height: 12),
                Container(
                  width: 44,
                  height: 4,
                  decoration: BoxDecoration(
                    color: Colors.grey.withAlpha(80),
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
                const SizedBox(height: 14),

                // Header
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 20),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Row(
                        children: [
                          Text(
                            isHindi ? 'सूचना केंद्र' : 'Notifications',
                            style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w800),
                          ),
                          if (unreadCount > 0) ...[
                            const SizedBox(width: 8),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                              decoration: BoxDecoration(
                                color: GBColors.primary.withAlpha(30),
                                borderRadius: BorderRadius.circular(12),
                              ),
                              child: Text(
                                '$unreadCount',
                                style: const TextStyle(
                                  color: GBColors.primary,
                                  fontSize: 12,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ),
                          ],
                        ],
                      ),
                      if (unreadCount > 0)
                        TextButton(
                          onPressed: () {
                            onMarkAllRead();
                            setSheetState(() {});
                          },
                          child: Text(
                            isHindi ? 'सभी पढ़ें' : 'Mark all read',
                            style: const TextStyle(
                              color: GBColors.primary,
                              fontSize: 12,
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                        ),
                    ],
                  ),
                ),
                const Divider(height: 16),

                // Notification List
                Expanded(
                  child: notifications.isEmpty
                      ? Center(
                          child: Column(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Icon(Icons.notifications_none_outlined, size: 56, color: Colors.grey.shade400),
                              const SizedBox(height: 12),
                              Text(
                                isHindi ? 'कोई नई सूचना नहीं है' : 'No notifications yet',
                                style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 15),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                isHindi
                                    ? 'ऑर्डर, डिलीवरी और सिस्टम अलर्ट यहाँ दिखाई देंगे।'
                                    : 'Order updates, delivery, and system alerts appear here.',
                                style: const TextStyle(fontSize: 12, color: Colors.grey),
                              ),
                            ],
                          ),
                        )
                      : ListView.separated(
                          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                          itemCount: notifications.length,
                          separatorBuilder: (_, __) => const SizedBox(height: 10),
                          itemBuilder: (ctx, idx) {
                            final item = notifications[idx];
                            final icon = item.type == 'order'
                                ? Icons.shopping_bag_outlined
                                : item.type == 'delivery'
                                    ? Icons.two_wheeler_outlined
                                    : item.type == 'approval'
                                        ? Icons.verified_outlined
                                        : item.type == 'payment'
                                            ? Icons.payments_outlined
                                            : Icons.info_outline;

                            final iconBg = item.type == 'order'
                                ? const Color(0xFF2E7D32).withAlpha(25)
                                : item.type == 'delivery'
                                    ? const Color(0xFFE65100).withAlpha(25)
                                    : item.type == 'approval'
                                        ? const Color(0xFF0288D1).withAlpha(25)
                                        : Colors.grey.withAlpha(25);

                            final iconColor = item.type == 'order'
                                ? const Color(0xFF2E7D32)
                                : item.type == 'delivery'
                                    ? const Color(0xFFE65100)
                                    : item.type == 'approval'
                                        ? const Color(0xFF0288D1)
                                        : Colors.grey.shade700;

                            return Container(
                              padding: const EdgeInsets.all(14),
                              decoration: BoxDecoration(
                                color: item.isRead
                                    ? (isDark ? const Color(0xFF0F172A) : const Color(0xFFF8FAFC))
                                    : (isDark ? const Color(0xFF334155) : Colors.white),
                                borderRadius: BorderRadius.circular(14),
                                border: Border.all(
                                  color: item.isRead
                                      ? (isDark ? Colors.white12 : Colors.grey.shade200)
                                      : GBColors.primary.withAlpha(80),
                                  width: item.isRead ? 1 : 1.5,
                                ),
                              ),
                              child: Row(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Container(
                                    width: 40,
                                    height: 40,
                                    decoration: BoxDecoration(
                                      color: iconBg,
                                      shape: BoxShape.circle,
                                    ),
                                    child: Icon(icon, color: iconColor, size: 20),
                                  ),
                                  const SizedBox(width: 12),
                                  Expanded(
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        Row(
                                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                          children: [
                                            Expanded(
                                              child: Text(
                                                item.title,
                                                style: TextStyle(
                                                  fontWeight: item.isRead ? FontWeight.w600 : FontWeight.w800,
                                                  fontSize: 13,
                                                ),
                                              ),
                                            ),
                                            if (!item.isRead)
                                              Container(
                                                width: 8,
                                                height: 8,
                                                decoration: const BoxDecoration(
                                                  color: GBColors.primary,
                                                  shape: BoxShape.circle,
                                                ),
                                              ),
                                          ],
                                        ),
                                        const SizedBox(height: 4),
                                        Text(
                                          item.body,
                                          style: TextStyle(
                                            fontSize: 12,
                                            color: isDark ? Colors.grey.shade300 : Colors.black87,
                                          ),
                                        ),
                                        const SizedBox(height: 6),
                                        Text(
                                          item.time,
                                          style: const TextStyle(fontSize: 10, color: Colors.grey),
                                        ),
                                      ],
                                    ),
                                  ),
                                ],
                              ),
                            );
                          },
                        ),
                ),
              ],
            ),
          );
        },
      );
    },
  );
}
