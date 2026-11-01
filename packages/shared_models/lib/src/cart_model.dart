import 'product_model.dart';

class GBCartItem {
  final GBProduct product;
  int quantity;

  GBCartItem({
    required this.product,
    this.quantity = 1,
  });

  double get totalPrice => product.price * quantity;

  Map<String, dynamic> toJson() {
    return {
      'product_id': product.id,
      'quantity': quantity,
    };
  }
}

class GBCartSummary {
  final List<GBCartItem> items;
  final String? storeId;
  final String? storeName;
  final double subtotal;
  final double deliveryFee;
  final double platformFee; // Strict ₹3.00
  final double totalAmount;
  final bool isServiceable;
  final double? distanceKm;

  GBCartSummary({
    required this.items,
    this.storeId,
    this.storeName,
    required this.subtotal,
    required this.deliveryFee,
    this.platformFee = 3.0,
    required this.totalAmount,
    this.isServiceable = true,
    this.distanceKm,
  });

  int get totalItemCount => items.fold(0, (sum, i) => sum + i.quantity);
}
