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
    notifyListeners();
  }

  void logout() async {
    currentUser = null;
    authToken = null;
    apiClient.clearAuthToken();
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
    }
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
        myStore = GBStore(
          id: myStore!.id,
          ownerId: myStore!.ownerId,
          shopName: myStore!.shopName,
          ownerName: myStore!.ownerName,
          category: myStore!.category,
          latitude: myStore!.latitude,
          longitude: myStore!.longitude,
          village: myStore!.village,
          landmark: myStore!.landmark,
          block: myStore!.block,
          district: myStore!.district,
          isOnline: isStoreOnline,
          isApproved: myStore!.isApproved,
          isFeatured: myStore!.isFeatured,
          rating: myStore!.rating,
          bannerUrl: myStore!.bannerUrl,
        );
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
    if (myStore == null) return;
    isLoadingProducts = true;
    notifyListeners();

    final res = await apiClient.getStoreProducts(myStore!.id);
    isLoadingProducts = false;
    if (res.isSuccess && res.data != null) {
      myProducts = res.data!;
    }
    notifyListeners();
  }

  Future<void> fetchFinances() async {
    final res = await apiClient.getVendorFinances();
    if (res.isSuccess && res.data != null) {
      finances = res.data!;
      notifyListeners();
    }
  }

  Future<bool> handleOrderAction(String orderId, String action) async {
    final res = await apiClient.vendorOrderAction(orderId, action);
    if (res.isSuccess) {
      await fetchOrders();
      fetchFinances();
      return true;
    }
    return false;
  }

  Future<bool> addProduct(Map<String, dynamic> productData) async {
    final res = await apiClient.addVendorProduct(productData);
    if (res.isSuccess && res.data != null) {
      myProducts.insert(0, res.data!);
      notifyListeners();
      return true;
    }
    return false;
  }

  Future<void> toggleProductStock(String productId) async {
    final idx = myProducts.indexWhere((p) => p.id == productId);
    if (idx != -1) {
      final current = myProducts[idx];
      final newStock = !current.inStock;
      final res = await apiClient.updateProductStock(productId, inStock: newStock);
      if (res.isSuccess) {
        myProducts[idx] = GBProduct(
          id: current.id,
          storeId: current.storeId,
          nameEn: current.nameEn,
          nameHi: current.nameHi,
          category: current.category,
          unit: current.unit,
          price: current.price,
          mrp: current.mrp,
          imageUrl: current.imageUrl,
          inStock: newStock,
          stockQuantity: current.stockQuantity,
        );
        notifyListeners();
      }
    }
  }
  Future<void> fetchNotifications() async {
    try {
      final res = await apiClient.getNotifications();
      if (res.isSuccess && res.data != null) {
        notifications = res.data!;
      } else if (notifications.isEmpty) {
        notifications = [
          GBNotification(
            id: 'notif_vend_welcome',
            title: isHindi ? 'दुकानदार पोर्टल में आपका स्वागत है' : 'Welcome to Shopkeeper Portal',
            body: isHindi
                ? 'गाँव बाज़ार 0% कमीशन पर आपकी दुकान को सीधे ग्रामीण ग्राहकों से जोड़ता है।'
                : 'GaonBazaar connects your village shop directly to customers at 0% commission.',
            timestamp: DateTime.now().subtract(const Duration(minutes: 30)),
            isRead: false,
            type: 'system',
          ),
          GBNotification(
            id: 'notif_vend_payout',
            title: isHindi ? 'दैनिक सेटलमेंट सक्रिय' : 'Daily Settlement Active',
            body: isHindi
                ? 'आपके बैंक / यूपीआई खाते में कल के सभी पूर्ण ऑर्डर का भुगतान प्रोसेस हो चुका है।'
                : 'Payout for all delivered orders processed to your linked UPI/Bank account.',
            timestamp: DateTime.now().subtract(const Duration(hours: 3)),
            isRead: true,
            type: 'settlement',
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
