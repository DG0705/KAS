from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Attendance
from .serializers import AttendanceSerializer, PunchInSerializer, PunchOutSerializer


# --- 1. Define Office Wi-Fi IP ---
# 🚨 REPLACE THIS WITH YOUR ACTUAL OFFICE IP (Search "What is my IP" on office Wi-Fi)
OFFICE_IP = "223.181.60.234" 

def get_client_ip(request):
    """Extracts the real IP address of the mobile phone, even on Render"""
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
        # --- 2. The Wi-Fi Security Gate ---
        user_ip = get_client_ip(request)
        attendance_type = request.data.get('type')
        
        # We only enforce the Wi-Fi check if they select "Office"
        if attendance_type == 'office' and user_ip != OFFICE_IP:
            return Response(
                {"detail": f"You must be connected to the Office Wi-Fi to punch in. (Detected IP: {user_ip})" },
                status=status.HTTP_403_FORBIDDEN
            )

        # --- 3. Proceed with normal Punch-In ---
        serializer = PunchInSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        attendance = serializer.save()

        return Response(
            {
                "message": "Punch in successful.",
                "attendance": AttendanceSerializer(
                    attendance,
                    context={"request": request},
                ).data,
            },
            status=status.HTTP_201_CREATED,
        )


class PunchOutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = PunchOutSerializer(data={}, context={"request": request})
        serializer.is_valid(raise_exception=True)
        attendance = serializer.save()

        return Response(
            {
                "message": "Punch out successful.",
                "punch_out": attendance.punch_out,
                "attendance": AttendanceSerializer(
                    attendance,
                    context={"request": request},
                ).data,
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