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
  String currentLanguage = "en";

  GBApiClient({String? customBaseUrl, String initialLanguage = "en"})
      : baseUrl = customBaseUrl ?? Endpoints.baseUrl,
        currentLanguage = initialLanguage;

  void setAuthToken(String token) {
    _authToken = token;
  }

  void clearAuthToken() {
    _authToken = null;
  }

  void setLanguage(String lang) {
    currentLanguage = lang.toLowerCase() == "hi" ? "hi" : "en";
  }

  Map<String, String> _headers() {
    final headers = {
      "Content-Type": "application/json",
      "Accept": "application/json",
      "Accept-Language": currentLanguage,
    };
    if (_authToken != null) {
      headers["Authorization"] = "Bearer $_authToken";
    }
    return headers;
  }

  String _cleanErrorMessage(dynamic e) {
    final str = e.toString().toLowerCase();
    final isEn = currentLanguage == "en";
    if (str.contains("timed out") || str.contains("timeout")) {
      return isEn
          ? "Server response timed out. Please retry."
          : "सर्वर से संपर्क में समय लग रहा है। कृपया कुछ सेकंड बाद पुनः प्रयास करें।";
    }
    if (str.contains("socketexception") ||
        str.contains("operation not permitted") ||
        str.contains("connection refused") ||
        str.contains("clientexception") ||
        str.contains("network is unreachable") ||
        str.contains("failed host lookup")) {
      return isEn
          ? "Unable to connect to server. Please check your internet connection."
          : "इंटरनेट कनेक्शन नहीं मिल पा रहा है। कृपया नेटवर्क जांचें।";
    }
    return isEn
        ? "Something went wrong. Please try again."
        : "अनपेक्षित त्रुटि हुई। कृपया दोबारा प्रयास करें।";
  }

  String _sanitizeErrorMessage(int statusCode, dynamic detail) {
    final isEn = currentLanguage == "en";
    if (detail is String && detail.trim().isNotEmpty) {
      final text = detail.trim();
      final low = text.toLowerCase();
      if (low.contains("traceback") ||
          low.contains("sqlalchemy") ||
          low.contains("psycopg") ||
          low.contains("foreignkey") ||
          low.contains("integrityerror") ||
          low.contains("syntaxerror") ||
          low.contains("operationalerror") ||
          low.contains("internal server error") ||
          low.contains("stack trace")) {
        return isEn
            ? "Service temporarily busy. Please retry shortly."
            : "सेवा वर्तमान में व्यस्त है। कृपया कुछ क्षण बाद पुनः प्रयास करें।";
      }
      if (text.contains("(") && text.endsWith(")")) {
        final startIdx = text.lastIndexOf("(");
        final enPart = text.substring(startIdx + 1, text.length - 1).trim();
        final hiPart = text.substring(0, startIdx).trim();
        if (isEn && enPart.isNotEmpty) {
          return enPart;
        } else if (!isEn && hiPart.isNotEmpty) {
          return hiPart;
        }
      }
      return text;
    }
    if (detail is List && detail.isNotEmpty) {
      final first = detail.first;
      if (first is Map && first.containsKey("msg")) {
        return "${first['msg']}";
      }
      return isEn ? "Please check the entered details." : "कृपया दर्ज की गई जानकारी की जांच करें।";
    }
    switch (statusCode) {
      case 400:
        return isEn ? "Invalid request. Please verify details and retry." : "अमान्य अनुरोध। कृपया पुनः प्रयास करें।";
      case 401:
        return isEn ? "Session expired. Please sign in again." : "सत्र समाप्त हो गया है। कृपया पुनः लॉगिन करें।";
      case 403:
        return isEn ? "You do not have permission for this action." : "इस कार्रवाई की अनुमति नहीं है।";
      case 404:
        return isEn ? "Requested information not found." : "अनुरोधित जानकारी उपलब्ध नहीं है।";
      case 409:
        return isEn ? "Status updated. Please refresh." : "ऑर्डर स्थिति बदल चुकी है। कृपया स्क्रीन ताज़ा करें।";
      case 422:
        return isEn ? "Please verify the entered details." : "कृपया दर्ज की गई जानकारी जांचें।";
      case 429:
        return isEn ? "Too many requests. Please wait before retrying." : "कृपया पुनः प्रयास करने से पहले प्रतीक्षा करें।";
      case 500:
      case 502:
      case 503:
      case 504:
        return isEn ? "Service temporarily busy. Please retry shortly." : "सर्वर सेवा वर्तमान में व्यस्त है। कृपया कुछ देर बाद प्रयास करें।";
      default:
        return isEn ? "Unable to complete request. Please try again." : "अनपेक्षित समस्या हुई। कृपया दोबारा प्रयास करें।";
    }
  }

  String _extractErrorMessage(http.Response response) {
    try {
      final decoded = jsonDecode(response.body);
      if (decoded is Map<String, dynamic> && decoded.containsKey('detail')) {
        return _sanitizeErrorMessage(response.statusCode, decoded['detail']);
      }
    } catch (_) {}
    return _sanitizeErrorMessage(response.statusCode, null);
  }

  /// Automatically verifies backend host connectivity.
  /// If the configured baseUrl is HTTPS (e.g. Render Staging), it validates that endpoint
  /// with cold-start allowance. Otherwise, it probes local candidates.
  Future<void> probeAndSelectHost() async {
    if (baseUrl.startsWith('https://')) {
      try {
        final healthUri = Uri.parse(baseUrl.replaceAll('/api/v1', '/health'));
        final response = await http.get(healthUri).timeout(const Duration(seconds: 10));
        if (response.statusCode == 200) {
          return;
        }
      } catch (_) {
        // Cold-start or transient network glitch; baseUrl remains unchanged
      }
    }

    for (final candidate in Endpoints.candidateBaseUrls) {
      try {
        final healthUri = Uri.parse(candidate.replaceAll('/api/v1', '/health'));
        final response = await http.get(healthUri).timeout(const Duration(milliseconds: 1500));
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
        errorMessage: _extractErrorMessage(response),
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
        errorMessage: _extractErrorMessage(response),
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
      return ApiResponse(isSuccess: false, errorMessage: _extractErrorMessage(response), statusCode: response.statusCode);
    } catch (e) {
      return ApiResponse(isSuccess: false, errorMessage: _cleanErrorMessage(e), statusCode: 500);
    }
  }

  Future<ApiResponse<GBUser>> updateProfile({
    String? name,
    String? email,
    String? preferredLanguage,
    String? avatarUrl,
    String? primaryVillage,
    String? primaryPanchayat,
  }) async {
    try {
      final payload = <String, dynamic>{};
      if (name != null) payload['name'] = name;
      if (email != null) payload['email'] = email;
      if (preferredLanguage != null) payload['preferred_language'] = preferredLanguage;
      if (avatarUrl != null) payload['avatar_url'] = avatarUrl;
      if (primaryVillage != null) payload['primary_village'] = primaryVillage;
      if (primaryPanchayat != null) payload['primary_panchayat'] = primaryPanchayat;

      final response = await http.patch(
        Uri.parse('$baseUrl${Endpoints.updateProfile}'),
        headers: _headers(),
        body: jsonEncode(payload),
      ).timeout(const Duration(seconds: 8));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        return ApiResponse(isSuccess: true, data: GBUser.fromJson(data), statusCode: 200);
      }
      return ApiResponse(isSuccess: false, errorMessage: _extractErrorMessage(response), statusCode: response.statusCode);
    } catch (e) {
      return ApiResponse(isSuccess: false, errorMessage: _cleanErrorMessage(e), statusCode: 500);
    }
  }

  Future<ApiResponse<GBUser>> uploadAvatar(String avatarData) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl${Endpoints.uploadAvatar}'),
        headers: _headers(),
        body: jsonEncode({'avatar_data': avatarData}),
      ).timeout(const Duration(seconds: 12));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        return ApiResponse(isSuccess: true, data: GBUser.fromJson(data), statusCode: 200);
      }
      return ApiResponse(isSuccess: false, errorMessage: _extractErrorMessage(response), statusCode: response.statusCode);
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
      return ApiResponse(isSuccess: false, errorMessage: _extractErrorMessage(response), statusCode: response.statusCode);
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
      return ApiResponse(isSuccess: false, errorMessage: _extractErrorMessage(response), statusCode: response.statusCode);
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
      return ApiResponse(isSuccess: false, errorMessage: _extractErrorMessage(response), statusCode: response.statusCode);
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
        errorMessage: _extractErrorMessage(response),
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
      return ApiResponse(isSuccess: false, errorMessage: _extractErrorMessage(response), statusCode: response.statusCode);
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
      return ApiResponse(isSuccess: false, errorMessage: _extractErrorMessage(response), statusCode: response.statusCode);
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
        errorMessage: _extractErrorMessage(response),
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
      return ApiResponse(isSuccess: false, errorMessage: _extractErrorMessage(response), statusCode: response.statusCode);
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
      return ApiResponse(isSuccess: false, errorMessage: _extractErrorMessage(response), statusCode: response.statusCode);
    } catch (e) {
      return ApiResponse(isSuccess: false, errorMessage: _cleanErrorMessage(e), statusCode: 500);
    }
  }

    Future<ApiResponse<List<Map<String, dynamic>>>> getPilotLocalities() async {
    try {
      final response = await http
          .get(Uri.parse('$baseUrl${Endpoints.pilotLocalities}'), headers: _headers())
          .timeout(const Duration(seconds: 8));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        final list = (data['localities'] as List? ?? []).cast<Map<String, dynamic>>();
        return ApiResponse(isSuccess: true, data: list, statusCode: response.statusCode);
      }
      return ApiResponse(isSuccess: false, errorMessage: _extractErrorMessage(response), statusCode: response.statusCode);
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
      return ApiResponse(isSuccess: false, errorMessage: _extractErrorMessage(response), statusCode: response.statusCode);
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
      return ApiResponse(isSuccess: false, errorMessage: _extractErrorMessage(response), statusCode: response.statusCode);
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
      return ApiResponse(isSuccess: false, errorMessage: _extractErrorMessage(response), statusCode: response.statusCode);
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
      return ApiResponse(isSuccess: false, errorMessage: _extractErrorMessage(response), statusCode: response.statusCode);
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
      return ApiResponse(isSuccess: false, errorMessage: _extractErrorMessage(response), statusCode: response.statusCode);
    } catch (e) {
      return ApiResponse(isSuccess: false, errorMessage: _cleanErrorMessage(e), statusCode: 500);
    }
  }

  // --- Vendor APIs ---
  Future<ApiResponse<GBStore>> getMyStore() async {
    try {
      final response = await http
          .get(Uri.parse('$baseUrl${Endpoints.myStore}'), headers: _headers())
          .timeout(const Duration(seconds: 8));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        return ApiResponse(isSuccess: true, data: GBStore.fromJson(data), statusCode: response.statusCode);
      }
      return ApiResponse(isSuccess: false, errorMessage: _extractErrorMessage(response), statusCode: response.statusCode);
    } catch (e) {
      return ApiResponse(isSuccess: false, errorMessage: _cleanErrorMessage(e), statusCode: 500);
    }
  }

  Future<ApiResponse<Map<String, dynamic>>> updateStoreStatus(bool isOnline) async {
    try {
      final response = await http
          .patch(
            Uri.parse('$baseUrl${Endpoints.storeStatus}'),
            headers: _headers(),
            body: jsonEncode({'is_online': isOnline}),
          )
          .timeout(const Duration(seconds: 8));

      final data = jsonDecode(response.body) as Map<String, dynamic>;
      if (response.statusCode == 200) {
        return ApiResponse(isSuccess: true, data: data, statusCode: response.statusCode);
      }
      return ApiResponse(isSuccess: false, errorMessage: _extractErrorMessage(response), statusCode: response.statusCode);
    } catch (e) {
      return ApiResponse(isSuccess: false, errorMessage: _cleanErrorMessage(e), statusCode: 500);
    }
  }

  Future<ApiResponse<GBStore>> onboardStore(Map<String, dynamic> storeData) async {
    try {
      final response = await http
          .post(
            Uri.parse('$baseUrl${Endpoints.storeOnboard}'),
            headers: _headers(),
            body: jsonEncode(storeData),
          )
          .timeout(const Duration(seconds: 8));

      if (response.statusCode == 200 || response.statusCode == 201) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        return ApiResponse(isSuccess: true, data: GBStore.fromJson(data), statusCode: response.statusCode);
      }
      return ApiResponse(isSuccess: false, errorMessage: _extractErrorMessage(response), statusCode: response.statusCode);
    } catch (e) {
      return ApiResponse(isSuccess: false, errorMessage: _cleanErrorMessage(e), statusCode: 500);
    }
  }

  Future<ApiResponse<List<GBOrder>>> getVendorOrders() async {
    try {
      final response = await http
          .get(Uri.parse('$baseUrl${Endpoints.vendorOrders}'), headers: _headers())
          .timeout(const Duration(seconds: 8));

      if (response.statusCode == 200) {
        final list = (jsonDecode(response.body) as List)
            .map((item) => GBOrder.fromJson(item as Map<String, dynamic>))
            .toList();
        return ApiResponse(isSuccess: true, data: list, statusCode: response.statusCode);
      }
      return ApiResponse(isSuccess: false, errorMessage: _extractErrorMessage(response), statusCode: response.statusCode);
    } catch (e) {
      return ApiResponse(isSuccess: false, errorMessage: _cleanErrorMessage(e), statusCode: 500);
    }
  }

  Future<ApiResponse<Map<String, dynamic>>> getVendorFinances() async {
    try {
      final response = await http
          .get(Uri.parse('$baseUrl${Endpoints.vendorFinances}'), headers: _headers())
          .timeout(const Duration(seconds: 8));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        return ApiResponse(isSuccess: true, data: data, statusCode: response.statusCode);
      }
      return ApiResponse(isSuccess: false, errorMessage: _extractErrorMessage(response), statusCode: response.statusCode);
    } catch (e) {
      return ApiResponse(isSuccess: false, errorMessage: _cleanErrorMessage(e), statusCode: 500);
    }
  }

  Future<ApiResponse<Map<String, dynamic>>> vendorOrderAction(String orderId, String action) async {
    try {
      final response = await http
          .post(
            Uri.parse('$baseUrl${Endpoints.vendorOrderAction(orderId)}'),
            headers: _headers(),
            body: jsonEncode({'action': action}),
          )
          .timeout(const Duration(seconds: 8));

      final data = jsonDecode(response.body) as Map<String, dynamic>;
      if (response.statusCode == 200) {
        return ApiResponse(isSuccess: true, data: data, statusCode: response.statusCode);
      }
      return ApiResponse(isSuccess: false, errorMessage: _extractErrorMessage(response), statusCode: response.statusCode);
    } catch (e) {
      return ApiResponse(isSuccess: false, errorMessage: _cleanErrorMessage(e), statusCode: 500);
    }
  }

  Future<ApiResponse<GBProduct>> addVendorProduct(Map<String, dynamic> productData) async {
    try {
      final response = await http
          .post(
            Uri.parse('$baseUrl${Endpoints.vendorProducts}'),
            headers: _headers(),
            body: jsonEncode(productData),
          )
          .timeout(const Duration(seconds: 8));

      if (response.statusCode == 200 || response.statusCode == 201) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        return ApiResponse(isSuccess: true, data: GBProduct.fromJson(data), statusCode: response.statusCode);
      }
      return ApiResponse(isSuccess: false, errorMessage: _extractErrorMessage(response), statusCode: response.statusCode);
    } catch (e) {
      return ApiResponse(isSuccess: false, errorMessage: _cleanErrorMessage(e), statusCode: 500);
    }
  }

  Future<ApiResponse<Map<String, dynamic>>> updateProductStock(
    String productId, {
    bool? inStock,
    int? stockQuantity,
    double? price,
  }) async {
    try {
      final body = <String, dynamic>{};
      if (inStock != null) body['in_stock'] = inStock;
      if (stockQuantity != null) body['stock_quantity'] = stockQuantity;
      if (price != null) body['price'] = price;

      final response = await http
          .patch(
            Uri.parse('$baseUrl${Endpoints.productStock(productId)}'),
            headers: _headers(),
            body: jsonEncode(body),
          )
          .timeout(const Duration(seconds: 8));

      final data = jsonDecode(response.body) as Map<String, dynamic>;
      if (response.statusCode == 200) {
        return ApiResponse(isSuccess: true, data: data, statusCode: response.statusCode);
      }
      return ApiResponse(isSuccess: false, errorMessage: _extractErrorMessage(response), statusCode: response.statusCode);
    } catch (e) {
      return ApiResponse(isSuccess: false, errorMessage: _cleanErrorMessage(e), statusCode: 500);
    }
  }

  // --- Runner APIs ---
  Future<ApiResponse<Map<String, dynamic>>> onboardRunner(Map<String, dynamic> runnerData) async {
    try {
      final response = await http
          .post(
            Uri.parse('$baseUrl${Endpoints.runnerOnboard}'),
            headers: _headers(),
            body: jsonEncode(runnerData),
          )
          .timeout(const Duration(seconds: 8));

      final data = jsonDecode(response.body) as Map<String, dynamic>;
      if (response.statusCode == 200 || response.statusCode == 201) {
        return ApiResponse(isSuccess: true, data: data, statusCode: response.statusCode);
      }
      return ApiResponse(isSuccess: false, errorMessage: _extractErrorMessage(response), statusCode: response.statusCode);
    } catch (e) {
      return ApiResponse(isSuccess: false, errorMessage: _cleanErrorMessage(e), statusCode: 500);
    }
  }

  Future<ApiResponse<Map<String, dynamic>>> getRunnerMe() async {
    try {
      final response = await http
          .get(Uri.parse('$baseUrl${Endpoints.runnerMe}'), headers: _headers())
          .timeout(const Duration(seconds: 8));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        return ApiResponse(isSuccess: true, data: data, statusCode: response.statusCode);
      }
      return ApiResponse(isSuccess: false, errorMessage: _extractErrorMessage(response), statusCode: response.statusCode);
    } catch (e) {
      return ApiResponse(isSuccess: false, errorMessage: _cleanErrorMessage(e), statusCode: 500);
    }
  }

  Future<ApiResponse<Map<String, dynamic>>> updateRunnerStatus(bool isOnline) async {
    try {
      final response = await http
          .patch(
            Uri.parse('$baseUrl${Endpoints.runnerStatus}'),
            headers: _headers(),
            body: jsonEncode({'is_online': isOnline}),
          )
          .timeout(const Duration(seconds: 8));

      final data = jsonDecode(response.body) as Map<String, dynamic>;
      if (response.statusCode == 200) {
        return ApiResponse(isSuccess: true, data: data, statusCode: response.statusCode);
      }
      return ApiResponse(isSuccess: false, errorMessage: _extractErrorMessage(response), statusCode: response.statusCode);
    } catch (e) {
      return ApiResponse(isSuccess: false, errorMessage: _cleanErrorMessage(e), statusCode: 500);
    }
  }

  Future<ApiResponse<List<GBOrder>>> getRunnerJobs() async {
    try {
      final response = await http
          .get(Uri.parse('$baseUrl${Endpoints.runnerJobs}'), headers: _headers())
          .timeout(const Duration(seconds: 8));

      if (response.statusCode == 200) {
        final list = (jsonDecode(response.body) as List)
            .map((item) => GBOrder.fromJson(item as Map<String, dynamic>))
            .toList();
        return ApiResponse(isSuccess: true, data: list, statusCode: response.statusCode);
      }
      return ApiResponse(isSuccess: false, errorMessage: _extractErrorMessage(response), statusCode: response.statusCode);
    } catch (e) {
      return ApiResponse(isSuccess: false, errorMessage: _cleanErrorMessage(e), statusCode: 500);
    }
  }

  Future<ApiResponse<Map<String, dynamic>>> getRunnerFinances() async {
    try {
      final response = await http
          .get(Uri.parse('$baseUrl${Endpoints.runnerFinances}'), headers: _headers())
          .timeout(const Duration(seconds: 8));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        return ApiResponse(isSuccess: true, data: data, statusCode: response.statusCode);
      }
      return ApiResponse(isSuccess: false, errorMessage: _extractErrorMessage(response), statusCode: response.statusCode);
    } catch (e) {
      return ApiResponse(isSuccess: false, errorMessage: _cleanErrorMessage(e), statusCode: 500);
    }
  }

  Future<ApiResponse<Map<String, dynamic>>> runnerJobAction(
    String orderId,
    String action, {
    String? deliveryOtp,
    bool? cashCollected,
  }) async {
    try {
      final body = <String, dynamic>{'action': action};
      if (deliveryOtp != null) body['delivery_otp'] = deliveryOtp;
      if (cashCollected != null) body['cash_collected'] = cashCollected;

      final response = await http
          .post(
            Uri.parse('$baseUrl${Endpoints.runnerJobAction(orderId)}'),
            headers: _headers(),
            body: jsonEncode(body),
          )
          .timeout(const Duration(seconds: 8));

      final data = jsonDecode(response.body) as Map<String, dynamic>;
      if (response.statusCode == 200) {
        return ApiResponse(isSuccess: true, data: data, statusCode: response.statusCode);
      }
      return ApiResponse(isSuccess: false, errorMessage: _extractErrorMessage(response), statusCode: response.statusCode);
    } catch (e) {
      return ApiResponse(isSuccess: false, errorMessage: _cleanErrorMessage(e), statusCode: 500);
    }
  }


  // --- Razorpay Payment Gateway ---
  Future<ApiResponse<Map<String, dynamic>>> createRazorpayOrder(String orderId) async {
    try {
      final response = await http
          .post(
            Uri.parse('$baseUrl${Endpoints.razorpayOrder}'),
            headers: _headers(),
            body: jsonEncode({'order_id': orderId}),
          )
          .timeout(const Duration(seconds: 8));

      final data = jsonDecode(response.body) as Map<String, dynamic>;
      if (response.statusCode == 200) {
        return ApiResponse(isSuccess: true, data: data, statusCode: response.statusCode);
      }
      return ApiResponse(isSuccess: false, errorMessage: _extractErrorMessage(response), statusCode: response.statusCode);
    } catch (e) {
      return ApiResponse(isSuccess: false, errorMessage: _cleanErrorMessage(e), statusCode: 500);
    }
  }

  Future<ApiResponse<Map<String, dynamic>>> verifyRazorpayPayment({
    required String orderId,
    required String razorpayOrderId,
    required String razorpayPaymentId,
    required String razorpaySignature,
  }) async {
    try {
      final response = await http
          .post(
            Uri.parse('$baseUrl${Endpoints.razorpayVerify}'),
            headers: _headers(),
            body: jsonEncode({
              'order_id': orderId,
              'razorpay_order_id': razorpayOrderId,
              'razorpay_payment_id': razorpayPaymentId,
              'razorpay_signature': razorpaySignature,
            }),
          )
          .timeout(const Duration(seconds: 8));

      final data = jsonDecode(response.body) as Map<String, dynamic>;
      if (response.statusCode == 200) {
        return ApiResponse(isSuccess: true, data: data, statusCode: response.statusCode);
      }
      return ApiResponse(isSuccess: false, errorMessage: _extractErrorMessage(response), statusCode: response.statusCode);
    } catch (e) {
      return ApiResponse(isSuccess: false, errorMessage: _cleanErrorMessage(e), statusCode: 500);
    }
  }

  // --- Payment Gateway Status ---
  Future<ApiResponse<Map<String, dynamic>>> getPaymentStatus() async {
    try {
      final response = await http
          .get(Uri.parse('$baseUrl${Endpoints.paymentStatus}'), headers: _headers())
          .timeout(const Duration(seconds: 8));

      final data = jsonDecode(response.body) as Map<String, dynamic>;
      if (response.statusCode == 200) {
        return ApiResponse(isSuccess: true, data: data, statusCode: 200);
      }
      return ApiResponse(isSuccess: false, errorMessage: _extractErrorMessage(response), statusCode: response.statusCode);
    } catch (e) {
      return ApiResponse(isSuccess: false, errorMessage: _cleanErrorMessage(e), statusCode: 500);
    }
  }

  // --- Order-Scoped Chat & Live Location Messages ---
  Future<ApiResponse<List<GBOrderMessage>>> getOrderMessages(String orderId) async {
    try {
      final response = await http
          .get(Uri.parse('$baseUrl${Endpoints.orderMessages(orderId)}'), headers: _headers())
          .timeout(const Duration(seconds: 8));

      if (response.statusCode == 200) {
        final list = (jsonDecode(response.body) as List)
            .map((item) => GBOrderMessage.fromJson(item as Map<String, dynamic>))
            .toList();
        return ApiResponse(isSuccess: true, data: list, statusCode: 200);
      }
      return ApiResponse(isSuccess: false, errorMessage: _extractErrorMessage(response), statusCode: response.statusCode);
    } catch (e) {
      return ApiResponse(isSuccess: false, errorMessage: _cleanErrorMessage(e), statusCode: 500);
    }
  }

  Future<ApiResponse<GBOrderMessage>> sendOrderMessage(
    String orderId, {
    required String messageType,
    String? content,
    double? latitude,
    double? longitude,
    String? locationTitle,
  }) async {
    try {
      final body = <String, dynamic>{
        'message_type': messageType,
        'content': content,
        'latitude': latitude,
        'longitude': longitude,
        'location_title': locationTitle,
      };

      final response = await http
          .post(
            Uri.parse('$baseUrl${Endpoints.orderMessages(orderId)}'),
            headers: _headers(),
            body: jsonEncode(body),
          )
          .timeout(const Duration(seconds: 8));

      final data = jsonDecode(response.body) as Map<String, dynamic>;
      if (response.statusCode == 200 || response.statusCode == 201) {
        return ApiResponse(isSuccess: true, data: GBOrderMessage.fromJson(data), statusCode: response.statusCode);
      }
      return ApiResponse(isSuccess: false, errorMessage: _extractErrorMessage(response), statusCode: response.statusCode);
    } catch (e) {
      return ApiResponse(isSuccess: false, errorMessage: _cleanErrorMessage(e), statusCode: 500);
    }
  }


  Future<ApiResponse<List<GBNotification>>> getNotifications() async {
    try {
      final response = await http
          .get(
            Uri.parse('$baseUrl${Endpoints.notifications}'),
            headers: _headers(),
          )
          .timeout(const Duration(seconds: 8));

      if (response.statusCode == 200) {
        final list = jsonDecode(response.body) as List<dynamic>;
        final notifs = list.map((item) => GBNotification.fromJson(item as Map<String, dynamic>)).toList();
        return ApiResponse(isSuccess: true, data: notifs, statusCode: 200);
      }
      return ApiResponse(isSuccess: false, errorMessage: _extractErrorMessage(response), statusCode: response.statusCode);
    } catch (e) {
      return ApiResponse(isSuccess: false, errorMessage: _cleanErrorMessage(e), statusCode: 500);
    }
  }

  Future<ApiResponse<bool>> markAllNotificationsRead() async {
    try {
      final response = await http
          .post(
            Uri.parse('$baseUrl${Endpoints.notificationsMarkAllRead}'),
            headers: _headers(),
          )
          .timeout(const Duration(seconds: 8));

      if (response.statusCode == 200) {
        return ApiResponse(isSuccess: true, data: true, statusCode: 200);
      }
      return ApiResponse(isSuccess: false, errorMessage: _extractErrorMessage(response), statusCode: response.statusCode);
    } catch (e) {
      return ApiResponse(isSuccess: false, errorMessage: _cleanErrorMessage(e), statusCode: 500);
    }
  }

}
