import 'package:flutter/material.dart';

import 'screens/splash_screen.dart';
import 'services/attendance_service.dart';
import 'services/auth_service.dart';

class AttendanceApp extends StatelessWidget {
  const AttendanceApp({
    super.key,
    required this.authService,
    required this.attendanceService,
  });

  final AuthService authService;
  final AttendanceService attendanceService;

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Employee Attendance',
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF1F6F5B),
          brightness: Brightness.light,
        ),
        scaffoldBackgroundColor: const Color(0xFFF5F7F4),
        appBarTheme: const AppBarTheme(
          centerTitle: false,
          elevation: 0,
          backgroundColor: Color(0xFFF5F7F4),
          foregroundColor: Color(0xFF17211D),
        ),
        inputDecorationTheme: InputDecorationTheme(
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(8),
          ),
          filled: true,
          fillColor: Colors.white,
        ),
        cardTheme: CardTheme(
          color: Colors.white,
          elevation: 0,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
            side: BorderSide(color: Colors.black.withOpacity(0.06)),
          ),
        ),
      ),
      home: SplashScreen(
        authService: authService,
        attendanceService: attendanceService,
      ),
    );
  }
}
