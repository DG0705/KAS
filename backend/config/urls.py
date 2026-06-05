from django.contrib import admin
from django.urls import path, include
# You can remove TemplateView and re_path imports if you aren't using them elsewhere

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/attendance/', include('attendance.urls')),
    path('api/auth/', include('accounts.urls')),
    
    
]