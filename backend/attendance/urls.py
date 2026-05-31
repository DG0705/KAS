from django.urls import path
from . import views

app_name = "attendance"

urlpatterns = [
    path("punch-in/", views.PunchInView.as_view(), name="punch-in"),
    path("punch-out/", views.PunchOutView.as_view(), name="punch-out"),
    path("history/", views.AttendanceHistoryView.as_view(), name="history"),
    path("auto-checkout/", views.AutoPunchOutView.as_view(), name="auto-checkout"),
]