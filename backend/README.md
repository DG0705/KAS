# Attendance Backend

Django REST backend for the employee attendance MVP.

## Setup

```powershell
cd C:\Users\darsh\OneDrive\Desktop\KAS
venv\Scripts\python.exe -m pip install -r backend\requirements.txt
Copy-Item backend\.env.example backend\.env
cd backend
..\venv\Scripts\python.exe manage.py migrate
..\venv\Scripts\python.exe manage.py createsuperuser
..\venv\Scripts\python.exe manage.py runserver
```

## Current Scope

- Custom `Employee` auth model with email login, phone, role, and admin support.
- `Attendance` model with office/site type, GPS coordinates, selfie upload, punch timestamps, and status.
- Django Admin registration for employees and attendance records.
- SQLite, local media storage, DRF, JWT settings, and CORS configuration.
- JWT authentication APIs for login, token refresh, and current employee profile.
- Attendance APIs for punch in, punch out, and employee attendance history.

## Authentication API

Base URL: `/api/auth/`

| Method | Endpoint | Auth | Purpose |
| --- | --- | --- | --- |
| POST | `/api/auth/login/` | Public | Login with `email` and `password`; returns `access`, `refresh`, and `employee`. |
| POST | `/api/auth/refresh/` | Public | Exchange a valid refresh token for a new access token. |
| GET | `/api/auth/me/` | Bearer token | Return the authenticated employee profile. |

## Attendance API

Base URL: `/api/attendance/`

All attendance endpoints require:

```http
Authorization: Bearer <access_token>
```

| Method | Endpoint | Content Type | Purpose |
| --- | --- | --- | --- |
| POST | `/api/attendance/punch-in/` | `multipart/form-data` | Create an active attendance record with GPS, selfie, and attendance type. |
| POST | `/api/attendance/punch-out/` | `application/json` | Complete the employee's active attendance record. |
| GET | `/api/attendance/history/` | `application/json` | Return the authenticated employee's records, latest first. |

### Postman: Punch In

Use `Body -> form-data`:

| Key | Type | Example |
| --- | --- | --- |
| `latitude` | Text | `28.613900` |
| `longitude` | Text | `77.209000` |
| `attendance_type` | Text | `office` or `site` |
| `selfie` | File | `selfie.jpg` |

Example response:

```json
{
  "message": "Punch in successful.",
  "attendance": {
    "id": 1,
    "employee": 1,
    "employee_name": "Demo Employee",
    "employee_email": "employee@example.com",
    "punch_in": "2026-05-26T19:40:12.123456+05:30",
    "punch_out": null,
    "latitude": "28.613900",
    "longitude": "77.209000",
    "selfie": "http://127.0.0.1:8000/media/selfies/2026/05/26/employee_1_ab12cd34ef56.jpg",
    "selfie_url": "http://127.0.0.1:8000/media/selfies/2026/05/26/employee_1_ab12cd34ef56.jpg",
    "attendance_type": "site",
    "status": "present",
    "created_at": "2026-05-26T19:40:12.123456+05:30"
  }
}
```

### Postman: Punch Out

Use `POST /api/attendance/punch-out/` with an empty JSON body:

```json
{}
```

Example response:

```json
{
  "message": "Punch out successful.",
  "punch_out": "2026-05-26T20:05:44.123456+05:30",
  "attendance": {
    "id": 1,
    "employee": 1,
    "employee_name": "Demo Employee",
    "employee_email": "employee@example.com",
    "punch_in": "2026-05-26T19:40:12.123456+05:30",
    "punch_out": "2026-05-26T20:05:44.123456+05:30",
    "latitude": "28.613900",
    "longitude": "77.209000",
    "selfie": "http://127.0.0.1:8000/media/selfies/2026/05/26/employee_1_ab12cd34ef56.jpg",
    "selfie_url": "http://127.0.0.1:8000/media/selfies/2026/05/26/employee_1_ab12cd34ef56.jpg",
    "attendance_type": "site",
    "status": "completed",
    "created_at": "2026-05-26T19:40:12.123456+05:30"
  }
}
```

### Postman: Attendance History

Use `GET /api/attendance/history/`.

Example response:

```json
[
  {
    "id": 1,
    "employee": 1,
    "employee_name": "Demo Employee",
    "employee_email": "employee@example.com",
    "punch_in": "2026-05-26T19:40:12.123456+05:30",
    "punch_out": "2026-05-26T20:05:44.123456+05:30",
    "latitude": "28.613900",
    "longitude": "77.209000",
    "selfie": "http://127.0.0.1:8000/media/selfies/2026/05/26/employee_1_ab12cd34ef56.jpg",
    "selfie_url": "http://127.0.0.1:8000/media/selfies/2026/05/26/employee_1_ab12cd34ef56.jpg",
    "attendance_type": "site",
    "status": "completed",
    "created_at": "2026-05-26T19:40:12.123456+05:30"
  }
]
```

### Common Error Responses

Duplicate punch in:

```json
{
  "detail": ["You are already punched in. Please punch out first."]
}
```

Punch out without punch in:

```json
{
  "detail": ["No active punch-in found. Please punch in first."]
}
```

Invalid or missing fields return `400 Bad Request` with field-level errors, such as `selfie`, `latitude`, `longitude`, or `attendance_type`.

## Migration And Testing

```powershell
cd C:\Users\darsh\OneDrive\Desktop\KAS\backend
..\venv\Scripts\python.exe manage.py makemigrations
..\venv\Scripts\python.exe manage.py migrate
..\venv\Scripts\python.exe manage.py test
```
