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
    list_display = ('client_name', 'employee', 'arrived_at', 'departed_at', 'meeting_duration', 'status')
    list_filter = ('status', 'arrived_at', 'employee')
    search_fields = ('client_name', 'employee__email')
    readonly_fields = ('created_at', 'meeting_duration')
    
    fieldsets = (
        ('Meeting Info', {
            'fields': ('employee', 'attendance', 'client_name', 'status')
        }),
        ('Time & Location', {
            'fields': ('arrived_at', 'departed_at', 'meeting_duration', 'check_in_latitude', 'check_in_longitude')
        }),
        ('Outcomes', {
            'fields': ('meeting_notes',)
        }),
    )