import csv
from django.http import HttpResponse
from django.contrib import admin
from django.utils import timezone
from .models import Attendance, SiteVisit

@admin.action(description="Export Selected Records to CSV (Excel)")
def export_to_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="attendance_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Employee', 'Date', 'Punch In Time', 'Punch Out Time', 'Total Hours', 'Type', 'Status'])
    
    for record in queryset:
        local_punch_in = timezone.localtime(record.punch_in)
        punch_in_str = local_punch_in.strftime("%I:%M %p")
        
        punch_out_str = "Still active"
        if record.punch_out:
            local_punch_out = timezone.localtime(record.punch_out)
            punch_out_str = local_punch_out.strftime("%I:%M %p")
            
        writer.writerow([
            record.employee.email, 
            local_punch_in.strftime("%Y-%m-%d"), 
            punch_in_str,
            punch_out_str,
            record.total_hours,
            record.get_attendance_type_display(),
            record.get_status_display()
        ])
        
    return response

class SiteVisitInline(admin.TabularInline):
    model = SiteVisit
    extra = 0 
    can_delete = False
    show_change_link = True
    readonly_fields = ('arrived_at', 'departed_at', 'meeting_duration', 'check_in_latitude', 'check_in_longitude')
    fields = ('client_name', 'status', 'arrived_at', 'departed_at', 'meeting_duration')

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'punch_in', 'punch_out', 'total_hours', 'attendance_type', 'status')
    list_filter = ('punch_in', 'attendance_type', 'status', 'employee')
    search_fields = ('employee__email',)
    readonly_fields = ('created_at', 'updated_at')
    actions = [export_to_csv]
    inlines = [SiteVisitInline] 

@admin.register(SiteVisit)
class SiteVisitAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'employee', 'arrived_at', 'status')
    list_filter = ('status', 'arrived_at', 'employee')
    
    # Add map_view to readonly fields so it renders on the page
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
        # Check if we actually have coordinates before trying to load the map
        if obj.check_in_latitude and obj.check_in_longitude:
            lat = obj.check_in_latitude
            lon = obj.check_in_longitude
            
            # Create a small bounding box to zoom the map in perfectly
            bbox_lon_min = lon - Decimal('0.005')
            bbox_lat_min = lat - Decimal('0.005')
            bbox_lon_max = lon + Decimal('0.005')
            bbox_lat_max = lat + Decimal('0.005')

            # Render an interactive OpenStreetMap iframe
            return mark_safe(f'''
                <div style="width: 100%; max-width: 600px; margin-top: 10px;">
                    <iframe width="100%" height="400" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" 
                    src="https://www.openstreetmap.org/export/embed.html?bbox={bbox_lon_min}%2C{bbox_lat_min}%2C{bbox_lon_max}%2C{bbox_lat_max}&amp;layer=mapnik&amp;marker={lat}%2C{lon}" 
                    style="border: 2px solid #ccc; border-radius: 8px;"></iframe>
                </div>
            ''')
        return "Waiting for location data..."
    
    map_view.short_description = "Live Map"