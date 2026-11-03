class GBNotification {
  final String id;
  final String title;
  final String body;
  final DateTime timestamp;
  final bool isRead;
  final String type; // 'order', 'delivery', 'payment', 'system', 'approval'
  final Map<String, dynamic>? metadata;

  const GBNotification({
    required this.id,
    required this.title,
    required this.body,
    required this.timestamp,
    this.isRead = false,
    this.type = 'system',
    this.metadata,
  });

  GBNotification copyWith({
    String? id,
    String? title,
    String? body,
    DateTime? timestamp,
    bool? isRead,
    String? type,
    Map<String, dynamic>? metadata,
  }) {
    return GBNotification(
      id: id ?? this.id,
      title: title ?? this.title,
      body: body ?? this.body,
      timestamp: timestamp ?? this.timestamp,
      isRead: isRead ?? this.isRead,
      type: type ?? this.type,
      metadata: metadata ?? this.metadata,
    );
  }

  factory GBNotification.fromJson(Map<String, dynamic> json) {
    return GBNotification(
      id: json['id'] as String? ?? 'notif_${DateTime.now().millisecondsSinceEpoch}',
      title: json['title'] as String? ?? '',
      body: json['body'] as String? ?? '',
      timestamp: json['timestamp'] != null
          ? DateTime.tryParse(json['timestamp'] as String) ?? DateTime.now()
          : DateTime.now(),
      isRead: json['is_read'] as bool? ?? json['isRead'] as bool? ?? false,
      type: json['type'] as String? ?? 'system',
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'body': body,
      'timestamp': timestamp.toIso8601String(),
      'is_read': isRead,
      'type': type,
      if (metadata != null) 'metadata': metadata,
    };
  }
}
