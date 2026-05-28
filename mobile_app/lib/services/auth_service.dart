import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import '../models/auth_response.dart';
import '../models/employee.dart';
import 'api_client.dart';

class AuthService {
  AuthService({
    required ApiClient apiClient,
    FlutterSecureStorage? storage,
  })  : _apiClient = apiClient,
        _storage = storage ?? const FlutterSecureStorage();

  static const _accessTokenKey = 'access_token';
  static const _refreshTokenKey = 'refresh_token';

  final ApiClient _apiClient;
  final FlutterSecureStorage _storage;

  String? _accessToken;
  String? _refreshToken;
  Employee? _currentEmployee;

  String? get accessToken => _accessToken;
  Employee? get currentEmployee => _currentEmployee;
  bool get isAuthenticated => _accessToken != null && _currentEmployee != null;

  Future<bool> restoreSession() async {
    _accessToken = await _storage.read(key: _accessTokenKey);
    _refreshToken = await _storage.read(key: _refreshTokenKey);

    if (_accessToken == null) return false;

    try {
      final profile = await _apiClient.getJson('/auth/me/');
      _currentEmployee = Employee.fromJson(profile);
      return true;
    } catch (_) {
      await logout();
      return false;
    }
  }

  Future<Employee> login({
    required String email,
    required String password,
  }) async {
    final json = await _apiClient.postJson(
      '/auth/login/',
      {'email': email.trim(), 'password': password},
      authenticated: false,
    );
    final authResponse = AuthResponse.fromJson(json);

    _accessToken = authResponse.accessToken;
    _refreshToken = authResponse.refreshToken;
    _currentEmployee = authResponse.employee;

    await _storage.write(key: _accessTokenKey, value: _accessToken);
    await _storage.write(key: _refreshTokenKey, value: _refreshToken);

    return authResponse.employee;
  }

  Future<void> logout() async {
    _accessToken = null;
    _refreshToken = null;
    _currentEmployee = null;
    await _storage.delete(key: _accessTokenKey);
    await _storage.delete(key: _refreshTokenKey);
  }
}
