import 'dart:convert';
import 'dart:io';
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
      ).timeout(const Duration(seconds: 10));

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
      return ApiResponse(isSuccess: false, errorMessage: e.toString(), statusCode: 500);
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
      ).timeout(const Duration(seconds: 10));

      final data = jsonDecode(response.body) as Map<String, dynamic>;
      if (response.statusCode == 200) {
        if (data.containsKey('access_token')) {
          setAuthToken(data['access_token'] as String);
        }
        return ApiResponse(isSuccess: true, data: data, statusCode: response.statusCode);
      }
      return ApiResponse(
        isSuccess: false,
        errorMessage: data['detail']?.toString() ?? 'Invalid OTP',
        statusCode: response.statusCode,
      );
    } catch (e) {
      return ApiResponse(isSuccess: false, errorMessage: e.toString(), statusCode: 500);
    }
  }

  // --- Store & Catalog APIs ---
  Future<ApiResponse<List<GBStore>>> getNearbyStores({
    required double latitude,
    required double longitude,
    double radiusKm = 8.0,
  }) async {
    try {
      final uri = Uri.parse(
        '$baseUrl${Endpoints.nearbyStores}?latitude=$latitude&longitude=$longitude&radius_km=$radiusKm',
      );
      final response = await http.get(uri, headers: _headers()).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        final list = (jsonDecode(response.body) as List)
            .map((item) => GBStore.fromJson(item as Map<String, dynamic>))
            .toList();
        return ApiResponse(isSuccess: true, data: list, statusCode: response.statusCode);
      }
      return ApiResponse(isSuccess: false, errorMessage: 'Failed to fetch stores', statusCode: response.statusCode);
    } catch (e) {
      return ApiResponse(isSuccess: false, errorMessage: e.toString(), statusCode: 500);
    }
  }

  Future<ApiResponse<List<GBProduct>>> getStoreProducts(String storeId) async {
    try {
      final response = await http
          .get(Uri.parse('$baseUrl${Endpoints.storeProducts(storeId)}'), headers: _headers())
          .timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        final list = (jsonDecode(response.body) as List)
            .map((item) => GBProduct.fromJson(item as Map<String, dynamic>))
            .toList();
        return ApiResponse(isSuccess: true, data: list, statusCode: response.statusCode);
      }
      return ApiResponse(isSuccess: false, errorMessage: 'Failed to fetch products', statusCode: response.statusCode);
    } catch (e) {
      return ApiResponse(isSuccess: false, errorMessage: e.toString(), statusCode: 500);
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
      return ApiResponse(isSuccess: false, errorMessage: e.toString(), statusCode: 500);
    }
  }

  Future<ApiResponse<GBOrder>> getOrderDetails(String orderId) async {
    try {
      final response = await http
          .get(Uri.parse('$baseUrl${Endpoints.orderDetails(orderId)}'), headers: _headers())
          .timeout(const Duration(seconds: 10));

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
      return ApiResponse(isSuccess: false, errorMessage: e.toString(), statusCode: 500);
    }
  }

  Future<ApiResponse<Map<String, dynamic>>> cancelOrder(String orderId, String reason) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl${Endpoints.cancelOrder(orderId)}'),
        headers: _headers(),
        body: jsonEncode({'reason': reason}),
      ).timeout(const Duration(seconds: 10));

      final data = jsonDecode(response.body) as Map<String, dynamic>;
      if (response.statusCode == 200) {
        return ApiResponse(isSuccess: true, data: data, statusCode: response.statusCode);
      }
      return ApiResponse(
        isSuccess: false,
        errorMessage: data['detail']?.toString() ?? 'Cancellation expired or failed',
        statusCode: response.statusCode,
      );
    } catch (e) {
      return ApiResponse(isSuccess: false, errorMessage: e.toString(), statusCode: 500);
    }
  }

  // --- AI Voice Assistant Query ---
  Future<ApiResponse<Map<String, dynamic>>> queryAI({
    required String query,
    String? storeId,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl${Endpoints.aiQuery}'),
        headers: _headers(),
        body: jsonEncode({
          'query': query,
          'store_id': storeId,
        }),
      ).timeout(const Duration(seconds: 8));

      final data = jsonDecode(response.body) as Map<String, dynamic>;
      if (response.statusCode == 200) {
        return ApiResponse(isSuccess: true, data: data, statusCode: response.statusCode);
      }
      return ApiResponse(isSuccess: false, errorMessage: 'AI parse failed', statusCode: response.statusCode);
    } catch (e) {
      return ApiResponse(isSuccess: false, errorMessage: e.toString(), statusCode: 500);
    }
  }
}
