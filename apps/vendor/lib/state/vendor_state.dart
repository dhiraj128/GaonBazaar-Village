import 'package:flutter/material.dart';
import 'package:shared_models/shared_models.dart';
import 'package:api_client/api_client.dart';

class VendorAppState extends ChangeNotifier {
  final GBApiClient apiClient = GBApiClient();

  GBUser? currentUser;
  String? authToken;
  String currentLocale = 'hi';
  ThemeMode themeMode = ThemeMode.light;

  bool isStoreOnline = true;
  bool isStoreApproved = true;

  GBStore? myStore = GBStore(
    id: 'str_01',
    ownerId: 'usr_v1',
    shopName: 'माँ शारदा किराना स्टोर',
    ownerName: 'Raju Sharma',
    category: 'Grocery',
    latitude: 26.2230,
    longitude: 85.3520,
    village: 'Chaturshi / Chatursi',
    landmark: 'Near Gram Panchayat Bhavan',
    block: 'Minapur',
    district: 'Muzaffarpur',
    isOnline: true,
    isApproved: true,
    rating: 4.9,
  );

  List<GBProduct> myProducts = [];
  List<GBOrder> storeOrders = [];

  bool get isHindi => currentLocale == 'hi';

  void setLocale(String lang) {
    currentLocale = lang;
    notifyListeners();
  }

  void toggleStoreOnline() {
    isStoreOnline = !isStoreOnline;
    notifyListeners();
  }

  void setAuth(GBUser user, String token) {
    currentUser = user;
    authToken = token;
    apiClient.setAuthToken(token);
    notifyListeners();
  }

  void updateOrderStatus(String orderId, String newStatus) {
    for (final o in storeOrders) {
      if (o.id == orderId) {
        // update status
        break;
      }
    }
    notifyListeners();
  }

  void addProduct(GBProduct product) {
    myProducts.insert(0, product);
    notifyListeners();
  }

  void toggleProductStock(String productId) {
    for (int i = 0; i < myProducts.length; i++) {
      if (myProducts[i].id == productId) {
        final p = myProducts[i];
        myProducts[i] = GBProduct(
          id: p.id,
          storeId: p.storeId,
          nameEn: p.nameEn,
          nameHi: p.nameHi,
          category: p.category,
          unit: p.unit,
          price: p.price,
          mrp: p.mrp,
          imageUrl: p.imageUrl,
          inStock: !p.inStock,
          stockQuantity: p.stockQuantity,
        );
        break;
      }
    }
    notifyListeners();
  }
}

class VendorStateProvider extends InheritedNotifier<VendorAppState> {
  const VendorStateProvider({
    super.key,
    required VendorAppState notifier,
    required super.child,
  }) : super(notifier: notifier);

  static VendorAppState of(BuildContext context) {
    return context
        .dependOnInheritedWidgetOfExactType<VendorStateProvider>()!
        .notifier!;
  }
}
