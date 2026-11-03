class GBUser {
  final String id;
  final String phone;
  final String? name;
  final String? email;
  final String role; // customer, vendor, runner, admin
  final String preferredLanguage;
  final String? avatarUrl;
  final String? primaryVillage;
  final String? primaryPanchayat;
  final bool isActive;

  GBUser({
    required this.id,
    required this.phone,
    this.name,
    this.email,
    required this.role,
    this.preferredLanguage = 'hi',
    this.avatarUrl,
    this.primaryVillage,
    this.primaryPanchayat,
    this.isActive = true,
  });

  factory GBUser.fromJson(Map<String, dynamic> json) {
    return GBUser(
      id: json['id'] as String,
      phone: json['phone'] as String,
      name: json['name'] as String?,
      email: json['email'] as String?,
      role: json['role'] as String? ?? 'customer',
      preferredLanguage: json['preferred_language'] as String? ?? 'hi',
      avatarUrl: json['avatar_url'] as String?,
      primaryVillage: json['primary_village'] as String?,
      primaryPanchayat: json['primary_panchayat'] as String?,
      isActive: json['is_active'] as bool? ?? true,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'phone': phone,
      'name': name,
      'email': email,
      'role': role,
      'preferred_language': preferredLanguage,
      'avatar_url': avatarUrl,
      'primary_village': primaryVillage,
      'primary_panchayat': primaryPanchayat,
      'is_active': isActive,
    };
  }

  GBUser copyWith({
    String? name,
    String? email,
    String? preferredLanguage,
    String? avatarUrl,
    String? primaryVillage,
    String? primaryPanchayat,
    bool? isActive,
  }) {
    return GBUser(
      id: id,
      phone: phone,
      name: name ?? this.name,
      email: email ?? this.email,
      role: role,
      preferredLanguage: preferredLanguage ?? this.preferredLanguage,
      avatarUrl: avatarUrl ?? this.avatarUrl,
      primaryVillage: primaryVillage ?? this.primaryVillage,
      primaryPanchayat: primaryPanchayat ?? this.primaryPanchayat,
      isActive: isActive ?? this.isActive,
    );
  }
}
