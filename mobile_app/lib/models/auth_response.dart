import 'employee.dart';

class AuthResponse {
  const AuthResponse({
    required this.accessToken,
    required this.refreshToken,
    required this.employee,
  });

  final String accessToken;
  final String refreshToken;
  final Employee employee;

  factory AuthResponse.fromJson(Map<String, dynamic> json) {
    return AuthResponse(
      accessToken: json['access'] as String,
      refreshToken: json['refresh'] as String,
      employee: Employee.fromJson(json['employee'] as Map<String, dynamic>),
    );
  }
}
