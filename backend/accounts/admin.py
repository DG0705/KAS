from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Employee


@admin.register(Employee)
class EmployeeAdmin(UserAdmin):
    model = Employee
    ordering = ("name",)
    list_display = ("id", "name", "email", "phone", "role", "is_active", "created_at")
    list_filter = ("role", "is_active", "is_staff", "created_at")
    search_fields = ("name", "email", "phone")
    readonly_fields = ("created_at", "last_login")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Employee Details", {"fields": ("name", "phone", "role")}),
        (
            "Permissions",
            {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")},
        ),
        ("Important Dates", {"fields": ("last_login", "created_at")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "name",
                    "phone",
                    "role",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                ),
            },
        ),
    )

# Register your models here.
