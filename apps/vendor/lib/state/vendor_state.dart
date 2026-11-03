import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:shared_models/shared_models.dart';
import 'package:api_client/api_client.dart';

class VendorAppState extends ChangeNotifier {
  final GBApiClient apiClient = GBApiClient();

  GBUser? currentUser;
  String? authToken;
  String currentLocale = 'hi';
  ThemeMode themeMode = ThemeMode.light;

  bool isStoreOnline = false;
  bool isStoreApproved = false;
  bool hasSavedLocale = false;
  bool isInitialized = false;
  bool isLoadingOrders = false;
  bool isLoadingProducts = false;

  GBStore? myStore;

  List<GBProduct> myProducts = [];
  List<GBOrder> storeOrders = [];
  Map<String, dynamic>? finances;
  List<GBNotification> notifications = [];
  int get unreadNotificationCount => notifications.where((n) => !n.isRead).length;

  bool get isHindi => currentLocale == 'hi';

  String get linkedUpiId {
    final upi = myStore?.upiId;
    if (upi == null || upi.trim().isEmpty || upi.trim() == 'vendor@upi' || upi.trim() == 'NOT_CONFIGURED') {
      return '';
    }
    return upi.trim();
  }

  int get profileCompletionPercentage {
    if (myStore == null) return 20;
    int score = 40; // Basic registration completed
    if (myStore!.village.isNotEmpty && myStore!.latitude != 0.0) score += 20; // Location confirmed
    if (myStore!.isApproved) score += 20; // Admin verification
    if (linkedUpiId.isNotEmpty) score += 20; // Payout configured
    return score.clamp(0, 100);
  }

  Future<void> init() async {
    try {
      await apiClient.probeAndSelectHost();
      final prefs = await SharedPreferences.getInstance();

      final savedLang = prefs.getString('gb_vendor_locale');
      if (savedLang != null) {
        currentLocale = savedLang;
        hasSavedLocale = true;
      }

      final savedTheme = prefs.getString('gb_vendor_theme');
      themeMode = (savedTheme == 'dark') ? ThemeMode.dark : ThemeMode.light;

      final token = prefs.getString('gb_vendor_token');
      final userJson = prefs.getString('gb_vendor_user');
      if (token != null && userJson != null) {
        authToken = token;
        apiClient.setAuthToken(token);
        currentUser = GBUser.fromJson(jsonDecode(userJson) as Map<String, dynamic>);
        await fetchStoreProfile();
        fetchOrders();
        fetchFinances();
        fetchNotifications();
      }
    } catch (_) {
    } finally {
      isInitialized = true;
      notifyListeners();
    }
  }

