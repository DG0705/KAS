from rest_framework import serializers

from .models import Attendance, SiteVisit
from .services import get_open_attendance, punch_in_employee, punch_out_employee


class AttendanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.name", read_only=True)
    employee_email = serializers.EmailField(source="employee.email", read_only=True)
    selfie_url = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = (
            "id",
            "employee",
            "employee_name",
            "employee_email",
            "punch_in",
            "punch_out",
            "latitude",
            "longitude",
            "selfie",
            "selfie_url",
            "attendance_type",
            "status",
            "created_at",
        )
        read_only_fields = fields

    def get_selfie_url(self, obj):
        if not obj.selfie:
            return None
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.selfie.url)
        return obj.selfie.url


class PunchInSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        # 🚨 Added latitude and longitude, removed selfie
        fields = ("attendance_type", "latitude", "longitude")
        extra_kwargs = {
            "attendance_type": {"required": True},
        }

    def validate(self, attrs):
        employee = self.context["request"].user
        if get_open_attendance(employee) is not None:
            raise serializers.ValidationError(
                {"detail": "You are already punched in. Please punch out first."}
            )

        # 🚨 Require coordinates for Site punch-ins
        if attrs.get('attendance_type') == 'site':
            if not attrs.get('latitude') or not attrs.get('longitude'):
                raise serializers.ValidationError(
                    {"detail": "Latitude and longitude are required for Site punch-ins."}
                )

        return attrs

    def create(self, validated_data):
        employee = self.context["request"].user
        try:
            return punch_in_employee(employee, **validated_data)
        except ValueError as exc:
            raise serializers.ValidationError({"detail": str(exc)}) from exc


class PunchOutSerializer(serializers.Serializer):
    attendance = serializers.SerializerMethodField(read_only=True)
    punch_out = serializers.DateTimeField(read_only=True)

    def get_attendance(self, obj):
        return obj.id

    def validate(self, attrs):
        employee = self.context["request"].user
        open_attendance = get_open_attendance(employee)

        if not open_attendance:
            raise serializers.ValidationError(
                {"detail": "No active punch-in found. Please punch in first."}
            )

        attrs["attendance"] = open_attendance
        return attrs

    def save(self, **kwargs):
        attendance = punch_out_employee(self.context["request"].user)
        if attendance is None:
            raise serializers.ValidationError(
                {"detail": "No active punch-in found. Please punch in first."}
            )
        return attendance


class SiteVisitSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteVisit
        fields = (
            "id", 
            "client_name", 
            "arrived_at", 
            "departed_at", 
            "meeting_duration", 
            "status", 
            "meeting_notes",
            "check_in_latitude",
            "check_in_longitude"
        )
        read_only_fields = fields