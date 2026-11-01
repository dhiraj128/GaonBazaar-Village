import 'package:flutter/material.dart';
import 'package:shared_models/shared_models.dart';
import 'package:api_client/api_client.dart';

class CustomerAppState extends ChangeNotifier {
  final GBApiClient apiClient = GBApiClient();

  GBUser? currentUser;
  String? authToken;
  String currentLocale = 'hi'; // Default Hindi
  ThemeMode themeMode = ThemeMode.light;

  // Selected Address
  GBAddress selectedAddress = GBAddress(
    id: 'addr_c1',
    userId: 'usr_c1',
    title: 'Home',
    recipientName: 'Ramesh Singh',
    phone: '9876543210',
    latitude: 26.2230,
    longitude: 85.3520,
    village: 'Chaturshi / Chatursi',
    landmark: 'Near Gram Panchayat Bhavan',
    block: 'Minapur',
    district: 'Muzaffarpur',
    isDefault: true,
  );

  List<GBAddress> savedAddresses = [];

  // Cart
  final Map<String, GBCartItem> _cartItems = {}; // productId -> GBCartItem
  String? currentCartStoreId;
  String? currentCartStoreName;

  // Active Orders
  List<GBOrder> myOrders = [];

  bool get isHindi => currentLocale == 'hi';
  List<GBCartItem> get cartItems => _cartItems.values.toList();
  int get cartCount => _cartItems.values.fold(0, (sum, i) => sum + i.quantity);

  double get cartSubtotal =>
      _cartItems.values.fold(0.0, (sum, i) => sum + i.totalPrice);
  double get cartDeliveryFee => _cartItems.isEmpty ? 0.0 : 15.0;
  double get cartPlatformFee => _cartItems.isEmpty ? 0.0 : 3.0; // Strict ₹3 fee
  double get cartTotal =>
      _cartItems.isEmpty ? 0.0 : cartSubtotal + cartDeliveryFee + cartPlatformFee;

  int getItemQuantity(String productId) {
    return _cartItems[productId]?.quantity ?? 0;
  }

  void setLocale(String lang) {
    currentLocale = lang;
    notifyListeners();
  }

  void toggleTheme() {
    themeMode = themeMode == ThemeMode.light ? ThemeMode.dark : ThemeMode.light;
    notifyListeners();
  }

  void setAuth(GBUser user, String token) {
    currentUser = user;
    authToken = token;
    apiClient.setAuthToken(token);
    notifyListeners();
  }

  void logout() {
    currentUser = null;
    authToken = null;
    apiClient.clearAuthToken();
    _cartItems.clear();
    currentCartStoreId = null;
    notifyListeners();
  }

  void setAddress(GBAddress address) {
    selectedAddress = address;
    notifyListeners();
  }

  void addToCart(GBProduct product, String storeName) {
    if (currentCartStoreId != null && currentCartStoreId != product.storeId) {
      _cartItems.clear();
    }
    currentCartStoreId = product.storeId;
    currentCartStoreName = storeName;

    if (_cartItems.containsKey(product.id)) {
      _cartItems[product.id]!.quantity += 1;
    } else {
      _cartItems[product.id] = GBCartItem(product: product, quantity: 1);
    }
    notifyListeners();
  }

  void incrementItem(String productId) {
    if (_cartItems.containsKey(productId)) {
      _cartItems[productId]!.quantity += 1;
      notifyListeners();
    }
  }

  void decrementItem(String productId) {
    if (_cartItems.containsKey(productId)) {
      if (_cartItems[productId]!.quantity > 1) {
        _cartItems[productId]!.quantity -= 1;
      } else {
        _cartItems.remove(productId);
        if (_cartItems.isEmpty) {
          currentCartStoreId = null;
          currentCartStoreName = null;
        }
      }
      notifyListeners();
    }
  }

  void clearCart() {
    _cartItems.clear();
    currentCartStoreId = null;
    currentCartStoreName = null;
    notifyListeners();
  }

  void addOrder(GBOrder order) {
    myOrders.insert(0, order);
    notifyListeners();
  }
}

class AppStateProvider extends InheritedNotifier<CustomerAppState> {
  const AppStateProvider({
    super.key,
    required CustomerAppState notifier,
    required super.child,
  }) : super(notifier: notifier);

  static CustomerAppState of(BuildContext context) {
    return context
        .dependOnInheritedWidgetOfExactType<AppStateProvider>()!
        .notifier!;
  }
}
