from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import SiteVisit

@admin.register(SiteVisit)
class SiteVisitAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'employee', 'arrived_at', 'status')
    list_filter = ('status', 'arrived_at', 'employee')
    
    readonly_fields = ('arrived_at', 'check_in_latitude', 'check_in_longitude', 'map_view')
    
    fieldsets = (
        ('Visit Details', {
            'fields': ('employee', 'client_name', 'attendance', 'status', 'arrived_at')
        }),
        ('Location Map', {
            'fields': ('check_in_latitude', 'check_in_longitude', 'map_view')
        }),
    )

    def map_view(self, obj):
        if obj.check_in_latitude and obj.check_in_longitude:
            try:
                # Safely convert to float to prevent TypeErrors during math
                lat = float(obj.check_in_latitude)
                lon = float(obj.check_in_longitude)
                
                # Create a small bounding box to zoom the map in perfectly
                bbox_lon_min = lon - 0.005
                bbox_lat_min = lat - 0.005
                bbox_lon_max = lon + 0.005
                bbox_lat_max = lat + 0.005

                # Render an interactive OpenStreetMap iframe
                return mark_safe(f'''
                    <div style="width: 100%; max-width: 600px; margin-top: 10px;">
                        <iframe width="100%" height="400" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" 
                        src="https://www.openstreetmap.org/export/embed.html?bbox={bbox_lon_min}%2C{bbox_lat_min}%2C{bbox_lon_max}%2C{bbox_lat_max}&amp;layer=mapnik&amp;marker={lat}%2C{lon}" 
                        style="border: 2px solid #ccc; border-radius: 8px;"></iframe>
                    </div>
                ''')
            except Exception as e:
                return f"Map failed to load. Error: {str(e)}"
                
        return "Waiting for location data..."
    
    map_view.short_description = "Live Map"