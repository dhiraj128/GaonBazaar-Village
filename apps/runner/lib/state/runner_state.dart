import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:shared_models/shared_models.dart';
import 'package:api_client/api_client.dart';

class RunnerAppState extends ChangeNotifier {
  final GBApiClient apiClient = GBApiClient();

  GBUser? currentUser;
  String? authToken;
  String currentLocale = 'hi';
  ThemeMode themeMode = ThemeMode.light;

  bool isOnline = true;
  bool isApproved = true;
  bool isInitialized = false;
  bool isLoadingJobs = false;

  Map<String, dynamic>? runnerProfile = {
    'id': 'run_01',
    'full_name': 'Amit Kumar',
    'vehicle_type': 'Motorcycle',
    'vehicle_number': 'BR-06-AB-1234',
    'dl_number': 'DL-0620240099881',
    'upi_id': 'amitkumar@upi',
    'rating': 4.9,
    'is_approved': true,
    'is_online': true,
  };

  double todayEarnings = 425.0;
  int completedTrips = 7;
  double cashCollectedToRemit = 0.0;

  List<GBOrder> activeJobs = [];
  Map<String, dynamic>? finances;
  List<GBNotification> notifications = [];
  int get unreadNotificationCount => notifications.where((n) => !n.isRead).length;

  bool get isHindi => currentLocale == 'hi';

  Future<void> init() async {
    try {
      await apiClient.probeAndSelectHost();
      final prefs = await SharedPreferences.getInstance();

      final savedLang = prefs.getString('gb_runner_locale');
      if (savedLang != null) currentLocale = savedLang;

      final savedTheme = prefs.getString('gb_runner_theme');
      themeMode = (savedTheme == 'dark') ? ThemeMode.dark : ThemeMode.light;

      final token = prefs.getString('gb_runner_token');
      final userJson = prefs.getString('gb_runner_user');
      if (token != null && userJson != null) {
        authToken = token;
        apiClient.setAuthToken(token);
        currentUser = GBUser.fromJson(jsonDecode(userJson) as Map<String, dynamic>);
        await fetchProfile();
        fetchJobs();
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
    notifyListeners();
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('gb_runner_locale', lang);
    } catch (_) {}
  }

  void setTheme(ThemeMode mode) async {
    themeMode = mode;
    notifyListeners();
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('gb_runner_theme', mode == ThemeMode.dark ? 'dark' : 'light');
    } catch (_) {}
  }

  void setAuth(GBUser user, String token) async {
    currentUser = user;
    authToken = token;
    apiClient.setAuthToken(token);
    notifyListeners();

    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('gb_runner_token', token);
      await prefs.setString('gb_runner_user', jsonEncode(user.toJson()));
    } catch (_) {}

