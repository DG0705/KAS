import 'package:image_picker/image_picker.dart';

import '../models/attendance_record.dart';
import 'api_client.dart';

class AttendanceService {
  const AttendanceService({required ApiClient apiClient}) : _apiClient = apiClient;

  final ApiClient _apiClient;

  Future<AttendanceRecord> punchIn({
    required double latitude,
    required double longitude,
    required XFile selfie,
    required AttendanceType attendanceType,
  }) async {
    final json = await _apiClient.postMultipart(
      '/attendance/punch-in/',
      fields: {
        // 🚨 Appending exact GPS coordinates for the Django geofence
        'latitude': latitude.toString(),
        'longitude': longitude.toString(),
        // Ensure this matches the field name in your Django PunchInSerializer
        'type': attendanceType.value, 
      },
      fileField: 'selfie',
      filePath: selfie.path,
    );

    return AttendanceRecord.fromJson(json['attendance'] as Map<String, dynamic>);
  }

  Future<AttendanceRecord> punchOut() async {
    final json = await _apiClient.postJson('/attendance/punch-out/', {});
    return AttendanceRecord.fromJson(json['attendance'] as Map<String, dynamic>);
  }

  Future<List<AttendanceRecord>> history() async {
    final list = await _apiClient.getList('/attendance/history/');
    return list
        .map((item) => AttendanceRecord.fromJson(item as Map<String, dynamic>))
        .toList();
  }
}