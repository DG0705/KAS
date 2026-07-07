class Employee {
  const Employee({
    required this.id,
    required this.name,
    required this.email,
    required this.phone,
    required this.role,
    required this.createdAt,
  });

  final int id;
  final String name;
  final String email;
  final String phone;
  final String role;
  final DateTime? createdAt;

  bool get isAdmin => role == 'admin';
  bool get isSalesperson => role == 'salesperson';

  factory Employee.fromJson(Map<String, dynamic> json) {
    return Employee(
      id: json['id'] as int,
      name: json['name'] as String? ?? '',
      email: json['email'] as String? ?? '',
      phone: json['phone'] as String? ?? '',
      role: json['role'] as String? ?? 'employee',
      createdAt: DateTime.tryParse(json['created_at'] as String? ?? ''),
    );
  }
}
