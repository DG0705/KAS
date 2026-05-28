enum AttendanceType {
  office('office', 'Office'),
  site('site', 'Site');

  const AttendanceType(this.value, this.label);

  final String value;
  final String label;

  static AttendanceType fromValue(String value) {
    return AttendanceType.values.firstWhere(
      (type) => type.value == value,
      orElse: () => AttendanceType.office,
    );
  }
}

enum AttendanceStatus {
  present('present', 'Present'),
  completed('completed', 'Completed'),
  pending('pending', 'Pending');

  const AttendanceStatus(this.value, this.label);

  final String value;
  final String label;

  static AttendanceStatus fromValue(String value) {
    return AttendanceStatus.values.firstWhere(
      (status) => status.value == value,
      orElse: () => AttendanceStatus.pending,
    );
  }
}

class AttendanceRecord {
  const AttendanceRecord({
    required this.id,
    required this.employeeId,
    required this.employeeName,
    required this.employeeEmail,
    required this.punchIn,
    required this.punchOut,
    required this.latitude,
    required this.longitude,
    required this.selfie,
    required this.selfieUrl,
    required this.attendanceType,
    required this.status,
    required this.createdAt,
  });

  final int id;
  final int employeeId;
  final String employeeName;
  final String employeeEmail;
  final DateTime? punchIn;
  final DateTime? punchOut;
  final double latitude;
  final double longitude;
  final String selfie;
  final String selfieUrl;
  final AttendanceType attendanceType;
  final AttendanceStatus status;
  final DateTime? createdAt;

  bool get isOpen => punchOut == null && status == AttendanceStatus.present;

  factory AttendanceRecord.fromJson(Map<String, dynamic> json) {
    return AttendanceRecord(
      id: json['id'] as int,
      employeeId: json['employee'] as int,
      employeeName: json['employee_name'] as String? ?? '',
      employeeEmail: json['employee_email'] as String? ?? '',
      punchIn: DateTime.tryParse(json['punch_in'] as String? ?? ''),
      punchOut: DateTime.tryParse(json['punch_out'] as String? ?? ''),
      latitude: _toDouble(json['latitude']),
      longitude: _toDouble(json['longitude']),
      selfie: json['selfie'] as String? ?? '',
      selfieUrl: json['selfie_url'] as String? ?? '',
      attendanceType: AttendanceType.fromValue(
        json['attendance_type'] as String? ?? 'office',
      ),
      status: AttendanceStatus.fromValue(json['status'] as String? ?? 'pending'),
      createdAt: DateTime.tryParse(json['created_at'] as String? ?? ''),
    );
  }

  static double _toDouble(Object? value) {
    if (value is num) return value.toDouble();
    return double.tryParse(value?.toString() ?? '') ?? 0;
  }
}
