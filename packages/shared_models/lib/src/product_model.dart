class GBProduct {
  final String id;
  final String storeId;
  final String? globalProductId;
  final String nameEn;
  final String nameHi;
  final String category;
  final String unit;
  final double price;
  final double? mrp;
  final String imageUrl;
  final bool inStock;
  final int stockQuantity;

  GBProduct({
    required this.id,
    required this.storeId,
    this.globalProductId,
    required this.nameEn,
    required this.nameHi,
    required this.category,
    required this.unit,
    required this.price,
    this.mrp,
    required this.imageUrl,
    this.inStock = true,
    this.stockQuantity = 50,
  });

  String getLocalizedName(bool isHindi) => isHindi ? nameHi : nameEn;

  factory GBProduct.fromJson(Map<String, dynamic> json) {
    return GBProduct(
      id: json['id'] as String,
      storeId: json['store_id'] as String? ?? '',
      globalProductId: json['global_product_id'] as String?,
      nameEn: json['name_en'] as String? ?? json['custom_name_en'] as String? ?? 'Product',
      nameHi: json['name_hi'] as String? ?? json['custom_name_hi'] as String? ?? 'उत्पाद',
      category: json['category'] as String? ?? 'Grocery',
      unit: json['unit'] as String? ?? '1 kg',
      price: (json['price'] as num).toDouble(),
      mrp: (json['mrp'] as num?)?.toDouble(),
      imageUrl: json['image_url'] as String? ?? '',
      inStock: json['in_stock'] as bool? ?? true,
      stockQuantity: (json['stock_quantity'] as num?)?.toInt() ?? 50,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'store_id': storeId,
      'global_product_id': globalProductId,
      'name_en': nameEn,
      'name_hi': nameHi,
      'category': category,
      'unit': unit,
      'price': price,
      'mrp': mrp,
      'image_url': imageUrl,
      'in_stock': inStock,
      'stock_quantity': stockQuantity,
    };
  }
  GBProduct copyWith({
    String? id,
    String? storeId,
    String? globalProductId,
    String? nameEn,
    String? nameHi,
    String? category,
    String? unit,
    double? price,
    double? mrp,
    String? imageUrl,
    bool? inStock,
    int? stockQuantity,
  }) {
    return GBProduct(
      id: id ?? this.id,
      storeId: storeId ?? this.storeId,
      globalProductId: globalProductId ?? this.globalProductId,
      nameEn: nameEn ?? this.nameEn,
      nameHi: nameHi ?? this.nameHi,
      category: category ?? this.category,
      unit: unit ?? this.unit,
      price: price ?? this.price,
      mrp: mrp ?? this.mrp,
      imageUrl: imageUrl ?? this.imageUrl,
      inStock: inStock ?? this.inStock,
      stockQuantity: stockQuantity ?? this.stockQuantity,
    );
  }
}
