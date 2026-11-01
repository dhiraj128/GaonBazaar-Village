class Endpoints {
  static const String baseUrl = 'http://10.0.2.2:8000/api/v1'; // 10.0.2.2 for Android emulator / local dev
  static const String localIpUrl = 'http://127.0.0.1:8000/api/v1';

  // Auth
  static const String sendOtp = '/auth/otp/send';
  static const String verifyOtp = '/auth/otp/verify';
  static const String currentUser = '/auth/me';

  // Stores & Products
  static const String nearbyStores = '/stores/nearby';
  static String storeDetails(String id) => '/stores/$id';
  static String storeProducts(String id) => '/stores/$id/products';
  static const String globalCatalog = '/catalog/global';

  // Addresses
  static const String addresses = '/addresses';
  static const String checkServiceability = '/serviceability/check';

  // Cart & Orders
  static const String syncCart = '/cart/sync';
  static const String createOrder = '/orders';
  static const String customerOrders = '/orders';
  static String orderDetails(String id) => '/orders/$id';
  static String cancelOrder(String id) => '/orders/$id/cancel';

  // Vendor actions
  static const String vendorOrders = '/vendor/orders';
  static String vendorOrderAction(String id) => '/vendor/orders/$id/action';
  static const String vendorProducts = '/vendor/products';

  // Runner actions
  static const String runnerAvailableJobs = '/runner/jobs/available';
  static String runnerJobAction(String id) => '/runner/jobs/$id/action';

  // AI Assistant
  static const String aiQuery = '/ai/query';
}
