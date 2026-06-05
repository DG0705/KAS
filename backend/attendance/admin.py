import csv
from django.http import HttpResponse
from django.contrib import admin
from .models import Attendance # Change this if your model is named differently

@admin.action(description="Export Selected Records to CSV (Excel)")
def export_to_csv(modeladmin, request, queryset):
    # 1. Create the HttpResponse object with CSV headers
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="attendance_export.csv"'
    
    writer = csv.writer(response)
    
    # 2. Write the header row
    writer.writerow(['Employee Name', 'Date', 'Punch In Time', 'Punch Out Time', 'IP Address'])
    
    # 3. Write the data rows
    for record in queryset:
        # We use .strftime to format the timestamps nicely, handling empty punch-outs
        punch_in = record.punch_in.strftime("%I:%M %p") if record.punch_in else "N/A"
        punch_out = record.punch_out.strftime("%I:%M %p") if record.punch_out else "Still active"
        
        writer.writerow([
            record.employee.email, # Or record.employee.first_name if you have it
            record.date,
            punch_in,
            punch_out,
            record.ip_address
        ])
        
    return response

# Register the Admin Class
@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    # What columns show up on the dashboard
    list_display = ('employee', 'date', 'punch_in', 'punch_out', 'ip_address')
    
    # Adds a filter sidebar on the right side
    list_filter = ('date', 'employee')
    
    # Adds a search bar at the top
    search_fields = ('employee__email', 'ip_address')
    
    # Attach our custom export button
    actions = [export_to_csv]