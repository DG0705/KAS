from django.urls import path

from .views import AttendanceHistoryView, PunchInView, PunchOutView

app_name = "attendance"

urlpatterns = [
    path("punch-in/", PunchInView.as_view(), name="punch-in"),
    path("punch-out/", PunchOutView.as_view(), name="punch-out"),
    path("history/", AttendanceHistoryView.as_view(), name="history"),
]
