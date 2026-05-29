import math
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Attendance
from .serializers import AttendanceSerializer, PunchInSerializer, PunchOutSerializer

# --- 1. Define Office Coordinates and Radius ---
# 🚨 REPLACE THESE WITH YOUR EXACT GOOGLE MAPS COORDINATES
OFFICE_LAT = 19.13598270198228
OFFICE_LON = 772.82766046243769
ALLOWED_RADIUS_METERS = 50


# --- 2. Distance Calculator (Haversine Formula) ---
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371000  # Radius of Earth in meters
    phi_1 = math.radians(lat1)
    phi_2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + \
        math.cos(phi_1) * math.cos(phi_2) * \
        math.sin(delta_lambda / 2.0) ** 2
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


class PunchInView(APIView):
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        # --- 3. Geofence Security Check ---
        try:
            # Extract coordinates from the incoming mobile app request
            user_lat = float(request.data.get('latitude'))
            user_lon = float(request.data.get('longitude'))
        except (TypeError, ValueError):
            return Response(
                {"detail": "Location coordinates (latitude and longitude) are required to punch in."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Calculate exact distance
        distance = calculate_distance(OFFICE_LAT, OFFICE_LON, user_lat, user_lon)

        # Block the punch-in if they are outside the 50m radius
        if distance > ALLOWED_RADIUS_METERS:
            return Response(
                {"detail": f"Too far! You are {int(distance)} meters away. Must be within {ALLOWED_RADIUS_METERS}m of the office."},
                status=status.HTTP_403_FORBIDDEN
            )

        # --- 4. Proceed with normal Punch-In if distance is valid ---
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