    await fetchProfile();
    fetchJobs();
    fetchNotifications();
    fetchFinances();
  }

  void logout() async {
    currentUser = null;
    authToken = null;
    apiClient.clearAuthToken();
    activeJobs.clear();
    finances = null;
    notifyListeners();

    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove('gb_runner_token');
      await prefs.remove('gb_runner_user');
    } catch (_) {}
  }

  Future<void> fetchProfile() async {
    final res = await apiClient.getRunnerMe();
    if (res.isSuccess && res.data != null) {
      runnerProfile = res.data!;
      isApproved = (res.data!['is_approved'] as bool?) ?? true;
      isOnline = (res.data!['is_online'] as bool?) ?? false;
      todayEarnings = (res.data!['today_earnings'] as num?)?.toDouble() ?? 0.0;
      completedTrips = (res.data!['completed_trips'] as int?) ?? 0;
      notifyListeners();
    }
  }

  Future<String?> toggleDutyOnline() async {
    if (!isApproved) {
      return isHindi
          ? 'आपकी प्रोफ़ाइल सत्यापन प्रक्रियाधीन है। सुपर एडमिन द्वारा अनुमोदन के बाद ही आप ऑनलाइन ड्यूटी पर जा सकते हैं।'
          : 'Your profile is pending admin approval. You cannot go on duty until approved.';
    }

    final newStatus = !isOnline;
    final res = await apiClient.updateRunnerStatus(newStatus);
    if (res.isSuccess) {
      isOnline = newStatus;
      if (runnerProfile != null) {
        runnerProfile!['is_online'] = isOnline;
      }
      notifyListeners();
      return null;
    }
    return res.errorMessage ?? (isHindi ? 'स्थिति बदलने में विफल' : 'Failed to update duty status');
  }

  Future<void> fetchJobs() async {
    isLoadingJobs = true;
    notifyListeners();

    final res = await apiClient.getRunnerJobs();
    isLoadingJobs = false;
    if (res.isSuccess && res.data != null && res.data!.isNotEmpty) {
      activeJobs = res.data!;
    } else if (activeJobs.isEmpty) {
      activeJobs = [
        GBOrder(
          id: 'ord_mnp_8842',
          customerId: 'usr_c1',
          storeId: 'str_minapur_1',
          storeName: 'Raju Kirana Store (राजू किराना स्टोर)',
          runnerId: 'run_01',
          runnerName: 'Vikram Singh',
          runnerPhone: '+91 98222 22222',
          deliveryAddress: 'Ward 4, Near Shiv Mandir, Chaturshi, Minapur, Muzaffarpur',
          status: 'OUT_FOR_DELIVERY',
          subtotal: 310.0,
          deliveryFee: 15.0,
          platformFee: 3.0,
          totalAmount: 328.0,
          paymentMethod: 'COD',
          paymentStatus: 'PENDING',
          deliveryOtp: '4821',
          placedAt: DateTime.now().subtract(const Duration(minutes: 18)),
          cancelUntil: DateTime.now().subtract(const Duration(minutes: 15)),
          canCancel: false,
          cancelSecondsRemaining: 0,
          items: [
            GBOrderItem(
              id: 'item_1',
              productId: 'cat_atta',
              nameEn: 'Aashirvaad Shudh Chakki Atta 5kg',
              nameHi: 'आशीर्वाद शुद्ध चक्की आटा 5 किग्रा',
              unit: '5 kg',
              unitPrice: 210.0,
              quantity: 1,
              totalPrice: 210.0,
              imageUrl: 'https://images.unsplash.com/photo-1509440159596-0249088772ff?w=500&q=80',
            ),
            GBOrderItem(
              id: 'item_2',
              productId: 'cat_mustard_oil',
              nameEn: 'Fortune Kachi Ghani Mustard Oil 1L',
              nameHi: 'फॉर्च्यून कच्ची घानी सरसों तेल 1 ली',
              unit: '1 L',
              unitPrice: 100.0,
              quantity: 1,
              totalPrice: 100.0,
              imageUrl: 'https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=500&q=80',
            ),
          ],
          timeline: [
            GBOrderTimelineItem(
              status: 'PLACED',
              title: 'Order Placed',
              description: 'Customer placed order with COD',
              timestamp: DateTime.now().subtract(const Duration(minutes: 18)),
            ),
            GBOrderTimelineItem(
              status: 'PACKED',
              title: 'Order Packed',
              description: 'Store confirmed and packed items',
              timestamp: DateTime.now().subtract(const Duration(minutes: 10)),
            ),
            GBOrderTimelineItem(
              status: 'OUT_FOR_DELIVERY',
              title: 'Out for Delivery',
              description: 'Delivery partner picked up package',
              timestamp: DateTime.now().subtract(const Duration(minutes: 4)),
            ),
          ],
        )
      ];
    }
    notifyListeners();
  }

  Future<void> fetchFinances() async {
    final res = await apiClient.getRunnerFinances();
    if (res.isSuccess && res.data != null) {
      finances = res.data!;
      todayEarnings = (res.data!['total_delivery_earnings'] as num?)?.toDouble() ?? todayEarnings;
      completedTrips = (res.data!['total_deliveries_count'] as int?) ?? completedTrips;
      cashCollectedToRemit = (res.data!['cash_collected_to_remit'] as num?)?.toDouble() ?? 0.0;
      notifyListeners();
    }
  }

  Future<Map<String, dynamic>> handleJobAction(
    String orderId,
    String action, {
    String? deliveryOtp,
    bool? cashCollected,
  }) async {
    final res = await apiClient.runnerJobAction(
      orderId,
      action,
      deliveryOtp: deliveryOtp,
      cashCollected: cashCollected ?? (action.toUpperCase() == 'DELIVER'),
    );
    if (res.isSuccess) {
      await fetchJobs();
      fetchFinances();
      return {'success': true, 'message': res.data?['message']};
    }
    return {'success': false, 'error': res.errorMessage ?? 'Action failed'};
  }

  Future<bool> onboardRunner(Map<String, dynamic> runnerData) async {
    final res = await apiClient.onboardRunner(runnerData);
    if (res.isSuccess && res.data != null) {
      runnerProfile = res.data!;
      isApproved = (res.data!['is_approved'] as bool?) ?? false;
      isOnline = (res.data!['is_online'] as bool?) ?? false;
      notifyListeners();
      return true;
    }
    return false;
  }
  Future<void> fetchNotifications() async {
    try {
      final res = await apiClient.getNotifications();
      if (res.isSuccess && res.data != null) {
        notifications = res.data!;
      } else if (notifications.isEmpty) {
        notifications = [
          GBNotification(
            id: 'notif_run_welcome',
            title: isHindi ? 'डिलीवरी साथी ऐप में आपका स्वागत है!' : 'Welcome to Runner Partner App!',
            body: isHindi
                ? 'मीनापुर क्लस्टर में पारदर्शी 5-स्तरीय पेआउट और तत्काल यूपीआई सेटलमेंट।'
                : 'Transparent 5-tier distance payouts and direct UPI settlements in Minapur cluster.',
            timestamp: DateTime.now().subtract(const Duration(minutes: 20)),
            isRead: false,
            type: 'system',
          ),
          GBNotification(
            id: 'notif_run_batch',
            title: isHindi ? 'मल्टी-ऑर्डर बैच प्रोत्साहन' : 'Multi-order Batch Incentive',
            body: isHindi
                ? 'एक ही ट्रिप में एकाधिक डिलीवरी पूर्ण करने पर प्रति अतिरिक्त ऑर्डर अतिरिक्त पेआउट।'
                : 'Earn bonus batch payouts for bundled drop-offs along the same rural route.',
            timestamp: DateTime.now().subtract(const Duration(hours: 4)),
            isRead: true,
            type: 'payout',
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

class RunnerStateProvider extends InheritedNotifier<RunnerAppState> {
  const RunnerStateProvider({
    super.key,
    required RunnerAppState notifier,
    required super.child,
  }) : super(notifier: notifier);

  static RunnerAppState of(BuildContext context) {
    return context
        .dependOnInheritedWidgetOfExactType<RunnerStateProvider>()!
        .notifier!;
  }
}
