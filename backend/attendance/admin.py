from django.contrib import admin

from .models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "employee_name",
        "employee_email",
        "attendance_type",
        "status",
        "punch_in",
        "punch_out",
        "latitude",
        "longitude",
    )
    list_filter = ("attendance_type", "status", "punch_in", "created_at")
    search_fields = ("employee__name", "employee__email", "employee__phone")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "punch_in"
    ordering = ("-punch_in",)

    @admin.display(ordering="employee__name", description="Employee")
    def employee_name(self, obj):
        return obj.employee.name

    @admin.display(ordering="employee__email", description="Email")
    def employee_email(self, obj):
        return obj.employee.email
