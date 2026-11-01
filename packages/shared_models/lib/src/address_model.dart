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
  final String? houseNumber;
  final String? street;
  final String? panchayat;
  final String? postOffice;
  final String? pinCode;
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
    this.houseNumber,
    this.street,
    this.panchayat,
    this.postOffice,
    this.pinCode,
    this.block = 'Minapur',
    this.district = 'Muzaffarpur',
    this.state = 'Bihar',
    this.isDefault = false,
  });

  String get readableAddress {
    final parts = <String>[];
    if (houseNumber != null && houseNumber!.isNotEmpty) parts.add(houseNumber!);
    if (street != null && street!.isNotEmpty) parts.add(street!);
    parts.add(village);
    if (landmark != null && landmark!.isNotEmpty) parts.add('Near $landmark');
    if (panchayat != null && panchayat!.isNotEmpty) parts.add('Panchayat: $panchayat');
    parts.add(block);
    parts.add(district);
    if (pinCode != null && pinCode!.isNotEmpty) parts.add(pinCode!);
    return parts.join(', ');
  }

  factory GBAddress.fromJson(Map<String, dynamic> json) {
    return GBAddress(
      id: json['id'] as String? ?? 'addr_local',
      userId: json['user_id'] as String? ?? '',
      title: json['title'] as String? ?? 'Home',
      recipientName: json['recipient_name'] as String? ?? 'Customer',
      phone: json['phone'] as String? ?? '',
      latitude: (json['latitude'] as num?)?.toDouble() ?? 26.2230,
      longitude: (json['longitude'] as num?)?.toDouble() ?? 85.3520,
      village: json['village'] as String? ?? 'Chaturshi',
      landmark: json['landmark'] as String?,
      houseNumber: json['house_number'] as String?,
      street: json['street'] as String?,
      panchayat: json['panchayat'] as String?,
      postOffice: json['post_office'] as String?,
      pinCode: json['pin_code'] as String?,
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
      'house_number': houseNumber,
      'street': street,
      'panchayat': panchayat,
      'post_office': postOffice,
      'pin_code': pinCode,
      'block': block,
      'district': district,
      'state': state,
      'is_default': isDefault,
    };
  }
}
