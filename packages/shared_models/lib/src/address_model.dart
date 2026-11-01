class GBAddress {
  final String id;
  final String userId;
  final String title;
  final String recipientName;
  final String phone;
  final double latitude;
  final double longitude;
  final String village;
  final String? landmark;
  final String block;
  final String district;
  final String state;
  final bool isDefault;

  GBAddress({
    required this.id,
    required this.userId,
    this.title = 'Home',
    required this.recipientName,
    required this.phone,
    required this.latitude,
    required this.longitude,
    required this.village,
    this.landmark,
    this.block = 'Minapur',
    this.district = 'Muzaffarpur',
    this.state = 'Bihar',
    this.isDefault = false,
  });

  String get readableAddress {
    final parts = [village];
    if (landmark != null && landmark!.isNotEmpty) {
      parts.add('Near $landmark');
    }
    parts.add(block);
    parts.add(district);
    return parts.join(', ');
  }

  factory GBAddress.fromJson(Map<String, dynamic> json) {
    return GBAddress(
      id: json['id'] as String,
      userId: json['user_id'] as String? ?? '',
      title: json['title'] as String? ?? 'Home',
      recipientName: json['recipient_name'] as String,
      phone: json['phone'] as String,
      latitude: (json['latitude'] as num).toDouble(),
      longitude: (json['longitude'] as num).toDouble(),
      village: json['village'] as String,
      landmark: json['landmark'] as String?,
      block: json['block'] as String? ?? 'Minapur',
      district: json['district'] as String? ?? 'Muzaffarpur',
      state: json['state'] as String? ?? 'Bihar',
      isDefault: json['is_default'] as bool? ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'title': title,
      'recipient_name': recipientName,
      'phone': phone,
      'latitude': latitude,
      'longitude': longitude,
      'village': village,
      'landmark': landmark,
      'block': block,
      'district': district,
      'state': state,
      'is_default': isDefault,
    };
  }
}
