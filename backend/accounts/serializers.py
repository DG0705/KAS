from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Employee


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ("id", "name", "email", "phone", "role", "created_at")
        read_only_fields = fields


class EmployeeTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = Employee.USERNAME_FIELD

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["role"] = user.role
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["employee"] = EmployeeSerializer(self.user).data
        return data
