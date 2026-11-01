import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_models/shared_models.dart';
import 'endpoints.dart';

class ApiResponse<T> {
  final bool isSuccess;
  final T? data;
  final String? errorMessage;
  final int statusCode;

  ApiResponse({
    required this.isSuccess,
    this.data,
    this.errorMessage,
    required this.statusCode,
  });
}

class GBApiClient {
  String baseUrl;
  String? _authToken;

  GBApiClient({String? customBaseUrl})
      : baseUrl = customBaseUrl ?? Endpoints.baseUrl;

  void setAuthToken(String token) {
    _authToken = token;
  }

  void clearAuthToken() {
    _authToken = null;
  }

  Map<String, String> _headers() {
    final headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };
    if (_authToken != null) {
      headers['Authorization'] = 'Bearer $_authToken';
    }
    return headers;
  }

  String _cleanErrorMessage(dynamic e) {
    final str = e.toString().toLowerCase();
    if (str.contains('socketexception') ||
        str.contains('operation not permitted') ||
        str.contains('connection refused') ||
        str.contains('timed out') ||
        str.contains('clientexception') ||
        str.contains('network is unreachable')) {
      return 'सर्वर से संपर्क नहीं हो पा रहा है। कृपया अपना इंटरनेट कनेक्शन जांचें (Unable to connect. Please check your internet connection)';
    }
    return 'अनपेक्षित त्रुटि हुई। कृपया दोबारा प्रयास करें (Something went wrong. Please try again)';
  }

  /// Automatically tests candidate hosts (ADB reverse localhost, Wi-Fi LAN, Emulator loopback)
  /// and selects the first active responsive backend host.
  Future<void> probeAndSelectHost() async {
    for (final candidate in Endpoints.candidateBaseUrls) {
      try {
        final healthUri = Uri.parse(candidate.replaceAll('/api/v1', '/health'));
        final response = await http.get(healthUri).timeout(const Duration(milliseconds: 1200));
        if (response.statusCode == 200) {
          baseUrl = candidate;
          return;
        }
      } catch (_) {
        // Try next candidate
      }
    }
  }

  // --- Auth APIs ---
  Future<ApiResponse<Map<String, dynamic>>> sendOtp({
    required String phone,
    String role = 'customer',
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl${Endpoints.sendOtp}'),
        headers: _headers(),
        body: jsonEncode({'phone': phone, 'role': role}),
      ).timeout(const Duration(seconds: 8));

      final data = jsonDecode(response.body) as Map<String, dynamic>;
      if (response.statusCode == 200) {
        return ApiResponse(isSuccess: true, data: data, statusCode: response.statusCode);
      }
      return ApiResponse(
        isSuccess: false,
        errorMessage: data['detail']?.toString() ?? 'Failed to send OTP',
        statusCode: response.statusCode,
      );
    } catch (e) {
      return ApiResponse(isSuccess: false, errorMessage: _cleanErrorMessage(e), statusCode: 500);
    }
  }

  Future<ApiResponse<Map<String, dynamic>>> verifyOtp({
    required String phone,
    required String otp,
    String? sessionId,
    String role = 'customer',
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl${Endpoints.verifyOtp}'),
        headers: _headers(),
        body: jsonEncode({
          'phone': phone,
          'otp': otp,
          'session_id': sessionId,
          'role': role,
        }),
      ).timeout(const Duration(seconds: 8));

      final data = jsonDecode(response.body) as Map<String, dynamic>;
      if (response.statusCode == 200) {
        if (data.containsKey('access_token')) {
          setAuthToken(data['access_token'] as String);
        }
        return ApiResponse(isSuccess: true, data: data, statusCode: response.statusCode);
      }
      return ApiResponse(
        isSuccess: false,
        errorMessage: data['detail']?.toString() ?? 'अमान्य ओटीपी कोड (Invalid OTP)',
        statusCode: response.statusCode,
      );
    } catch (e) {
      return ApiResponse(isSuccess: false, errorMessage: _cleanErrorMessage(e), statusCode: 500);
    }
  }

  Future<ApiResponse<GBUser>> getCurrentUser() async {
    try {
      final response = await http
          .get(Uri.parse('$baseUrl${Endpoints.currentUser}'), headers: _headers())
          .timeout(const Duration(seconds: 8));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        return ApiResponse(isSuccess: true, data: GBUser.fromJson(data), statusCode: 200);
      }
      return ApiResponse(isSuccess: false, errorMessage: 'User profile not found', statusCode: response.statusCode);
    } catch (e) {
      return ApiResponse(isSuccess: false, errorMessage: _cleanErrorMessage(e), statusCode: 500);
    }
  }

  Future<ApiResponse<GBUser>> updateProfile({
    String? name,
    String? email,
    String? preferredLanguage,
  }) async {
    try {
      final payload = <String, dynamic>{};
      if (name != null) payload['name'] = name;
      if (email != null) payload['email'] = email;
      if (preferredLanguage != null) payload['preferred_language'] = preferredLanguage;

      final response = await http.patch(
        Uri.parse('$baseUrl${Endpoints.updateProfile}'),
        headers: _headers(),
        body: jsonEncode(payload),
      ).timeout(const Duration(seconds: 8));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        return ApiResponse(isSuccess: true, data: GBUser.fromJson(data), statusCode: 200);
      }
      return ApiResponse(isSuccess: false, errorMessage: 'Failed to update profile', statusCode: response.statusCode);
    } catch (e) {
      return ApiResponse(isSuccess: false, errorMessage: _cleanErrorMessage(e), statusCode: 500);
    }
  }

  // --- Store & Catalog APIs ---
  Future<ApiResponse<List<GBStore>>> getNearbyStores({
    required double latitude,
    required double longitude,
    double radiusKm = 8.0,
    bool featuredOnly = false,
  }) async {
    try {
      var urlStr = '$baseUrl${Endpoints.nearbyStores}?latitude=$latitude&longitude=$longitude&radius_km=$radiusKm';
      if (featuredOnly) {
        urlStr += '&featured_only=true';
      }
      final response = await http.get(Uri.parse(urlStr), headers: _headers()).timeout(const Duration(seconds: 8));

      if (response.statusCode == 200) {
        final list = (jsonDecode(response.body) as List)
            .map((item) => GBStore.fromJson(item as Map<String, dynamic>))
            .toList();
        return ApiResponse(isSuccess: true, data: list, statusCode: response.statusCode);
      }
      return ApiResponse(isSuccess: false, errorMessage: 'Failed to fetch stores', statusCode: response.statusCode);
    } catch (e) {
      return ApiResponse(isSuccess: false, errorMessage: _cleanErrorMessage(e), statusCode: 500);
    }
  }

  Future<ApiResponse<List<GBProduct>>> getStoreProducts(String storeId) async {
    try {
      final response = await http
          .get(Uri.parse('$baseUrl${Endpoints.storeProducts(storeId)}'), headers: _headers())
          .timeout(const Duration(seconds: 8));

      if (response.statusCode == 200) {
        final list = (jsonDecode(response.body) as List)
            .map((item) => GBProduct.fromJson(item as Map<String, dynamic>))
            .toList();
        return ApiResponse(isSuccess: true, data: list, statusCode: response.statusCode);
      }
      return ApiResponse(isSuccess: false, errorMessage: 'Failed to fetch products', statusCode: response.statusCode);
    } catch (e) {
      return ApiResponse(isSuccess: false, errorMessage: _cleanErrorMessage(e), statusCode: 500);
    }
  }

  Future<ApiResponse<List<Map<String, dynamic>>>> getGlobalCatalog() async {
    try {
      final response = await http
          .get(Uri.parse('$baseUrl${Endpoints.globalCatalog}'), headers: _headers())
          .timeout(const Duration(seconds: 8));

      if (response.statusCode == 200) {
        final list = (jsonDecode(response.body) as List).cast<Map<String, dynamic>>();
        return ApiResponse(isSuccess: true, data: list, statusCode: response.statusCode);
      }
      return ApiResponse(isSuccess: false, errorMessage: 'Failed to fetch catalog', statusCode: response.statusCode);
    } catch (e) {
      return ApiResponse(isSuccess: false, errorMessage: _cleanErrorMessage(e), statusCode: 500);
    }
  }

  // --- Orders APIs ---
  Future<ApiResponse<GBOrder>> createOrder({
    required String storeId,
    required String deliveryAddressId,
    required String paymentMethod,
    required List<Map<String, dynamic>> items,
    String? customerNotes,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl${Endpoints.createOrder}'),
        headers: _headers(),
        body: jsonEncode({
          'store_id': storeId,
          'delivery_address_id': deliveryAddressId,
          'payment_method': paymentMethod,
          'items': items,
          'customer_notes': customerNotes,
        }),
      ).timeout(const Duration(seconds: 12));

      final data = jsonDecode(response.body) as Map<String, dynamic>;
      if (response.statusCode == 200 || response.statusCode == 201) {
        return ApiResponse(
          isSuccess: true,
          data: GBOrder.fromJson(data),
          statusCode: response.statusCode,
        );
      }
      return ApiResponse(
        isSuccess: false,
        errorMessage: data['detail']?.toString() ?? 'Order placement failed',
        statusCode: response.statusCode,
      );
    } catch (e) {
      return ApiResponse(isSuccess: false, errorMessage: _cleanErrorMessage(e), statusCode: 500);
    }
  }

  Future<ApiResponse<List<GBOrder>>> getCustomerOrders() async {
    try {
      final response = await http
          .get(Uri.parse('$baseUrl${Endpoints.customerOrders}'), headers: _headers())
          .timeout(const Duration(seconds: 8));

      if (response.statusCode == 200) {
        final list = (jsonDecode(response.body) as List)
            .map((item) => GBOrder.fromJson(item as Map<String, dynamic>))
            .toList();
        return ApiResponse(isSuccess: true, data: list, statusCode: response.statusCode);
      }
      return ApiResponse(isSuccess: false, errorMessage: 'Failed to fetch orders', statusCode: response.statusCode);
    } catch (e) {
      return ApiResponse(isSuccess: false, errorMessage: _cleanErrorMessage(e), statusCode: 500);
    }
  }

  Future<ApiResponse<GBOrder>> getOrderDetails(String orderId) async {
    try {
      final response = await http
          .get(Uri.parse('$baseUrl${Endpoints.orderDetails(orderId)}'), headers: _headers())
          .timeout(const Duration(seconds: 8));

      final data = jsonDecode(response.body) as Map<String, dynamic>;
      if (response.statusCode == 200) {
        return ApiResponse(
          isSuccess: true,
          data: GBOrder.fromJson(data),
          statusCode: response.statusCode,
        );
      }
      return ApiResponse(isSuccess: false, errorMessage: 'Order not found', statusCode: response.statusCode);
    } catch (e) {
      return ApiResponse(isSuccess: false, errorMessage: _cleanErrorMessage(e), statusCode: 500);
    }
  }

  Future<ApiResponse<Map<String, dynamic>>> cancelOrder(String orderId, String reason) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl${Endpoints.cancelOrder(orderId)}'),
        headers: _headers(),
        body: jsonEncode({'reason': reason}),
      ).timeout(const Duration(seconds: 8));

      final data = jsonDecode(response.body) as Map<String, dynamic>;
      if (response.statusCode == 200) {
        return ApiResponse(isSuccess: true, data: data, statusCode: response.statusCode);
      }
      return ApiResponse(
        isSuccess: false,
        errorMessage: data['detail']?.toString() ?? 'रद्दीकरण की समय सीमा समाप्त हो चुकी है (Cancellation expired)',
        statusCode: response.statusCode,
      );
    } catch (e) {
      return ApiResponse(isSuccess: false, errorMessage: _cleanErrorMessage(e), statusCode: 500);
    }
  }

  // --- Addresses APIs ---
  Future<ApiResponse<List<GBAddress>>> getSavedAddresses() async {
    try {
      final response = await http
          .get(Uri.parse('$baseUrl${Endpoints.addresses}'), headers: _headers())
          .timeout(const Duration(seconds: 8));

      if (response.statusCode == 200) {
        final list = (jsonDecode(response.body) as List)
            .map((item) => GBAddress.fromJson(item as Map<String, dynamic>))
            .toList();
        return ApiResponse(isSuccess: true, data: list, statusCode: response.statusCode);
      }
      return ApiResponse(isSuccess: false, errorMessage: 'Failed to fetch addresses', statusCode: response.statusCode);
    } catch (e) {
      return ApiResponse(isSuccess: false, errorMessage: _cleanErrorMessage(e), statusCode: 500);
    }
  }

  Future<ApiResponse<GBAddress>> createAddress(GBAddress address) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl${Endpoints.addresses}'),
        headers: _headers(),
        body: jsonEncode(address.toJson()),
      ).timeout(const Duration(seconds: 8));

      if (response.statusCode == 201 || response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        return ApiResponse(isSuccess: true, data: GBAddress.fromJson(data), statusCode: response.statusCode);
      }
      return ApiResponse(isSuccess: false, errorMessage: 'Failed to save address', statusCode: response.statusCode);
    } catch (e) {
      return ApiResponse(isSuccess: false, errorMessage: _cleanErrorMessage(e), statusCode: 500);
    }
  }

  Future<ApiResponse<bool>> deleteAddress(String addressId) async {
    try {
      final response = await http
          .delete(Uri.parse('$baseUrl${Endpoints.addressDetails(addressId)}'), headers: _headers())
          .timeout(const Duration(seconds: 8));

      if (response.statusCode == 204 || response.statusCode == 200) {
        return ApiResponse(isSuccess: true, data: true, statusCode: response.statusCode);
      }
      return ApiResponse(isSuccess: false, errorMessage: 'Failed to delete address', statusCode: response.statusCode);
    } catch (e) {
      return ApiResponse(isSuccess: false, errorMessage: _cleanErrorMessage(e), statusCode: 500);
    }
  }

  // --- AI Voice Assistant Query ---
  Future<ApiResponse<Map<String, dynamic>>> queryAI({
    required String query,
    String? storeId,
    String language = 'hi',
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl${Endpoints.aiQuery}'),
        headers: _headers(),
        body: jsonEncode({
          'query': query,
          'store_id': storeId,
          'language': language,
        }),
      ).timeout(const Duration(seconds: 8));

      final data = jsonDecode(response.body) as Map<String, dynamic>;
      if (response.statusCode == 200) {
        return ApiResponse(isSuccess: true, data: data, statusCode: response.statusCode);
      }
      return ApiResponse(isSuccess: false, errorMessage: 'AI parse failed', statusCode: response.statusCode);
    } catch (e) {
      return ApiResponse(isSuccess: false, errorMessage: _cleanErrorMessage(e), statusCode: 500);
    }
  }

  // --- Support Desk & AI Chat ---
  Future<ApiResponse<Map<String, dynamic>>> createSupportTicket({
    String? orderId,
    required String subject,
    required String message,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl${Endpoints.supportTickets}'),
        headers: _headers(),
        body: jsonEncode({
          'order_id': orderId,
          'subject': subject,
          'message': message,
        }),
      ).timeout(const Duration(seconds: 8));

      final data = jsonDecode(response.body) as Map<String, dynamic>;
      if (response.statusCode == 201 || response.statusCode == 200) {
        return ApiResponse(isSuccess: true, data: data, statusCode: response.statusCode);
      }
      return ApiResponse(isSuccess: false, errorMessage: 'Failed to submit ticket', statusCode: response.statusCode);
    } catch (e) {
      return ApiResponse(isSuccess: false, errorMessage: _cleanErrorMessage(e), statusCode: 500);
    }
  }

  Future<ApiResponse<List<Map<String, dynamic>>>> getCustomerTickets() async {
    try {
      final response = await http
          .get(Uri.parse('$baseUrl${Endpoints.supportTickets}'), headers: _headers())
          .timeout(const Duration(seconds: 8));

      if (response.statusCode == 200) {
        final list = (jsonDecode(response.body) as List).cast<Map<String, dynamic>>();
        return ApiResponse(isSuccess: true, data: list, statusCode: response.statusCode);
      }
      return ApiResponse(isSuccess: false, errorMessage: 'Failed to load tickets', statusCode: response.statusCode);
    } catch (e) {
      return ApiResponse(isSuccess: false, errorMessage: _cleanErrorMessage(e), statusCode: 500);
    }
  }

  Future<ApiResponse<Map<String, dynamic>>> querySupportAI({
    required String query,
    String language = 'hi',
    String? orderId,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl${Endpoints.supportAiChat}'),
        headers: _headers(),
        body: jsonEncode({
          'query': query,
          'language': language,
          'order_id': orderId,
        }),
      ).timeout(const Duration(seconds: 8));

      final data = jsonDecode(response.body) as Map<String, dynamic>;
      if (response.statusCode == 200) {
        return ApiResponse(isSuccess: true, data: data, statusCode: response.statusCode);
      }
      return ApiResponse(isSuccess: false, errorMessage: 'Support AI failed', statusCode: response.statusCode);
    } catch (e) {
      return ApiResponse(isSuccess: false, errorMessage: _cleanErrorMessage(e), statusCode: 500);
    }
  }
}
