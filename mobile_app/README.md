# Employee Attendance Flutter App

Flutter mobile app for employees to login, punch in with GPS and selfie, punch out, and view attendance history.

## Structure

- `lib/models/`: Employee, auth response, and attendance record models.
- `lib/services/`: API client, auth storage, attendance calls, GPS, and camera services.
- `lib/screens/`: Splash, login, dashboard, punch in, and history screens.
- `lib/widgets/`: Reusable buttons, cards, and error UI.
- `lib/utils/`: App config, API exception, and date formatting helpers.

## Run

Start the backend first:

```powershell
cd C:\Users\darsh\OneDrive\Desktop\KAS\backend
..\venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000
```

Run the app:

```powershell
cd C:\Users\darsh\OneDrive\Desktop\KAS\mobile_app
flutter pub get
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000/api
```

For a physical Android/iOS device, replace `10.0.2.2` with the computer LAN IP.

## Required Permissions

When Android and iOS platform folders are generated, add these permissions.

Android `android/app/src/main/AndroidManifest.xml`:

```xml
<uses-permission android:name="android.permission.CAMERA" />
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
```

iOS `ios/Runner/Info.plist`:

```xml
<key>NSCameraUsageDescription</key>
<string>Camera access is required to capture attendance selfies.</string>
<key>NSLocationWhenInUseUsageDescription</key>
<string>Location access is required to capture attendance GPS coordinates.</string>
```

## Backend Endpoints Used

- `POST /api/auth/login/`
- `GET /api/auth/me/`
- `POST /api/attendance/punch-in/`
- `POST /api/attendance/punch-out/`
- `GET /api/attendance/history/`
