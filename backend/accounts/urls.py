from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import EmployeeLoginView, MeView

app_name = "accounts"

urlpatterns = [
    path("login/", EmployeeLoginView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("me/", MeView.as_view(), name="me"),
]
