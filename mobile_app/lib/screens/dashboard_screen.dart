import 'package:flutter/material.dart';
import '../models/attendance_record.dart';
import '../services/attendance_service.dart';
import '../services/auth_service.dart';
import '../utils/api_exception.dart';
import '../utils/date_formatters.dart';
import '../widgets/app_error_banner.dart';
import '../widgets/metric_tile.dart';
import '../widgets/primary_button.dart';
import 'attendance_history_screen.dart';
import 'login_screen.dart';
import 'punch_in_screen.dart';
import 'site_visit_screen.dart'; // 🚨 Imported the new screen

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({
    super.key,
    required this.authService,
    required this.attendanceService,
  });

  final AuthService authService;
  final AttendanceService attendanceService;

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  late Future<List<AttendanceRecord>> _historyFuture;
  bool _isPunchingOut = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _historyFuture = widget.attendanceService.history();
  }

  void _refresh() {
    setState(() {
      _historyFuture = widget.attendanceService.history();
      _error = null;
    });
  }

  AttendanceRecord? _activeRecord(List<AttendanceRecord> records) {
    for (final record in records) {
      if (record.isOpen) return record;
    }
    return null;
  }

  Future<void> _openPunchIn() async {
    final didPunchIn = await Navigator.of(context).push<bool>(
      MaterialPageRoute(
        builder: (_) => PunchInScreen(attendanceService: widget.attendanceService),
      ),
    );
    if (didPunchIn == true) _refresh();
  }

  Future<void> _punchOut() async {
    setState(() {
      _isPunchingOut = true;
      _error = null;
    });

    try {
      await widget.attendanceService.punchOut();
      _refresh();
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Punch out successful.')),
      );
    } on ApiException catch (error) {
      setState(() => _error = error.message);
    } catch (_) {
      setState(() => _error = 'Unable to punch out. Please try again.');
    } finally {
      if (mounted) setState(() => _isPunchingOut = false);
    }
  }

  Future<void> _logout() async {
    await widget.authService.logout();
    if (!mounted) return;
    Navigator.of(context).pushAndRemoveUntil(
      MaterialPageRoute(
        builder: (_) => LoginScreen(
          authService: widget.authService,
          attendanceService: widget.attendanceService,
        ),
      ),
      (_) => false,
    );
  }

  @override
  Widget build(BuildContext context) {
    final employee = widget.authService.currentEmployee;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Dashboard'),
        actions: [
          IconButton(
            tooltip: 'Refresh',
            onPressed: _refresh,
            icon: const Icon(Icons.refresh),
          ),
          IconButton(
            tooltip: 'Logout',
            onPressed: _logout,
            icon: const Icon(Icons.logout),
          ),
        ],
      ),
      body: FutureBuilder<List<AttendanceRecord>>(
        future: _historyFuture,
        builder: (context, snapshot) {
          final records = snapshot.data ?? const <AttendanceRecord>[];
          final activeRecord = _activeRecord(records);

          return RefreshIndicator(
            onRefresh: () async => _refresh(),
            child: ListView(
              padding: const EdgeInsets.all(18),
              children: [
                Text(
                  'Hello, ${employee?.name ?? 'Employee'}',
                  style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                        fontWeight: FontWeight.w800,
                      ),
                ),
                const SizedBox(height: 4),
                Text(
                  employee?.email ?? '',
                  style: Theme.of(context).textTheme.bodyMedium,
                ),
                const SizedBox(height: 18),
                if (_error != null) ...[
                  AppErrorBanner(message: _error!),
                  const SizedBox(height: 14),
                ],
                if (snapshot.hasError) ...[
                  AppErrorBanner(message: snapshot.error.toString()),
                  const SizedBox(height: 14),
                ],
                if (snapshot.connectionState == ConnectionState.waiting)
                  const LinearProgressIndicator(),
                const SizedBox(height: 10),
                _StatusPanel(activeRecord: activeRecord),
                const SizedBox(height: 16),
                Row(
                  children: [
                    Expanded(
                      child: MetricTile(
                        label: 'Records',
                        value: records.length.toString(),
                        icon: Icons.calendar_month_outlined,
                      ),
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: MetricTile(
                        label: 'Today',
                        value: records.isEmpty
                            ? '-'
                            : DateFormatters.time(records.first.punchIn),
                        icon: Icons.schedule_outlined,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 18),
                if (activeRecord == null)
                  PrimaryButton(
                    label: 'Punch In',
                    icon: Icons.login,
                    onPressed: _openPunchIn,
                  )
                else
                  PrimaryButton(
                    label: 'Punch Out',
                    icon: Icons.logout,
                    isLoading: _isPunchingOut,
                    onPressed: _punchOut,
                  ),
                const SizedBox(height: 12),
                OutlinedButton.icon(
                  onPressed: () {
                    Navigator.of(context).push(
                      MaterialPageRoute(
                        builder: (_) => AttendanceHistoryScreen(
                          attendanceService: widget.attendanceService,
                        ),
                      ),
                    );
                  },
                  icon: const Icon(Icons.history),
                  label: const Text('View Attendance History'),
                ),
                
                // 🚨 NEW: Client Site Visit Button - Visible only to Sales/Admin
                if (employee != null && (employee.isSalesperson || employee.isAdmin)) ...[
                  const SizedBox(height: 12),
                  OutlinedButton.icon(
                    onPressed: () {
                      Navigator.of(context).push(
                        MaterialPageRoute(
                          builder: (_) => SiteVisitScreen(
                            attendanceService: widget.attendanceService,
                          ),
                        ),
                      );
                    },
                    icon: const Icon(Icons.handshake_outlined),
                    label: const Text('Log Client Meeting'),
                    style: OutlinedButton.styleFrom(
                      foregroundColor: const Color(0xFF1F6F5B),
                      side: const BorderSide(color: Color(0xFF1F6F5B)),
                    ),
                  ),
                ],
              ],
            ),
          );
        },
      ),
    );
  }
}

class _StatusPanel extends StatelessWidget {
  const _StatusPanel({required this.activeRecord});

  final AttendanceRecord? activeRecord;

  @override
  Widget build(BuildContext context) {
    final isActive = activeRecord != null;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  isActive ? Icons.verified_outlined : Icons.pending_actions,
                  color: isActive ? const Color(0xFF1F6F5B) : const Color(0xFF8B6F20),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    isActive ? 'Currently punched in' : 'Ready for attendance',
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                          fontWeight: FontWeight.w800,
                        ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            Text(
              isActive
                  ? 'Punch in: ${DateFormatters.dateTime(activeRecord!.punchIn)}'
                  : 'Capture location and selfie before punching in.',
            ),
            if (isActive) ...[
              const SizedBox(height: 8),
              Text('Type: ${activeRecord!.attendanceType.label}'),
            ],
          ],
        ),
      ),
    );
  }
}