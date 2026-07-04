from django.urls import path
from .views import (
    PunchInView, 
    PunchOutView, 
    AttendanceHistoryView, 
    AutoPunchOutView,
    SiteVisitCheckInView,  # 🚨 New import
    SiteVisitCheckOutView  # 🚨 New import
)

urlpatterns = [
    # Existing Attendance Routes
    path("punch-in/", PunchInView.as_view(), name="punch-in"),
    path("punch-out/", PunchOutView.as_view(), name="punch-out"),
    path("history/", AttendanceHistoryView.as_view(), name="attendance-history"),
    path("auto-punch-out/", AutoPunchOutView.as_view(), name="auto-punch-out"),

    # 🚨 NEW: Field Force Management (FFM) Routes
    path("site-checkin/", SiteVisitCheckInView.as_view(), name="site-checkin"),
    path("site-checkout/", SiteVisitCheckOutView.as_view(), name="site-checkout"),
]