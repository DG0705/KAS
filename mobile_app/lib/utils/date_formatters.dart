import 'package:intl/intl.dart';

class DateFormatters {
  static final _dateTime = DateFormat('dd MMM yyyy, hh:mm a');
  static final _time = DateFormat('hh:mm a');
  static final _date = DateFormat('dd MMM yyyy');

  static String dateTime(DateTime? value) {
    if (value == null) return '-';
    return _dateTime.format(value.toLocal());
  }

  static String time(DateTime? value) {
    if (value == null) return '-';
    return _time.format(value.toLocal());
  }

  static String date(DateTime? value) {
    if (value == null) return '-';
    return _date.format(value.toLocal());
  }
}
