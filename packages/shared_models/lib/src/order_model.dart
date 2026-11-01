class GBOrderItem {
  final String id;
  final String productId;
  final String nameEn;
  final String nameHi;
  final String unit;
  final double unitPrice;
  final int quantity;
  final double totalPrice;
  final String? imageUrl;

  GBOrderItem({
    required this.id,
    required this.productId,
    required this.nameEn,
    required this.nameHi,
    required this.unit,
    required this.unitPrice,
    required this.quantity,
    required this.totalPrice,
    this.imageUrl,
  });

  factory GBOrderItem.fromJson(Map<String, dynamic> json) {
    return GBOrderItem(
      id: json['id'] as String,
      productId: json['product_id'] as String,
      nameEn: json['name_en'] as String,
      nameHi: json['name_hi'] as String,
      unit: json['unit'] as String,
      unitPrice: (json['unit_price'] as num).toDouble(),
      quantity: (json['quantity'] as num).toInt(),
      totalPrice: (json['total_price'] as num).toDouble(),
      imageUrl: json['image_url'] as String?,
    );
  }
}

class GBOrderTimelineItem {
  final String status;
  final String title;
  final String? description;
  final DateTime timestamp;

  GBOrderTimelineItem({
    required this.status,
    required this.title,
    this.description,
    required this.timestamp,
  });

  factory GBOrderTimelineItem.fromJson(Map<String, dynamic> json) {
    return GBOrderTimelineItem(
      status: json['status'] as String,
      title: json['title'] as String,
      description: json['description'] as String?,
      timestamp: DateTime.parse(json['timestamp'] as String),
    );
  }
}

class GBOrder {
  final String id;
  final String customerId;
  final String storeId;
  final String storeName;
  final String? runnerId;
  final String? runnerName;
  final String? runnerPhone;
  final String deliveryAddress;
  final String status; // PLACED, ACCEPTED, PACKED, RUNNER_ASSIGNED, PICKED_UP, OUT_FOR_DELIVERY, DELIVERED, CANCELLED
  final double subtotal;
  final double deliveryFee;
  final double platformFee;
  final double totalAmount;
  final String paymentMethod;
  final String paymentStatus;
  final String deliveryOtp;
  final DateTime placedAt;
  final DateTime cancelUntil;
  final bool canCancel;
  final int cancelSecondsRemaining;
  final List<GBOrderItem> items;
  final List<GBOrderTimelineItem> timeline;

  GBOrder({
    required this.id,
    required this.customerId,
    required this.storeId,
    required this.storeName,
    this.runnerId,
    this.runnerName,
    this.runnerPhone,
    required this.deliveryAddress,
    required this.status,
    required this.subtotal,
    required this.deliveryFee,
    required this.platformFee,
    required this.totalAmount,
    required this.paymentMethod,
    required this.paymentStatus,
    required this.deliveryOtp,
    required this.placedAt,
    required this.cancelUntil,
    required this.canCancel,
    required this.cancelSecondsRemaining,
    required this.items,
    required this.timeline,
  });

  factory GBOrder.fromJson(Map<String, dynamic> json) {
    return GBOrder(
      id: json['id'] as String,
      customerId: json['customer_id'] as String,
      storeId: json['store_id'] as String,
      storeName: json['store_name'] as String,
      runnerId: json['runner_id'] as String?,
      runnerName: json['runner_name'] as String?,
      runnerPhone: json['runner_phone'] as String?,
      deliveryAddress: json['delivery_address'] as String,
      status: json['status'] as String,
      subtotal: (json['subtotal'] as num).toDouble(),
      deliveryFee: (json['delivery_fee'] as num).toDouble(),
      platformFee: (json['platform_fee'] as num).toDouble(),
      totalAmount: (json['total_amount'] as num).toDouble(),
      paymentMethod: json['payment_method'] as String,
      paymentStatus: json['payment_status'] as String,
      deliveryOtp: json['delivery_otp'] as String,
      placedAt: DateTime.parse(json['placed_at'] as String),
      cancelUntil: DateTime.parse(json['cancel_until'] as String),
      canCancel: json['can_cancel'] as bool? ?? false,
      cancelSecondsRemaining: (json['cancel_seconds_remaining'] as num?)?.toInt() ?? 0,
      items: (json['items'] as List<dynamic>?)
              ?.map((item) => GBOrderItem.fromJson(item as Map<String, dynamic>))
              .toList() ??
          [],
      timeline: (json['timeline'] as List<dynamic>?)
              ?.map((item) => GBOrderTimelineItem.fromJson(item as Map<String, dynamic>))
              .toList() ??
          [],
    );
  }
}
