class GBUser {
  final String id;
  final String phone;
  final String? name;
  final String role; // customer, vendor, runner, admin
  final String preferredLanguage;
  final bool isActive;

  GBUser({
    required this.id,
    required this.phone,
    this.name,
    required this.role,
    this.preferredLanguage = 'hi',
    this.isActive = true,
  });

  factory GBUser.fromJson(Map<String, dynamic> json) {
    return GBUser(
      id: json['id'] as String,
      phone: json['phone'] as String,
      name: json['name'] as String?,
      role: json['role'] as String? ?? 'customer',
      preferredLanguage: json['preferred_language'] as String? ?? 'hi',
      isActive: json['is_active'] as bool? ?? true,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'phone': phone,
      'name': name,
      'role': role,
      'preferred_language': preferredLanguage,
      'is_active': isActive,
    };
  }
}
