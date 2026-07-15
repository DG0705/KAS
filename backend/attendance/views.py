from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
from django.utils import timezone
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Attendance, SiteVisit
from .serializers import AttendanceSerializer, PunchInSerializer, PunchOutSerializer, SiteVisitSerializer
from .services import get_open_attendance

CRON_SECRET = "lushvibes0202"
OFFICE_IP = "223.181.57.171" 

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
    # 🚨 Added JSONParser so normal requests are processed smoothly
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    def post(self, request):
        user_ip = get_client_ip(request)
        attendance_type = request.data.get('attendance_type')
        
        # Office Wi-Fi verification
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
        employee = request.user
        open_attendance = get_open_attendance(employee)

        if not open_attendance:
            return Response({"detail": "No active punch-in found."}, status=status.HTTP_400_BAD_REQUEST)

        # Enforce Office IP check on punch-out as well
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


class SiteVisitCheckInView(APIView):
    permission_classes = (IsAuthenticated,)
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    def post(self, request):
        employee = request.user
        open_attendance = get_open_attendance(employee)

        # 1. SMART AUTO-PUNCH: If no open shift, create one automatically
        if not open_attendance:
            data = request.data.copy() if hasattr(request.data, 'copy') else request.data
            data['attendance_type'] = 'site'
            
            # 🚨 Map FFM coordinates to the core Attendance punch-in
            if data.get('check_in_latitude'):
                data['latitude'] = data.get('check_in_latitude')
            if data.get('check_in_longitude'):
                data['longitude'] = data.get('check_in_longitude')

            punch_in_serializer = PunchInSerializer(
                data=data,
                context={'request': request}
            )
            punch_in_serializer.is_valid(raise_exception=True)
            open_attendance = punch_in_serializer.save()

        # 2. Block concurrent meetings
        active_meeting = SiteVisit.objects.filter(employee=employee, status=SiteVisit.VisitStatus.IN_PROGRESS).first()
        if active_meeting:
            return Response(
                {"detail": f"You are already in a meeting with {active_meeting.client_name}. Please check out first."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # 3. Create the specific Client Visit
        client_name = request.data.get('client_name')
        lat = request.data.get('check_in_latitude')
        lon = request.data.get('check_in_longitude')

        if not client_name:
            return Response({"detail": "Client name is required."}, status=status.HTTP_400_BAD_REQUEST)

        visit = SiteVisit.objects.create(
            employee=employee,
            attendance=open_attendance,
            client_name=client_name,
            check_in_latitude=lat,
            check_in_longitude=lon
        )

        return Response({
            "message": "Checked into client site successfully.",
            "visit": SiteVisitSerializer(visit).data
        }, status=status.HTTP_201_CREATED)


class SiteVisitCheckOutView(APIView):
    permission_classes = (IsAuthenticated,)
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    def post(self, request):
        employee = request.user
        active_meeting = SiteVisit.objects.filter(employee=employee, status=SiteVisit.VisitStatus.IN_PROGRESS).first()

        if not active_meeting:
            return Response({"detail": "No active client meeting found to check out of."}, status=status.HTTP_400_BAD_REQUEST)

        notes = request.data.get('meeting_notes', '')
        
        # Close the meeting
        active_meeting.departed_at = timezone.now()
        active_meeting.status = SiteVisit.VisitStatus.COMPLETED
        active_meeting.meeting_notes = notes
        active_meeting.save()

        return Response({
            "message": "Checked out of client site successfully.",
            "visit": SiteVisitSerializer(active_meeting).data
        }, status=status.HTTP_200_OK)


class AutoPunchOutView(APIView):
    permission_classes = () 

    def get(self, request):
        secret = request.query_params.get('secret')
        
        if secret != CRON_SECRET:
            return Response({"detail": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        open_records = Attendance.objects.filter(punch_out__isnull=True)
        count = open_records.count()

        for record in open_records:
            record.punch_out = timezone.now()
            record.status = Attendance.Status.COMPLETED
            record.save()
            
            SiteVisit.objects.filter(
                attendance=record, 
                status=SiteVisit.VisitStatus.IN_PROGRESS
            ).update(
                departed_at=timezone.now(), 
                status=SiteVisit.VisitStatus.COMPLETED, 
                meeting_notes="Auto-closed by midnight sweep."
            )

        return Response({"message": f"Midnight Sweep Complete: Auto-punched out {count} employees."})