class GBStore {
  String get address => '$village, ${landmark != null && landmark!.isNotEmpty ? "$landmark, " : ""}$block, $district';
  final String id;
  final String ownerId;
  final String shopName;
  final String ownerName;
  final String category;
  final double latitude;
  final double longitude;
  final String village;
  final String? landmark;
  final String block;
  final String district;
  final bool isOnline;
  final bool isApproved;
  final bool isFeatured;
  final double rating;
  final String? bannerUrl;
  final double? distanceKm;
  final String? upiId;
  final double commissionRate;

  GBStore({
    required this.id,
    required this.ownerId,
    required this.shopName,
    required this.ownerName,
    required this.category,
    required this.latitude,
    required this.longitude,
    required this.village,
    this.landmark,
    this.block = 'Minapur',
    this.district = 'Muzaffarpur',
    this.isOnline = true,
    this.isApproved = false,
    this.isFeatured = false,
    this.rating = 4.8,
    this.bannerUrl,
    this.distanceKm,
    this.upiId,
    this.commissionRate = 0.0,
  });

  factory GBStore.fromJson(Map<String, dynamic> json) {
    return GBStore(
      id: json['id'] as String,
      ownerId: json['owner_id'] as String? ?? '',
      shopName: json['shop_name'] as String,
      ownerName: json['owner_name'] as String? ?? '',
      category: json['category'] as String,
      latitude: (json['latitude'] as num).toDouble(),
      longitude: (json['longitude'] as num).toDouble(),
      village: json['village'] as String,
      landmark: json['landmark'] as String?,
      block: json['block'] as String? ?? '',
      district: json['district'] as String? ?? '',
      isOnline: json['is_online'] as bool? ?? true,
      isApproved: json['is_approved'] as bool? ?? false,
      isFeatured: json['is_featured'] as bool? ?? false,
      rating: (json['rating'] as num?)?.toDouble() ?? 4.8,
      bannerUrl: json['banner_url'] as String?,
      distanceKm: (json['distance_km'] as num?)?.toDouble(),
      upiId: json['upi_id'] as String?,
      commissionRate: (json['commission_rate'] as num?)?.toDouble() ?? 0.0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'owner_id': ownerId,
      'shop_name': shopName,
      'owner_name': ownerName,
      'category': category,
      'latitude': latitude,
      'longitude': longitude,
      'village': village,
      'landmark': landmark,
      'block': block,
      'district': district,
      'is_online': isOnline,
      'is_approved': isApproved,
      'is_featured': isFeatured,
      'rating': rating,
      'banner_url': bannerUrl,
      'distance_km': distanceKm,
      'upi_id': upiId,
      'commission_rate': commissionRate,
    };
  }

  GBStore copyWith({
    String? id,
    String? ownerId,
    String? shopName,
    String? ownerName,
    String? category,
    double? latitude,
    double? longitude,
    String? village,
    String? landmark,
    String? block,
    String? district,
    bool? isOnline,
    bool? isApproved,
    bool? isFeatured,
    double? rating,
    String? bannerUrl,
    double? distanceKm,
    String? upiId,
    double? commissionRate,
  }) {
    return GBStore(
      id: id ?? this.id,
      ownerId: ownerId ?? this.ownerId,
      shopName: shopName ?? this.shopName,
      ownerName: ownerName ?? this.ownerName,
      category: category ?? this.category,
      latitude: latitude ?? this.latitude,
      longitude: longitude ?? this.longitude,
      village: village ?? this.village,
      landmark: landmark ?? this.landmark,
      block: block ?? this.block,
      district: district ?? this.district,
      isOnline: isOnline ?? this.isOnline,
      isApproved: isApproved ?? this.isApproved,
      isFeatured: isFeatured ?? this.isFeatured,
      rating: rating ?? this.rating,
      bannerUrl: bannerUrl ?? this.bannerUrl,
      distanceKm: distanceKm ?? this.distanceKm,
      upiId: upiId ?? this.upiId,
      commissionRate: commissionRate ?? this.commissionRate,
    );
  }
}
