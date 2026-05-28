import 'package:flutter/material.dart';

import '../services/attendance_service.dart';
import '../services/auth_service.dart';
import 'dashboard_screen.dart';
import 'login_screen.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({
    super.key,
    required this.authService,
    required this.attendanceService,
  });

  final AuthService authService;
  final AttendanceService attendanceService;

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  @override
  void initState() {
    super.initState();
    _restoreSession();
  }

  Future<void> _restoreSession() async {
    final isAuthenticated = await widget.authService.restoreSession();
    if (!mounted) return;

    Navigator.of(context).pushReplacement(
      MaterialPageRoute(
        builder: (_) => isAuthenticated
            ? DashboardScreen(
                authService: widget.authService,
                attendanceService: widget.attendanceService,
              )
            : LoginScreen(
                authService: widget.authService,
                attendanceService: widget.attendanceService,
              ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      body: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.fact_check_outlined, size: 58, color: Color(0xFF1F6F5B)),
            SizedBox(height: 18),
            Text(
              'Employee Attendance',
              style: TextStyle(fontSize: 22, fontWeight: FontWeight.w700),
            ),
            SizedBox(height: 20),
            CircularProgressIndicator(),
          ],
        ),
      ),
    );
  }
}
