import csv
from django.http import HttpResponse
from django.contrib import admin
from django.utils import timezone
from .models import Attendance

@admin.action(description="Export Selected Records to CSV (Excel)")
def export_to_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="attendance_export.csv"'
    
    writer = csv.writer(response)
    # Updated headers to match your actual model
    writer.writerow(['Employee', 'Date', 'Punch In Time', 'Punch Out Time', 'Total Hours', 'Type', 'Status'])
    
    for record in queryset:
        # Safely convert to local time zone for the export
        local_punch_in = timezone.localtime(record.punch_in)
        punch_in_str = local_punch_in.strftime("%I:%M %p")
        
        punch_out_str = "Still active"
        if record.punch_out:
            local_punch_out = timezone.localtime(record.punch_out)
            punch_out_str = local_punch_out.strftime("%I:%M %p")
            
        writer.writerow([
            record.employee.email, 
            local_punch_in.strftime("%Y-%m-%d"), # Extracts the date from punch_in
            punch_in_str,
            punch_out_str,
            record.total_hours,
            record.get_attendance_type_display(),
            record.get_status_display()
        ])
        
    return response

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    # Matches your exact models.py fields
    list_display = ('employee', 'punch_in', 'punch_out', 'total_hours', 'attendance_type', 'status')
    
    # We use punch_in for the date filter since there is no separate 'date' field
    list_filter = ('punch_in', 'attendance_type', 'status', 'employee')
    
    # Allows HR to search by employee email
    search_fields = ('employee__email',)
    
    readonly_fields = ('created_at', 'updated_at')
    actions = [export_to_csv]