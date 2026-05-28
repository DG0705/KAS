import os
import uuid
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone

from .validators import validate_selfie_file


def attendance_selfie_upload_path(instance, filename: str) -> str:
    extension = os.path.splitext(filename)[1].lower()
    date_path = timezone.localdate().strftime("%Y/%m/%d")
    employee_id = instance.employee_id or "unassigned"
    unique_suffix = uuid.uuid4().hex[:12]
    return f"selfies/{date_path}/employee_{employee_id}_{unique_suffix}{extension}"


class Attendance(models.Model):
    class AttendanceType(models.TextChoices):
        OFFICE = "office", "Office"
        SITE = "site", "Site"

    class Status(models.TextChoices):
        PRESENT = "present", "Present"
        COMPLETED = "completed", "Completed"
        PENDING = "pending", "Pending"

    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="attendance_records",
    )
    punch_in = models.DateTimeField(default=timezone.now)
    punch_out = models.DateTimeField(null=True, blank=True)
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[MinValueValidator(Decimal("-90")), MaxValueValidator(Decimal("90"))],
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[MinValueValidator(Decimal("-180")), MaxValueValidator(Decimal("180"))],
    )
    selfie = models.ImageField(
        upload_to=attendance_selfie_upload_path,
        validators=[validate_selfie_file],
    )
    attendance_type = models.CharField(
        max_length=10,
        choices=AttendanceType.choices,
        default=AttendanceType.OFFICE,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PRESENT,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-punch_in"]
        indexes = [
            models.Index(fields=["employee", "-punch_in"]),
            models.Index(fields=["attendance_type", "-punch_in"]),
            models.Index(fields=["status"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["employee"],
                condition=Q(punch_out__isnull=True),
                name="unique_open_attendance_per_employee",
            ),
            models.CheckConstraint(
                condition=Q(latitude__gte=-90, latitude__lte=90),
                name="attendance_latitude_range",
            ),
            models.CheckConstraint(
                condition=Q(longitude__gte=-180, longitude__lte=180),
                name="attendance_longitude_range",
            ),
        ]

    def clean(self):
        if self.punch_out and self.punch_out < self.punch_in:
            raise ValidationError({"punch_out": "Punch out cannot be earlier than punch in."})
        if self.status == self.Status.COMPLETED and not self.punch_out:
            raise ValidationError({"status": "Completed records require a punch out timestamp."})
        if self.punch_out and self.status != self.Status.COMPLETED:
            raise ValidationError({"status": "Records with a punch out timestamp must be completed."})

    def __str__(self) -> str:
        punch_date = timezone.localtime(self.punch_in).strftime("%Y-%m-%d %H:%M")
        return f"{self.employee} - {self.attendance_type} - {punch_date}"
