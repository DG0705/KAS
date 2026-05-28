from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import EmployeeSerializer, EmployeeTokenObtainPairSerializer


class EmployeeLoginView(TokenObtainPairView):
    permission_classes = ()
    authentication_classes = ()
    serializer_class = EmployeeTokenObtainPairSerializer


class MeView(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = EmployeeSerializer

    def get_object(self):
        return self.request.user
