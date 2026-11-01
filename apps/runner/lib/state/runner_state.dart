import 'package:flutter/material.dart';
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

  double todayEarnings = 425.0;
  int completedTrips = 7;

  // Active delivery job
  Map<String, dynamic>? activeJob = {
    'id': 'ord_run_101',
    'store_name': 'माँ शारदा किराना स्टोर',
    'store_village': 'Chaturshi / Chatursi',
    'store_landmark': 'Near Gram Panchayat Bhavan',
    'customer_name': 'Ramesh Singh',
    'customer_phone': '9876543210',
    'customer_village': 'Chaturshi, Near Shiv Mandir',
    'items_summary': 'चक्की आटा x 2 kg, गाय का दूध x 1 L',
    'payout': 25.0,
    'status': 'ASSIGNED', // ASSIGNED, PICKED_UP, OUT_FOR_DELIVERY, DELIVERED
    'delivery_otp': '4821',
    'is_cod': true,
    'cod_amount': 132.0,
  };

  bool get isHindi => currentLocale == 'hi';

  void setLocale(String lang) {
    currentLocale = lang;
    notifyListeners();
  }

  void toggleOnline() {
    isOnline = !isOnline;
    notifyListeners();
  }

  void setAuth(GBUser user, String token) {
    currentUser = user;
    authToken = token;
    apiClient.setAuthToken(token);
    notifyListeners();
  }

  void updateJobStatus(String newStatus) {
    if (activeJob != null) {
      activeJob!['status'] = newStatus;
      if (newStatus == 'DELIVERED') {
        todayEarnings += (activeJob!['payout'] as num).toDouble();
        completedTrips += 1;
      }
      notifyListeners();
    }
  }

  void clearJob() {
    activeJob = null;
    notifyListeners();
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
