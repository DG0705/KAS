import 'dart:io';
import 'dart:io';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../models/attendance_record.dart';
import '../services/attendance_service.dart';
import '../services/camera_service.dart';
import '../utils/api_exception.dart';
import '../widgets/app_error_banner.dart';
import '../widgets/primary_button.dart';

class PunchInScreen extends StatefulWidget {
  const PunchInScreen({
    super.key,
    required this.attendanceService,
    this.cameraService,
  });

  final AttendanceService attendanceService;
  final CameraService? cameraService;

  @override
  State<PunchInScreen> createState() => _PunchInScreenState();
}

class _PunchInScreenState extends State<PunchInScreen> {
  AttendanceType _attendanceType = AttendanceType.office;
  XFile? _selfie;
  late final CameraService _cameraService = widget.cameraService ?? CameraService();
  
  bool _isCapturingSelfie = false;
  bool _isSubmitting = false;
  String? _error;

  Future<void> _captureSelfie() async {
    setState(() {
      _isCapturingSelfie = true;
      _error = null;
    });

    try {
      final selfie = await _cameraService.captureSelfie();
      if (mounted && selfie != null) setState(() => _selfie = selfie);
    } catch (_) {
      setState(() => _error = 'Unable to open camera. Please check camera permission.');
    } finally {
      if (mounted) setState(() => _isCapturingSelfie = false);
    }
  }

  Future<void> _submit() async {
    setState(() => _error = null);

    if (_selfie == null) {
      setState(() => _error = 'Selfie photo is required before punch in.');
      return;
    }

    setState(() => _isSubmitting = true);

    try {
      // 🚨 Calling the API with just the Selfie and Type!
      await widget.attendanceService.punchIn(
        selfie: _selfie!,
        attendanceType: _attendanceType,
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
          const SizedBox(height: 18),
          
          // 🚨 GPS UI CARD HAS BEEN COMPLETELY REMOVED!

          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.photo_camera_outlined),
                      const SizedBox(width: 8),
                      Text(
                        'Selfie',
                        style: Theme.of(context).textTheme.titleMedium,
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  if (_selfie != null)
                    ClipRRect(
                      borderRadius: BorderRadius.circular(8),
                      child: Image.file(
                        File(_selfie!.path),
                        height: 220,
                        width: double.infinity,
                        fit: BoxFit.cover,
                      ),
                    )
                  else
                    Container(
                      height: 160,
                      width: double.infinity,
                      alignment: Alignment.center,
                      decoration: BoxDecoration(
                        color: const Color(0xFFE8ECEF),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: const Text('No selfie captured yet.'),
                    ),
                  const SizedBox(height: 12),
                  OutlinedButton.icon(
                    onPressed: _isCapturingSelfie ? null : _captureSelfie,
                    icon: _isCapturingSelfie
                        ? const SizedBox.square(
                            dimension: 16,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Icon(Icons.camera_alt_outlined),
                    label: const Text('Open Camera'),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 20),
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