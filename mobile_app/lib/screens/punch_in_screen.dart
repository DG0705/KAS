import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart'; // 🚨 Added for location logging
import '../models/attendance_record.dart';
import '../services/attendance_service.dart';
import '../utils/api_exception.dart';
import '../widgets/app_error_banner.dart';
import '../widgets/primary_button.dart';

class PunchInScreen extends StatefulWidget {
  const PunchInScreen({
    super.key,
    required this.attendanceService,
  });

  final AttendanceService attendanceService;

  @override
  State<PunchInScreen> createState() => _PunchInScreenState();
}

class _PunchInScreenState extends State<PunchInScreen> {
  AttendanceType _attendanceType = AttendanceType.office;
  bool _isSubmitting = false;
  String? _error;

  /// Helper to request location permissions and fetch current GPS coordinates
  Future<Position?> _getCurrentLocation() async {
    bool serviceEnabled;
    LocationPermission permission;

    serviceEnabled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) {
      setState(() => _error = 'Location services are disabled. Please enable GPS.');
      return null;
    }

    permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.denied) {
        setState(() => _error = 'Location permissions are denied.');
        return null;
      }
    }
    
    if (permission == LocationPermission.deniedForever) {
      setState(() => _error = 'Location permissions are permanently denied. Check app settings.');
      return null;
    }

    return await Geolocator.getCurrentPosition();
  }

  Future<void> _submit() async {
    setState(() => _error = null);
    setState(() => _isSubmitting = true);

    double? lat;
    double? lon;

    try {
      // 🚨 Fetch coordinates ONLY if the user is punching into a Site
      if (_attendanceType == AttendanceType.site) {
        final position = await _getCurrentLocation();
        if (position == null) {
          setState(() => _isSubmitting = false);
          return; // Stop if permission or GPS is unavailable
        }
        lat = position.latitude;
        lon = position.longitude;
      }

      // 🚨 Fire the clean JSON request matching our new attendance service
      await widget.attendanceService.punchIn(
        attendanceType: _attendanceType,
        lat: lat,
        lon: lon,
      );
      
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Punch in successful.')),
      );
      Navigator.of(context).pop(true);
    } on ApiException catch (error) {
      setState(() => _error = error.message);
    } catch (_) {
      setState(() => _error = 'Unable to punch in. Please try again.');
    } finally {
      if (mounted) setState(() => _isSubmitting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Punch In')),
      body: ListView(
        padding: const EdgeInsets.all(18),
        children: [
          if (_error != null) ...[
            AppErrorBanner(message: _error!),
            const SizedBox(height: 14),
          ],
          Text(
            'Attendance Type',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.w700,
                ),
          ),
          const SizedBox(height: 10),
          SegmentedButton<AttendanceType>(
            segments: const [
              ButtonSegment(
                value: AttendanceType.office,
                label: Text('Office'),
                icon: Icon(Icons.business_outlined),
              ),
              ButtonSegment(
                value: AttendanceType.site,
                label: Text('Site'),
                icon: Icon(Icons.engineering_outlined),
              ),
            ],
            selected: {_attendanceType},
            onSelectionChanged: (selection) {
              setState(() => _attendanceType = selection.first);
            },
          ),
          const SizedBox(height: 30),
          
          // 🚨 Helpful contextual helper text for the employee
          Card(
            color: Theme.of(context).colorScheme.surfaceVariant.withOpacity(0.3),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  Icon(
                    _attendanceType == AttendanceType.office 
                        ? Icons.wifi_find_outlined 
                        : Icons.location_on_outlined,
                    color: Theme.of(context).primaryColor,
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      _attendanceType == AttendanceType.office
                          ? 'Office punch-in validates your session directly against the secure office router IP network.'
                          : 'Site punch-in will capture your precise GPS coordinates alongside the shift entry.',
                      style: Theme.of(context).textTheme.bodyMedium,
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 40),
          PrimaryButton(
            label: 'Submit Punch In',
            icon: Icons.check_circle_outline,
            isLoading: _isSubmitting,
            onPressed: _submit,
          ),
        ],
      ),
    );
  }
}