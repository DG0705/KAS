import 'package:flutter/material.dart';
import 'app.dart';
import 'services/api_client.dart';
import 'services/attendance_service.dart';
import 'services/auth_service.dart';
import 'utils/app_config.dart';

void main() {
  final apiClient = ApiClient(baseUrl: AppConfig.apiBaseUrl);
  final authService = AuthService(apiClient: apiClient);
  apiClient.tokenProvider = () => authService.accessToken;

  runApp(
    AttendanceApp(
      authService: authService,
      attendanceService: AttendanceService(apiClient: apiClient),
    ),
  );
}
