from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Your existing API routes
    path('api/attendance/', include('attendance.urls')),
    path('api/accounts/', include('accounts.urls')), # Assuming you have this
    
    # 🚨 This Catch-All route MUST go at the very bottom!
    # It tells Django: "If the URL isn't an API or Admin, serve the Web App"
    re_path(r'^.*$', TemplateView.as_view(template_name='index.html')),
]

# (Keep your existing static/media settings here if you have them)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)