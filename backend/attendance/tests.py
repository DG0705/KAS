import shutil
from datetime import timedelta
from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone
from PIL import Image
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import Employee

from .models import Attendance


TEST_MEDIA_ROOT = Path(__file__).resolve().parent.parent / "test_media"


def make_test_selfie(filename="selfie.jpg"):
    image_file = BytesIO()
    Image.new("RGB", (32, 32), color="white").save(image_file, format="JPEG")
    image_file.seek(0)
    return SimpleUploadedFile(
        filename,
        image_file.read(),
        content_type="image/jpeg",
    )


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class AttendanceApiTests(APITestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.employee = Employee.objects.create_user(
            email="employee@example.com",
            password="StrongPass123!",
            name="Demo Employee",
            phone="9876543210",
        )
        self.other_employee = Employee.objects.create_user(
            email="other@example.com",
            password="StrongPass123!",
            name="Other Employee",
        )

    def authenticate(self):
        login_response = self.client.post(
            reverse("accounts:login"),
            {"email": "employee@example.com", "password": "StrongPass123!"},
            format="json",
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {login_response.data['access']}"
        )

    def punch_in(self, attendance_type=Attendance.AttendanceType.SITE):
        return self.client.post(
            reverse("attendance:punch-in"),
            {
                "latitude": "28.613900",
                "longitude": "77.209000",
                "attendance_type": attendance_type,
                "selfie": make_test_selfie(),
            },
            format="multipart",
        )

    def test_attendance_flow_punch_in_history_and_punch_out(self):
        self.authenticate()

        punch_in_response = self.punch_in()

        self.assertEqual(punch_in_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(punch_in_response.data["message"], "Punch in successful.")
        self.assertEqual(
            punch_in_response.data["attendance"]["attendance_type"],
            Attendance.AttendanceType.SITE,
        )
        self.assertEqual(
            punch_in_response.data["attendance"]["status"],
            Attendance.Status.PRESENT,
        )
        attendance = Attendance.objects.get(id=punch_in_response.data["attendance"]["id"])
        self.assertTrue(attendance.selfie.name.startswith("selfies/"))

        history_response = self.client.get(reverse("attendance:history"))

        self.assertEqual(history_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(history_response.data), 1)
        self.assertEqual(history_response.data[0]["id"], attendance.id)

        punch_out_response = self.client.post(reverse("attendance:punch-out"))

        self.assertEqual(punch_out_response.status_code, status.HTTP_200_OK)
        self.assertEqual(punch_out_response.data["message"], "Punch out successful.")
        self.assertIsNotNone(punch_out_response.data["punch_out"])

        attendance.refresh_from_db()
        self.assertEqual(attendance.status, Attendance.Status.COMPLETED)
        self.assertIsNotNone(attendance.punch_out)

    def test_punch_in_requires_authentication(self):
        response = self.punch_in()

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_duplicate_punch_in_is_rejected(self):
        self.authenticate()
        first_response = self.punch_in()

        second_response = self.punch_in()

        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("already punched in", str(second_response.data).lower())

    def test_punch_out_without_open_attendance_is_rejected(self):
        self.authenticate()

        response = self.client.post(reverse("attendance:punch-out"))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("no active punch-in", str(response.data).lower())

    def test_punch_in_validates_required_fields_and_attendance_type(self):
        self.authenticate()

        missing_selfie_response = self.client.post(
            reverse("attendance:punch-in"),
            {
                "latitude": "28.613900",
                "longitude": "77.209000",
                "attendance_type": Attendance.AttendanceType.OFFICE,
            },
            format="multipart",
        )
        invalid_type_response = self.client.post(
            reverse("attendance:punch-in"),
            {
                "latitude": "28.613900",
                "longitude": "77.209000",
                "attendance_type": "remote",
                "selfie": make_test_selfie("invalid-type.jpg"),
            },
            format="multipart",
        )
        invalid_gps_response = self.client.post(
            reverse("attendance:punch-in"),
            {
                "latitude": "91.000000",
                "longitude": "77.209000",
                "attendance_type": Attendance.AttendanceType.OFFICE,
                "selfie": make_test_selfie("invalid-gps.jpg"),
            },
            format="multipart",
        )

        self.assertEqual(missing_selfie_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(invalid_type_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(invalid_gps_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_history_returns_only_authenticated_employee_records_latest_first(self):
        self.authenticate()
        older_record = Attendance.objects.create(
            employee=self.employee,
            punch_in=timezone.now() - timedelta(days=1),
            latitude="28.613900",
            longitude="77.209000",
            attendance_type=Attendance.AttendanceType.OFFICE,
            status=Attendance.Status.PRESENT,
            selfie=make_test_selfie("older.jpg"),
        )
        newer_record = Attendance.objects.create(
            employee=self.employee,
            punch_in=timezone.now(),
            punch_out=timezone.now(),
            latitude="28.704100",
            longitude="77.102500",
            attendance_type=Attendance.AttendanceType.SITE,
            status=Attendance.Status.COMPLETED,
            selfie=make_test_selfie("newer.jpg"),
        )
        Attendance.objects.create(
            employee=self.other_employee,
            punch_in=timezone.now(),
            latitude="19.076000",
            longitude="72.877700",
            attendance_type=Attendance.AttendanceType.SITE,
            status=Attendance.Status.PRESENT,
            selfie=make_test_selfie("other.jpg"),
        )

        response = self.client.get(reverse("attendance:history"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [record["id"] for record in response.data],
            [newer_record.id, older_record.id],
        )
