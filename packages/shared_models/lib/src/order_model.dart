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
  final String? customerName;
  final String? customerPhone;
  final String storeId;
  final String storeName;
  final String? storePhone;
  final String? runnerId;
  final String? runnerName;
  final String? runnerPhone;
  final String deliveryAddress;
  final double? storeLatitude;
  final double? storeLongitude;
  final String? storeAddress;
  final double? deliveryLatitude;
  final double? deliveryLongitude;
  final double? distanceKm;
  final String? cancellationReason;
  final String status; // PLACED, ACCEPTED, PACKED, RUNNER_ASSIGNED, PICKED_UP, OUT_FOR_DELIVERY, DELIVERED, CANCELLED
  final double subtotal;
  final double deliveryFee;
  final double platformFee;
  final double totalAmount;
  final String paymentMethod;
  final String paymentStatus;
  final String deliveryOtp;
  final double? runnerPayout;
  final DateTime placedAt;
  final DateTime cancelUntil;
  final bool canCancel;
  final int cancelSecondsRemaining;
  final List<GBOrderItem> items;
  final List<GBOrderTimelineItem> timeline;

  GBOrder({
    required this.id,
    required this.customerId,
    this.customerName,
    this.customerPhone,
    required this.storeId,
    required this.storeName,
    this.storePhone,
    this.runnerId,
    this.runnerName,
    this.runnerPhone,
    required this.deliveryAddress,
    this.storeLatitude,
    this.storeLongitude,
    this.storeAddress,
    this.deliveryLatitude,
    this.deliveryLongitude,
    this.distanceKm,
    this.cancellationReason,
    required this.status,
    required this.subtotal,
    required this.deliveryFee,
    required this.platformFee,
    required this.totalAmount,
    required this.paymentMethod,
    required this.paymentStatus,
    required this.deliveryOtp,
    this.runnerPayout,
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
      customerName: json['customer_name'] as String?,
      customerPhone: json['customer_phone'] as String?,
      storeId: json['store_id'] as String,
      storeName: json['store_name'] as String,
      storePhone: json['store_phone'] as String?,
      runnerId: json['runner_id'] as String?,
      runnerName: json['runner_name'] as String?,
      runnerPhone: json['runner_phone'] as String?,
      deliveryAddress: json['delivery_address'] as String,
      storeLatitude: (json['store_latitude'] as num?)?.toDouble(),
      storeLongitude: (json['store_longitude'] as num?)?.toDouble(),
      storeAddress: json['store_address'] as String?,
      deliveryLatitude: (json['delivery_latitude'] as num?)?.toDouble(),
      deliveryLongitude: (json['delivery_longitude'] as num?)?.toDouble(),
      distanceKm: (json['distance_km'] as num?)?.toDouble(),
      cancellationReason: json['cancellation_reason'] as String?,
      status: json['status'] as String,
      subtotal: (json['subtotal'] as num).toDouble(),
      deliveryFee: (json['delivery_fee'] as num).toDouble(),
      platformFee: (json['platform_fee'] as num).toDouble(),
      totalAmount: (json['total_amount'] as num).toDouble(),
      paymentMethod: json['payment_method'] as String,
      paymentStatus: json['payment_status'] as String,
      deliveryOtp: json['delivery_otp'] as String? ?? '',
      runnerPayout: (json['runner_payout'] as num?)?.toDouble() ?? _deriveRunnerPayout((json['delivery_fee'] as num).toDouble()),
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

  static double _deriveRunnerPayout(double deliveryFee) {
    if (deliveryFee <= 15.0) return 10.0;
    if (deliveryFee <= 20.0) return 14.0;
    if (deliveryFee <= 25.0) return 18.0;
    if (deliveryFee <= 30.0) return 22.0;
    return 28.0;
  }
}


class GBOrderMessage {
  final String id;
  final String orderId;
  final String senderId;
  final String senderRole;
  final String senderName;
  final String messageType; // TEXT, LOCATION_PIN, LIVE_LOCATION_START, LIVE_LOCATION_STOP
  final String? content;
  final double? latitude;
  final double? longitude;
  final String? locationTitle;
  final DateTime createdAt;

  GBOrderMessage({
    required this.id,
    required this.orderId,
    required this.senderId,
    required this.senderRole,
    required this.senderName,
    required this.messageType,
    this.content,
    this.latitude,
    this.longitude,
    this.locationTitle,
    required this.createdAt,
  });

  factory GBOrderMessage.fromJson(Map<String, dynamic> json) {
    return GBOrderMessage(
      id: json['id'] as String,
      orderId: json['order_id'] as String,
      senderId: json['sender_id'] as String,
      senderRole: json['sender_role'] as String,
      senderName: json['sender_name'] as String,
      messageType: json['message_type'] as String? ?? 'TEXT',
      content: json['content'] as String?,
      latitude: (json['latitude'] as num?)?.toDouble(),
      longitude: (json['longitude'] as num?)?.toDouble(),
      locationTitle: json['location_title'] as String?,
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'order_id': orderId,
      'sender_id': senderId,
      'sender_role': senderRole,
      'sender_name': senderName,
      'message_type': messageType,
      'content': content,
      'latitude': latitude,
      'longitude': longitude,
      'location_title': locationTitle,
      'created_at': createdAt.toIso8601String(),
    };
  }
}