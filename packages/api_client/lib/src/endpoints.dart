class Endpoints {
  // Candidate base URLs for different environments:
  // 1. Physical Android phone via USB ADB reverse (adb reverse tcp:8000 tcp:8000)
  // 2. Physical Android phone via local Wi-Fi LAN
  // 3. Android Studio Emulator loopback
  static const String baseUrl = 'http://127.0.0.1:8000/api/v1';
  static const String emulatorBaseUrl = 'http://10.0.2.2:8000/api/v1';
  static const String wifiLanBaseUrl = 'http://192.168.31.187:8000/api/v1';

  static const List<String> candidateBaseUrls = [
    'http://127.0.0.1:8000/api/v1',
    'http://localhost:8000/api/v1',
    'http://192.168.31.187:8000/api/v1',
    'http://10.0.2.2:8000/api/v1',
  ];

  // Auth
  static const String sendOtp = '/auth/otp/send';
  static const String verifyOtp = '/auth/otp/verify';
  static const String currentUser = '/auth/me';
  static const String updateProfile = '/auth/me';

  // Stores & Products
  static const String nearbyStores = '/stores/nearby';
  static String storeDetails(String id) => '/stores/$id';
  static String storeProducts(String id) => '/stores/$id/products';
  static const String globalCatalog = '/catalog/global';

  // Addresses
  static const String addresses = '/addresses';
  static String addressDetails(String id) => '/addresses/$id';
  static const String checkServiceability = '/addresses/serviceability/check';

  // Cart & Orders
  static const String syncCart = '/cart/sync';
  static const String createOrder = '/orders';
  static const String customerOrders = '/orders';
  static String orderDetails(String id) => '/orders/$id';
  static String cancelOrder(String id) => '/orders/$id/cancel';

  // Support & Tickets
  static const String supportTickets = '/support/tickets';
  static const String supportAiChat = '/support/ai-chat';

  // Vendor actions
  static const String myStore = '/stores/me';
  static const String storeStatus = '/stores/status';
  static const String storeOnboard = '/stores/onboard';
  static const String vendorOrders = '/vendor/orders';
  static const String vendorFinances = '/vendor/finances';
  static String vendorOrderAction(String id) => '/vendor/orders/$id/action';
  static const String vendorProducts = '/vendor/products';
  static String productStock(String id) => '/stores/products/$id/stock';

  // Runner actions
  static const String runnerMe = '/runner/me';
  static const String runnerStatus = '/runner/status';
  static const String runnerOnboard = '/runner/onboard';
  static const String runnerJobs = '/runner/jobs';
  static const String runnerFinances = '/runner/finances';
  static String runnerJobAction(String id) => '/runner/jobs/$id/action';

  // AI Assistant
  static const String aiQuery = '/ai/query';
}
