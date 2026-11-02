import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:shared_models/shared_models.dart';
import 'package:api_client/api_client.dart';

class CustomerAppState extends ChangeNotifier {
  final GBApiClient apiClient = GBApiClient();

  GBUser? currentUser;
  String? authToken;
  String currentLocale = 'hi'; // Default Hindi
  ThemeMode themeMode = ThemeMode.light; // Explicit Light / Dark (No system)
  bool isInitialized = false;

  // Selected Address
  GBAddress selectedAddress = GBAddress(
    id: 'addr_default_1',
    userId: 'usr_c1',
    title: 'Home',
    recipientName: '',
    phone: '',
    latitude: 26.2230,
    longitude: 85.3520,
    village: 'Chaturshi / Chatursi',
    landmark: 'Near Gram Panchayat Bhavan',
    block: 'Minapur',
    district: 'Muzaffarpur',
    state: 'Bihar',
    isDefault: true,
  );

  List<GBAddress> savedAddresses = [];

  // Cart
  final Map<String, GBCartItem> _cartItems = {}; // productId -> GBCartItem
  String? currentCartStoreId;
  String? currentCartStoreName;

  // Orders
  List<GBOrder> myOrders = [];
  bool isLoadingOrders = false;

  bool get isHindi => currentLocale == 'hi';
  bool get isAuthenticated => authToken != null && currentUser != null;

  List<GBCartItem> get cartItems => _cartItems.values.toList();
  int get cartCount => _cartItems.values.fold(0, (sum, i) => sum + i.quantity);

  double get cartSubtotal =>
      _cartItems.values.fold(0.0, (sum, i) => sum + i.totalPrice);
  double get cartDeliveryFee {
    if (_cartItems.isEmpty) return 0.0;
    // Default pilot distance 0.8 km (Tier 1: 0-2 km is ₹15.0)
    const dist = 0.8;
    if (dist <= 2.0) return 15.0;
    if (dist <= 4.0) return 20.0;
    if (dist <= 5.0) return 25.0;
    return 35.0;
  }
  double get cartPlatformFee => _cartItems.isEmpty ? 0.0 : 3.0; // Strict ₹3 fee
  double get cartTotal =>
      _cartItems.isEmpty ? 0.0 : cartSubtotal + cartDeliveryFee + cartPlatformFee;

  int getItemQuantity(String productId) {
    return _cartItems[productId]?.quantity ?? 0;
  }

  /// Initialize state from persistent storage and probe backend host
  Future<void> init() async {
    try {
      await apiClient.probeAndSelectHost();
      final prefs = await SharedPreferences.getInstance();
      
      // Load Locale
      final savedLang = prefs.getString('gb_app_locale');
      if (savedLang != null && (savedLang == 'hi' || savedLang == 'en')) {
        currentLocale = savedLang;
      }

      // Load Theme (Explicit Light or Dark)
      final savedTheme = prefs.getString('gb_app_theme');
      if (savedTheme == 'dark') {
        themeMode = ThemeMode.dark;
      } else {
        themeMode = ThemeMode.light;
      }

      // Load Auth Token
      final token = prefs.getString('gb_auth_token');
      final userJson = prefs.getString('gb_user_data');
      if (token != null && userJson != null) {
        authToken = token;
        apiClient.setAuthToken(token);
        currentUser = GBUser.fromJson(jsonDecode(userJson) as Map<String, dynamic>);
        
        // Fetch fresh profile and orders in background
        fetchProfile();
        fetchOrders();
        fetchAddresses();
      }

      // Load Selected Address
      final addressJson = prefs.getString('gb_selected_address');
      if (addressJson != null) {
        selectedAddress = GBAddress.fromJson(jsonDecode(addressJson) as Map<String, dynamic>);
      }
    } catch (_) {
      // Graceful fallback
    } finally {
      isInitialized = true;
      notifyListeners();
    }
  }

  void setLocale(String lang) async {
    currentLocale = lang;
    notifyListeners();
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('gb_app_locale', lang);
    } catch (_) {}
  }

  void setTheme(ThemeMode mode) async {
    themeMode = mode;
    notifyListeners();
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('gb_app_theme', mode == ThemeMode.dark ? 'dark' : 'light');
    } catch (_) {}
  }

  void setAuth(GBUser user, String token) async {
    currentUser = user;
    authToken = token;
    apiClient.setAuthToken(token);
    notifyListeners();

    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('gb_auth_token', token);
      await prefs.setString('gb_user_data', jsonEncode(user.toJson()));
    } catch (_) {}

    fetchProfile();
    fetchOrders();
    fetchAddresses();
  }

  void logout() async {
    currentUser = null;
    authToken = null;
    apiClient.clearAuthToken();
    _cartItems.clear();
    currentCartStoreId = null;
    currentCartStoreName = null;
    myOrders.clear();
    savedAddresses.clear();
    notifyListeners();

    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove('gb_auth_token');
      await prefs.remove('gb_user_data');
    } catch (_) {}
  }

  Future<void> fetchProfile() async {
    if (authToken == null) return;
    final res = await apiClient.getCurrentUser();
    if (res.isSuccess && res.data != null) {
      currentUser = res.data;
      notifyListeners();
      try {
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('gb_user_data', jsonEncode(currentUser!.toJson()));
      } catch (_) {}
    }
  }

  Future<bool> updateProfile({String? name, String? email, String? preferredLanguage}) async {
    if (authToken == null) return false;
    final res = await apiClient.updateProfile(
      name: name,
      email: email,
      preferredLanguage: preferredLanguage,
    );
    if (res.isSuccess && res.data != null) {
      currentUser = res.data;
      notifyListeners();
      try {
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('gb_user_data', jsonEncode(currentUser!.toJson()));
      } catch (_) {}
      return true;
    }
    return false;
  }

  Future<void> fetchOrders() async {
    if (authToken == null) return;
    isLoadingOrders = true;
    notifyListeners();

    final res = await apiClient.getCustomerOrders();
    isLoadingOrders = false;
    if (res.isSuccess && res.data != null) {
      myOrders = res.data!;
    }
    notifyListeners();
  }

  Future<void> fetchAddresses() async {
    if (authToken == null) return;
    final res = await apiClient.getSavedAddresses();
    if (res.isSuccess && res.data != null) {
      savedAddresses = res.data!;
      if (savedAddresses.isNotEmpty) {
        final defaultAddr = savedAddresses.firstWhere(
          (a) => a.isDefault,
          orElse: () => savedAddresses.first,
        );
        selectedAddress = defaultAddr;
      }
      notifyListeners();
    }
  }

  Future<bool> saveAddress(GBAddress address) async {
    final res = await apiClient.createAddress(address);
    if (res.isSuccess && res.data != null) {
      selectedAddress = res.data!;
      await fetchAddresses();
      try {
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('gb_selected_address', jsonEncode(selectedAddress.toJson()));
      } catch (_) {}
      return true;
    }
    return false;
  }

  Future<bool> deleteAddress(String addressId) async {
    final res = await apiClient.deleteAddress(addressId);
    if (res.isSuccess) {
      await fetchAddresses();
      return true;
    }
    return false;
  }

  void setAddress(GBAddress address) async {
    selectedAddress = address;
    notifyListeners();
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('gb_selected_address', jsonEncode(address.toJson()));
    } catch (_) {}
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