  void setLocale(String lang) async {
    currentLocale = lang;
    hasSavedLocale = true;
    notifyListeners();
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('gb_vendor_locale', lang);
    } catch (_) {}
  }

  void setTheme(ThemeMode mode) async {
    themeMode = mode;
    notifyListeners();
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('gb_vendor_theme', mode == ThemeMode.dark ? 'dark' : 'light');
    } catch (_) {}
  }

  void setAuth(GBUser user, String token) async {
    currentUser = user;
    authToken = token;
    apiClient.setAuthToken(token);
    notifyListeners();

    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('gb_vendor_token', token);
      await prefs.setString('gb_vendor_user', jsonEncode(user.toJson()));
    } catch (_) {}

    await fetchStoreProfile();
    fetchOrders();
    fetchFinances();
    fetchNotifications();
  }

  void updateStore(GBStore updated) {
    myStore = updated;
    isStoreOnline = updated.isOnline;
    isStoreApproved = updated.isApproved;
    notifyListeners();
  }

  void logout() async {
    currentUser = null;
    authToken = null;
    apiClient.clearAuthToken();
    myStore = null;
    isStoreApproved = false;
    isStoreOnline = false;
    storeOrders.clear();
    myProducts.clear();
    finances = null;
    notifyListeners();

    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove('gb_vendor_token');
      await prefs.remove('gb_vendor_user');
    } catch (_) {}
  }

  Future<void> fetchStoreProfile() async {
    final res = await apiClient.getMyStore();
    if (res.isSuccess && res.data != null) {
      myStore = res.data!;
      isStoreOnline = myStore!.isOnline;
      isStoreApproved = myStore!.isApproved;
      notifyListeners();
      fetchProducts();
    } else {
      isStoreApproved = false;
      notifyListeners();
    }
  }

  Future<bool> onboardStore(Map<String, dynamic> storeData) async {
    final res = await apiClient.onboardStore(storeData);
    if (res.isSuccess && res.data != null) {
      myStore = res.data!;
      isStoreOnline = myStore!.isOnline;
      isStoreApproved = myStore!.isApproved;
      notifyListeners();
      return true;
    }
    return false;
  }

  Future<bool> updateStoreProfile(Map<String, dynamic> storeData) async {
    return await onboardStore(storeData);
  }

  Future<String?> toggleStoreOnline() async {
    if (!isStoreApproved) {
      return isHindi
          ? 'दुकान सुपर एडमिन के सत्यापन के अधीन है। अनुमोदन के बाद ऑनलाइन हो सकेंगे।'
          : 'Store is pending Admin approval. You cannot go online until approved.';
    }

    final newStatus = !isStoreOnline;
    final res = await apiClient.updateStoreStatus(newStatus);
    if (res.isSuccess) {
      isStoreOnline = newStatus;
      if (myStore != null) {
        myStore = myStore!.copyWith(isOnline: isStoreOnline);
      }
      notifyListeners();
      return null;
    }
    return res.errorMessage ?? (isHindi ? 'स्थिति बदलने में विफल' : 'Failed to update store status');
  }

  Future<void> fetchOrders() async {
    isLoadingOrders = true;
    notifyListeners();

    final res = await apiClient.getVendorOrders();
    isLoadingOrders = false;
    if (res.isSuccess && res.data != null) {
      storeOrders = res.data!;
    }
    notifyListeners();
  }

  Future<void> fetchProducts() async {
    isLoadingProducts = true;
    notifyListeners();

    final res = await apiClient.getVendorProducts();
    isLoadingProducts = false;
    if (res.isSuccess && res.data != null) {
      myProducts = res.data!;
    }
    notifyListeners();
  }

  
  Future<bool> handleOrderAction(String orderId, String action) async {
    final res = await updateOrderStatus(orderId, action);
    return res['success'] == true;
  }

  Future<bool> addProduct(Map<String, dynamic> data) async {
    final res = await addCustomProduct(data);
    return res['success'] == true;
  }

  Future<void> fetchFinances() async {
    final res = await apiClient.getVendorFinances();
    if (res.isSuccess && res.data != null) {
      finances = res.data!;
      notifyListeners();
    }
  }

  Future<Map<String, dynamic>> updateOrderStatus(String orderId, String status) async {
    final res = await apiClient.updateOrderStatus(orderId, status);
    if (res.isSuccess) {
      await fetchOrders();
      fetchFinances();
      return {'success': true, 'message': res.data?['message']};
    }
    return {'success': false, 'error': res.errorMessage ?? 'Action failed'};
  }

  Future<Map<String, dynamic>> toggleProductStock(String productId, [bool? inStock]) async {
    final current = myProducts.firstWhere((p) => p.id == productId, orElse: () => myProducts.first);
    final targetStock = inStock ?? !current.inStock;
    final res = await apiClient.toggleProductStock(productId, targetStock);
    if (res.isSuccess) {
      final idx = myProducts.indexWhere((p) => p.id == productId);
      if (idx != -1) {
        myProducts[idx] = myProducts[idx].copyWith(inStock: targetStock);
        notifyListeners();
      }
      return {'success': true};
    }
    return {'success': false, 'error': res.errorMessage};
  }

  Future<Map<String, dynamic>> updateProductPrice(String productId, double price, int stock) async {
    final res = await apiClient.updateProductInventory(productId, price, stock);
    if (res.isSuccess) {
      await fetchProducts();
      return {'success': true};
    }
    return {'success': false, 'error': res.errorMessage};
  }

  Future<Map<String, dynamic>> addCustomProduct(Map<String, dynamic> productData) async {
    final res = await apiClient.createVendorProduct(productData);
    if (res.isSuccess) {
      await fetchProducts();
      return {'success': true};
    }
    return {'success': false, 'error': res.errorMessage};
  }

  Future<void> fetchNotifications() async {
    try {
      final res = await apiClient.getNotifications();
      if (res.isSuccess && res.data != null) {
        notifications = res.data!;
      } else if (notifications.isEmpty) {
        notifications = [
          GBNotification(
            id: 'notif_ven_welcome',
            title: isHindi ? 'विक्रेता ऐप में आपका स्वागत है!' : 'Welcome to Vendor App!',
            body: isHindi
                ? 'गाँव बाज़ार में आपका स्वागत है। अपनी दुकान चालू रखें और 0% कमीशन पर सीधे गाँव में उत्पाद बेचें।'
                : 'Welcome to GaonBazaar! Keep your store online to fulfill rural quick-commerce orders with 0% commission.',
            timestamp: DateTime.now().subtract(const Duration(minutes: 10)),
            isRead: false,
            type: 'system',
          ),
        ];
      }
      notifyListeners();
    } catch (_) {}
  }

  Future<void> markAllNotificationsRead() async {
    notifications = notifications.map((n) => n.copyWith(isRead: true)).toList();
    notifyListeners();
    try {
      await apiClient.markAllNotificationsRead();
    } catch (_) {}
  }

  Future<Map<String, dynamic>> verifyPennyDrop({
    required String accountHolderName,
    String? accountNumber,
    String? ifscCode,
    String? upiId,
  }) async {
    final res = await apiClient.verifyPennyDrop(
      accountHolderName: accountHolderName,
      accountNumber: accountNumber,
      ifscCode: ifscCode,
      upiId: upiId,
    );
    if (res.isSuccess && res.data != null) {
      return {'success': true, 'data': res.data};
    }
    return {'success': false, 'error': res.errorMessage ?? 'Verification failed'};
  }

  Future<Map<String, dynamic>> updateBankDetails({
    required String accountHolderName,
    required String accountNumber,
    required String ifscCode,
    required String otp,
  }) async {
    final res = await apiClient.updateStoreBank(
      accountHolderName: accountHolderName,
      accountNumber: accountNumber,
      ifscCode: ifscCode,
      otp: otp,
    );
    if (res.isSuccess) {
      await fetchStoreProfile();
      return {'success': true, 'message': res.data?['message'], 'cooldown_hours': res.data?['cooldown_hours']};
    }
    return {'success': false, 'error': res.errorMessage ?? 'Bank update failed'};
  }

  Future<Map<String, dynamic>> handoffOrder(String orderId, String handoverCode) async {
    final res = await apiClient.vendorHandoffOrder(orderId, handoverCode);
    if (res.isSuccess) {
      await fetchOrders();
      return {'success': true, 'message': res.data?['message']};
    }
    return {'success': false, 'error': res.errorMessage ?? 'Handover failed'};
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
