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
    if (res.isSuccess && res.data != null) {
      activeJobs = res.data!;
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
  }) async {
    final res = await apiClient.runnerJobAction(orderId, action, deliveryOtp: deliveryOtp);
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
