
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from .models import Employee


class AuthenticationApiTests(APITestCase):
    def setUp(self):
        self.employee = Employee.objects.create_user(
            email="employee@example.com",
            password="StrongPass123!",
            name="Demo Employee",
            phone="9876543210",
        )

    def test_login_returns_jwt_tokens_and_employee_profile(self):
        response = self.client.post(
            reverse("accounts:login"),
            {
                "email": "employee@example.com",
                "password": "StrongPass123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["employee"]["email"], self.employee.email)
        self.assertEqual(response.data["employee"]["role"], Employee.Role.EMPLOYEE)

        access_token = AccessToken(response.data["access"])
        self.assertEqual(access_token["email"], self.employee.email)
        self.assertEqual(access_token["role"], Employee.Role.EMPLOYEE)

    def test_login_rejects_invalid_credentials(self):
        response = self.client.post(
            reverse("accounts:login"),
            {
                "email": "employee@example.com",
                "password": "wrong-password",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_requires_authentication(self):
        response = self.client.get(reverse("accounts:me"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_returns_authenticated_employee(self):
        login_response = self.client.post(
            reverse("accounts:login"),
            {
                "email": "employee@example.com",
                "password": "StrongPass123!",
            },
            format="json",
        )
        access_token = login_response.data["access"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        response = self.client.get(reverse("accounts:me"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.employee.email)

    def test_refresh_returns_new_access_token(self):
        login_response = self.client.post(
            reverse("accounts:login"),
            {
                "email": "employee@example.com",
                "password": "StrongPass123!",
            },
            format="json",
        )

        response = self.client.post(
            reverse("accounts:token-refresh"),
            {"refresh": login_response.data["refresh"]},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
