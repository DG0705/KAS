import 'package:flutter/material.dart';

import '../models/attendance_record.dart';
import '../services/attendance_service.dart';
import '../widgets/app_error_banner.dart';
import '../widgets/attendance_record_card.dart';

class AttendanceHistoryScreen extends StatefulWidget {
  const AttendanceHistoryScreen({
    super.key,
    required this.attendanceService,
  });

  final AttendanceService attendanceService;

  @override
  State<AttendanceHistoryScreen> createState() => _AttendanceHistoryScreenState();
}

class _AttendanceHistoryScreenState extends State<AttendanceHistoryScreen> {
  late Future<List<AttendanceRecord>> _historyFuture;

  @override
  void initState() {
    super.initState();
    _historyFuture = widget.attendanceService.history();
  }

  Future<void> _refresh() async {
    setState(() {
      _historyFuture = widget.attendanceService.history();
    });
    await _historyFuture;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Attendance History')),
      body: FutureBuilder<List<AttendanceRecord>>(
        future: _historyFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }

          if (snapshot.hasError) {
            return Padding(
              padding: const EdgeInsets.all(18),
              child: AppErrorBanner(message: snapshot.error.toString()),
            );
          }

          final records = snapshot.data ?? const <AttendanceRecord>[];
          if (records.isEmpty) {
            return RefreshIndicator(
              onRefresh: _refresh,
              child: ListView(
                padding: const EdgeInsets.all(24),
                children: const [
                  SizedBox(height: 120),
                  Icon(Icons.event_busy_outlined, size: 48),
                  SizedBox(height: 12),
                  Text(
                    'No attendance records yet.',
                    textAlign: TextAlign.center,
                  ),
                ],
              ),
            );
          }

          return RefreshIndicator(
            onRefresh: _refresh,
            child: ListView.separated(
              padding: const EdgeInsets.all(18),
              itemBuilder: (context, index) {
                return AttendanceRecordCard(record: records[index]);
              },
              separatorBuilder: (_, __) => const SizedBox(height: 10),
              itemCount: records.length,
            ),
          );
        },
      ),
    );
  }
}
