import 'package:flutter/material.dart';
import 'colors.dart';
import 'typography.dart';
import 'buttons.dart';

class GBStoreCard extends StatelessWidget {
  final String name;
  final String category;
  final String village;
  final double rating;
  final double? distanceKm;
  final String? bannerUrl;
  final bool isOnline;
  final VoidCallback onTap;

  const GBStoreCard({
    super.key,
    required this.name,
    required this.category,
    required this.village,
    required this.rating,
    this.distanceKm,
    this.bannerUrl,
    this.isOnline = true,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.all(10),
        decoration: BoxDecoration(
          color: isDark ? GBColors.cardDark : GBColors.cardLight,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: isDark ? GBColors.borderDark : GBColors.borderLight,
          ),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(isDark ? 0.2 : 0.04),
              blurRadius: 6,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            // Store banner or category icon
            ClipRRect(
              borderRadius: BorderRadius.circular(8),
              child: Stack(
                children: [
                  Container(
                    height: 72,
                    width: double.infinity,
                    color: GBColors.primary.withOpacity(0.12),
                    child: bannerUrl != null && bannerUrl!.isNotEmpty
                        ? Image.network(
                            bannerUrl!,
                            fit: BoxFit.cover,
                            errorBuilder: (ctx, err, stack) => const Icon(
                              Icons.storefront,
                              size: 36,
                              color: GBColors.primary,
                            ),
                          )
                        : const Icon(
                            Icons.storefront,
                            size: 36,
                            color: GBColors.primary,
                          ),
                  ),
                  Positioned(
                    top: 6,
                    right: 6,
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                      decoration: BoxDecoration(
                        color: Colors.black.withOpacity(0.7),
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          const Icon(Icons.star, size: 12, color: Colors.amber),
                          const SizedBox(width: 3),
                          Text(
                            rating.toStringAsFixed(1),
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 10,
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 8),
            Text(
              name,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700),
            ),
            const SizedBox(height: 2),
            Text(
              village,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: TextStyle(
                fontSize: 11,
                color: isDark ? GBColors.textMutedDark : GBColors.textMutedLight,
              ),
            ),
            const SizedBox(height: 4),
            Row(
              children: [
                if (distanceKm != null) ...[
                  Icon(
                    Icons.navigation_outlined,
                    size: 11,
                    color: isDark ? GBColors.textSecondaryDark : GBColors.textSecondaryLight,
                  ),
                  const SizedBox(width: 2),
                  Text(
                    '${distanceKm!.toStringAsFixed(1)} km',
                    style: TextStyle(
                      fontSize: 10,
                      fontWeight: FontWeight.w600,
                      color: isDark ? GBColors.textSecondaryDark : GBColors.textSecondaryLight,
                    ),
                  ),
                  const Spacer(),
                ],
                Container(
                  width: 6,
                  height: 6,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: isOnline ? GBColors.success : GBColors.textMutedLight,
                  ),
                ),
                const SizedBox(width: 4),
                Text(
                  isOnline ? 'Open' : 'Closed',
                  style: TextStyle(
                    fontSize: 10,
                    fontWeight: FontWeight.w600,
                    color: isOnline ? GBColors.success : GBColors.textMutedLight,
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

class GBProductCard extends StatelessWidget {
  final String name;
  final String unit;
  final double price;
  final double? mrp;
  final String imageUrl;
  final int quantityInCart;
  final VoidCallback onAdd;
  final VoidCallback onIncrement;
  final VoidCallback onDecrement;
  final VoidCallback? onTap;

  const GBProductCard({
    super.key,
    required this.name,
    required this.unit,
    required this.price,
    this.mrp,
    required this.imageUrl,
    required this.quantityInCart,
    required this.onAdd,
    required this.onIncrement,
    required this.onDecrement,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        decoration: BoxDecoration(
          color: isDark ? GBColors.cardDark : GBColors.cardLight,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: isDark ? GBColors.borderDark : GBColors.borderLight,
          ),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(isDark ? 0.2 : 0.03),
              blurRadius: 4,
              offset: const Offset(0, 1),
            ),
          ],
        ),
        padding: const EdgeInsets.all(8),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Product image
            Expanded(
              child: Center(
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(8),
                  child: Image.network(
                    imageUrl,
                    fit: BoxFit.contain,
                    errorBuilder: (ctx, err, stack) => const Icon(
                      Icons.shopping_bag_outlined,
                      size: 40,
                      color: GBColors.primary,
                    ),
                  ),
                ),
              ),
            ),
            const SizedBox(height: 6),
            // Unit
            Text(
              unit,
              style: TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.w500,
                color: isDark ? GBColors.textMutedDark : GBColors.textMutedLight,
              ),
            ),
            const SizedBox(height: 2),
            // Title
            Text(
              name,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
              style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600, height: 1.2),
            ),
            const SizedBox(height: 6),
            // Price & Add button row
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    if (mrp != null && mrp! > price)
                      Text(
                        '₹${mrp!.toStringAsFixed(0)}',
                        style: TextStyle(
                          fontSize: 11,
                          decoration: TextDecoration.lineThrough,
                          color: isDark ? GBColors.textMutedDark : GBColors.textMutedLight,
                        ),
                      ),
                    Text(
                      '₹${price.toStringAsFixed(0)}',
                      style: const TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.w800,
                        color: GBColors.primary,
                      ),
                    ),
                  ],
                ),
                GBAddToCartButton(
                  quantity: quantityInCart,
                  onAdd: onAdd,
                  onIncrement: onIncrement,
                  onDecrement: onDecrement,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class GBOrderStatusBadge extends StatelessWidget {
  final String status;

  const GBOrderStatusBadge({super.key, required this.status});

  @override
  Widget build(BuildContext context) {
    Color bg;
    Color fg;
    String label;

    switch (status.toUpperCase()) {
      case 'PLACED':
        bg = GBColors.placed;
        fg = GBColors.placedText;
        label = 'Placed (पुष्टि हुई)';
        break;
      case 'ACCEPTED':
      case 'PACKED':
        bg = GBColors.packing;
        fg = GBColors.packingText;
        label = 'Packing (तैयार हो रहा)';
        break;
      case 'RUNNER_ASSIGNED':
      case 'PICKED_UP':
      case 'OUT_FOR_DELIVERY':
        bg = GBColors.outForDelivery;
        fg = GBColors.outForDeliveryText;
        label = 'Out for Delivery (रास्ते में)';
        break;
      case 'DELIVERED':
        bg = GBColors.delivered;
        fg = GBColors.deliveredText;
        label = 'Delivered (पहुँचा दिया)';
        break;
      case 'CANCELLED':
      default:
        bg = GBColors.cancelled;
        fg = GBColors.cancelledText;
        label = 'Cancelled (रद्द)';
        break;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(6),
      ),
      child: Text(
        label,
        style: TextStyle(
          color: fg,
          fontSize: 11,
          fontWeight: FontWeight.w700,
        ),
      ),
    );
  }
}
