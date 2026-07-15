import '../models/attendance_record.dart';
import 'api_client.dart';

class AttendanceService {
  const AttendanceService({required ApiClient apiClient}) : _apiClient = apiClient;

  final ApiClient _apiClient;

  Future<AttendanceRecord> punchIn({
    required AttendanceType attendanceType,
    double? lat,
    double? lon,
  }) async {
    // Build the JSON body
    final Map<String, dynamic> requestBody = {
      'attendance_type': attendanceType.value,
    };

    // If it's a site punch-in, attach the coordinates
    if (attendanceType.value == 'site' && lat != null && lon != null) {
      requestBody['latitude'] = lat;
      requestBody['longitude'] = lon;
    }

    // Send as a standard JSON request instead of multipart
    final json = await _apiClient.postJson(
      '/attendance/punch-in/',
      requestBody,
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

  // --- 🚨 NEW: Field Force Management API Calls ---
  Future<Map<String, dynamic>> checkInToClient({
    required String clientName,
    required double lat,
    required double lon,
  }) async {
    // Send as JSON since the selfie is no longer needed
    final json = await _apiClient.postJson(
      '/attendance/site-checkin/',
      {
        'client_name': clientName,
        'check_in_latitude': lat,
        'check_in_longitude': lon,
      },
    );
    return json as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> checkOutOfClient(String notes) async {
    final json = await _apiClient.postJson(
      '/attendance/site-checkout/',
      {'meeting_notes': notes},
    );
    return json as Map<String, dynamic>;
  }
}