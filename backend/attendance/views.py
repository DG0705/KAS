from django.utils import timezone
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Attendance
from .serializers import AttendanceSerializer, PunchInSerializer, PunchOutSerializer
from .services import get_open_attendance

# 🚨 REPLACE WITH YOUR EXACT OFFICE WI-FI IP
OFFICE_IP = "223.181.60.234" 

# 🚨 A secret password so only YOU can trigger the auto-checkout
CRON_SECRET = "lushvibes0202"

def get_client_ip(request):
    """Extracts the real IP address of the mobile phone"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class PunchInView(APIView):
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        user_ip = get_client_ip(request)
        attendance_type = request.data.get('attendance_type')
        
        if attendance_type == 'office' and user_ip != OFFICE_IP:
            return Response(
                {"detail": f"You must be connected to the Office Wi-Fi to punch in. (Detected IP: {user_ip})" },
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = PunchInSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        attendance = serializer.save()

        return Response(
            {
                "message": "Punch in successful.",
                "attendance": AttendanceSerializer(attendance, context={"request": request}).data,
            },
            status=status.HTTP_201_CREATED,
        )


class PunchOutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        # --- PATH 1: Secure the Punch Out ---
        employee = request.user
        open_attendance = get_open_attendance(employee)

        if not open_attendance:
            return Response({"detail": "No active punch-in found."}, status=status.HTTP_400_BAD_REQUEST)

        # Only enforce Wi-Fi if they originally punched in at the office
        if open_attendance.attendance_type == 'office':
            user_ip = get_client_ip(request)
            if user_ip != OFFICE_IP:
                return Response(
                    {"detail": f"You must be connected to the Office Wi-Fi to punch out. (Detected IP: {user_ip})" },
                    status=status.HTTP_403_FORBIDDEN
                )

        serializer = PunchOutSerializer(data={}, context={"request": request})
        serializer.is_valid(raise_exception=True)
        attendance = serializer.save()

        return Response(
            {
                "message": "Punch out successful.",
                "punch_out": attendance.punch_out,
                "attendance": AttendanceSerializer(attendance, context={"request": request}).data,
            },
            status=status.HTTP_200_OK,
        )


class AttendanceHistoryView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = AttendanceSerializer

    def get_queryset(self):
        return (
            Attendance.objects.filter(employee=self.request.user)
            .select_related("employee")
            .order_by("-punch_in")
        )


# --- PATH 4: The Midnight Auto-Checkout Webhook ---
class AutoPunchOutView(APIView):
    permission_classes = () # No login required, we use the secret key instead

    def get(self, request):
        secret = request.query_params.get('secret')
        
        # Block hackers from triggering this URL
        if secret != CRON_SECRET:
            return Response({"detail": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        # Find everyone who forgot to punch out (punch_out is empty)
        open_records = Attendance.objects.filter(punch_out__isnull=True)
        count = open_records.count()

        # Force punch them out
        for record in open_records:
            record.punch_out = timezone.now()
            record.status = Attendance.Status.COMPLETED
            record.save()

        return Response({"message": f"Midnight Sweep Complete: Auto-punched out {count} employees."})