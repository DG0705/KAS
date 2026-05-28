# Employee Attendance Management MVP

Production-minded MVP for employee office/site attendance.

## Apps

- `backend/`: Django REST Framework API with JWT authentication, SQLite, local media storage, Django Admin, and attendance workflow APIs.
- `mobile_app/`: Flutter mobile app source with login, dashboard, punch in, selfie/GPS capture, punch out, and attendance history.

## Backend

```powershell
cd C:\Users\darsh\OneDrive\Desktop\KAS
venv\Scripts\python.exe -m pip install -r backend\requirements.txt
cd backend
..\venv\Scripts\python.exe manage.py migrate
..\venv\Scripts\python.exe manage.py createsuperuser
..\venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000
```

## Mobile

```powershell
cd C:\Users\darsh\OneDrive\Desktop\KAS\mobile_app
flutter pub get
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000/api
```

Use `http://10.0.2.2:8000/api` for Android emulator. For a real phone, use the computer LAN IP, for example `http://192.168.1.25:8000/api`.

If platform folders are missing, run this inside `mobile_app/`:

```powershell
flutter create . --platforms=android,ios --project-name employee_attendance_app --org com.kas.attendance
```
