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

  bool isOnline = false;
  bool isApproved = false;
  bool isInitialized = false;
  bool hasSavedLocale = false;
  bool isLoadingJobs = false;

  Map<String, dynamic>? runnerProfile;

  double todayEarnings = 0.0;
  int completedTrips = 0;
  double cashCollectedToRemit = 0.0;

  List<GBOrder> activeJobs = [];
  Map<String, dynamic>? finances;
  List<GBNotification> notifications = [];
  int get unreadNotificationCount => notifications.where((n) => !n.isRead).length;

  bool get isHindi => currentLocale == 'hi';

  double get totalDeliveryEarnings => (finances?['total_delivery_earnings'] as num?)?.toDouble() ?? todayEarnings;
  double get todayEarningsTotal => (finances?['today_earnings'] as num?)?.toDouble() ?? todayEarnings;
  double get weeklyEarnings => (finances?['weekly_earnings'] as num?)?.toDouble() ?? 0.0;
  List<Map<String, dynamic>> get trips => (finances?['trips'] as List<dynamic>?)?.cast<Map<String, dynamic>>() ?? [];

  String get linkedUpiId {
    final upi = (finances?['upi_id'] as String?) ?? (runnerProfile?['upi_id'] as String?);
    if (upi == null || upi.trim().isEmpty || upi.trim() == 'runner@upi' || upi.trim() == 'NOT_CONFIGURED') {
      return '';
    }
    return upi.trim();
  }

  int get profileCompletionPercentage {
    if (runnerProfile == null) return 20;
    int score = 40; // Initial registration
    if (runnerProfile!['vehicle_number'] != null && runnerProfile!['vehicle_number'].toString().isNotEmpty) score += 20;
    if (isApproved) score += 20;
    if (linkedUpiId.isNotEmpty) score += 20;
    return score.clamp(0, 100);
  }

  GBOrder? get activeMission {
    final runnerId = runnerProfile?['id'] as String? ?? currentUser?.id;
    const activeStatuses = ['RUNNER_ASSIGNED', 'PICKED_UP', 'OUT_FOR_DELIVERY'];
    try {
      return activeJobs.firstWhere((o) =>
          (o.runnerId == runnerId || (o.runnerId != null && o.runnerId!.isNotEmpty)) &&
          activeStatuses.contains(o.status));
    } catch (_) {
      try {
        return activeJobs.firstWhere((o) => activeStatuses.contains(o.status));
      } catch (_) {
        return null;
      }
    }
  }

  List<GBOrder> get availableJobs {
    const activeStatuses = ['RUNNER_ASSIGNED', 'PICKED_UP', 'OUT_FOR_DELIVERY'];
    return activeJobs.where((o) => !activeStatuses.contains(o.status) || o.runnerId == null || o.runnerId!.isEmpty).toList();
  }

  Future<void> init() async {
    try {
      await apiClient.probeAndSelectHost();
      final prefs = await SharedPreferences.getInstance();

      final savedLang = prefs.getString('gb_runner_locale');
      if (savedLang != null) {
        currentLocale = savedLang;
        hasSavedLocale = true;
      }

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
    hasSavedLocale = true;
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
    runnerProfile = null;
    isApproved = false;
    isOnline = false;
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
      // Strict rule: missing approval defaults to false!
      isApproved = (res.data!['is_approved'] as bool?) ?? false;
      isOnline = (res.data!['is_online'] as bool?) ?? false;
      todayEarnings = (res.data!['today_earnings'] as num?)?.toDouble() ?? 0.0;
      completedTrips = (res.data!['completed_trips'] as int?) ?? 0;
      notifyListeners();
    } else {
      isApproved = false;
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
    if (res.isSuccess && res.data != null) {
      activeJobs = res.data!;
    } else {
      activeJobs = [];
    }
    notifyListeners();
  }

  Future<void> fetchFinances() async {
    final res = await apiClient.getRunnerFinances();
    if (res.isSuccess && res.data != null) {
      finances = res.data!;
      todayEarnings = (res.data!['today_earnings'] as num?)?.toDouble() ??
          (res.data!['total_delivery_earnings'] as num?)?.toDouble() ??
          todayEarnings;
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

  Future<bool> updateRunnerProfile(Map<String, dynamic> runnerData) async {
    return await onboardRunner(runnerData);
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
                ? 'पारदर्शी 5-स्तरीय दूरी पेआउट और तत्काल बैंक/यूपीआई सेटलमेंट।'
                : 'Transparent 5-tier distance payouts and direct bank/UPI settlements.',
            timestamp: DateTime.now().subtract(const Duration(minutes: 20)),
            isRead: false,
            type: 'system',
          ),
          GBNotification(
            id: 'notif_run_safety',
            title: isHindi ? 'सड़क सुरक्षा एवं डिलीवरी दिशानिर्देश' : 'Road Safety & Delivery Guidelines',
            body: isHindi
                ? 'सुरक्षित गति बनाए रखें एवं सामान सौंपते समय ग्राहक से 4-अंकीय ओटीपी अवश्य सत्यापित करें।'
                : 'Maintain safe speeds and always verify the 4-digit PIN before completing delivery.',
            timestamp: DateTime.now().subtract(const Duration(hours: 3)),
            isRead: true,
            type: 'safety',
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
