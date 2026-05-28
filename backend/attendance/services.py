from django.db import IntegrityError, transaction
from django.utils import timezone

from .models import Attendance


def get_open_attendance(employee):
    return (
        Attendance.objects.filter(employee=employee, punch_out__isnull=True)
        .order_by("-punch_in")
        .first()
    )


def punch_in_employee(employee, **attendance_data):
    try:
        return Attendance.objects.create(
            employee=employee,
            punch_in=timezone.now(),
            status=Attendance.Status.PRESENT,
            **attendance_data,
        )
    except IntegrityError as exc:
        raise ValueError("You are already punched in. Please punch out first.") from exc


@transaction.atomic
def punch_out_employee(employee):
    attendance = (
        Attendance.objects.select_for_update()
        .filter(employee=employee, punch_out__isnull=True)
        .order_by("-punch_in")
        .first()
    )

    if attendance is None:
        return None

    attendance.punch_out = timezone.now()
    attendance.status = Attendance.Status.COMPLETED
    attendance.full_clean()
    attendance.save(update_fields=["punch_out", "status", "updated_at"])
    return attendance
