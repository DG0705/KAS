from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Attendance
from .serializers import AttendanceSerializer, PunchInSerializer, PunchOutSerializer


class PunchInView(APIView):
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
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
