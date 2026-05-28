import 'package:flutter/material.dart';

import '../models/attendance_record.dart';
import '../utils/date_formatters.dart';

class AttendanceRecordCard extends StatelessWidget {
  const AttendanceRecordCard({
    super.key,
    required this.record,
  });

  final AttendanceRecord record;

  @override
  Widget build(BuildContext context) {
    final isOpen = record.isOpen;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    DateFormatters.date(record.punchIn),
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                ),
                Chip(
                  visualDensity: VisualDensity.compact,
                  label: Text(isOpen ? 'Active' : record.status.label),
                  backgroundColor: isOpen
                      ? const Color(0xFFDDF3E7)
                      : const Color(0xFFE8ECEF),
                ),
              ],
            ),
            const SizedBox(height: 10),
            Row(
              children: [
                _Detail(
                  icon: Icons.login,
                  label: 'In',
                  value: DateFormatters.time(record.punchIn),
                ),
                const SizedBox(width: 16),
                _Detail(
                  icon: Icons.logout,
                  label: 'Out',
                  value: DateFormatters.time(record.punchOut),
                ),
              ],
            ),
            const SizedBox(height: 10),
            Row(
              children: [
                Icon(
                  record.attendanceType == AttendanceType.site
                      ? Icons.engineering_outlined
                      : Icons.business_outlined,
                  size: 18,
                ),
                const SizedBox(width: 8),
                Text(record.attendanceType.label),
                const Spacer(),
                const Icon(Icons.location_on_outlined, size: 18),
                const SizedBox(width: 4),
                Text(
                  '${record.latitude.toStringAsFixed(4)}, ${record.longitude.toStringAsFixed(4)}',
                  style: Theme.of(context).textTheme.bodySmall,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _Detail extends StatelessWidget {
  const _Detail({
    required this.icon,
    required this.label,
    required this.value,
  });

  final IconData icon;
  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Row(
        children: [
          Icon(icon, size: 18),
          const SizedBox(width: 8),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(label, style: Theme.of(context).textTheme.labelSmall),
                Text(value, overflow: TextOverflow.ellipsis),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
