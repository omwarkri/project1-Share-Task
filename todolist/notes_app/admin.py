# admin.py
from django.contrib import admin
from .models import TaskNotes  # Import your TaskNotes model

# Define the admin class for TaskNotes
class TaskNotesAdmin(admin.ModelAdmin):
    # Specify the fields to display in the admin list view
    list_display = ('task', 'user', 'note_text', 'created_at')
    
    # Add filters for the list view
    list_filter = ('task', 'user', 'created_at')
    
    # Add search functionality
    search_fields = ('note_text', 'task__title', 'user__username')
    
    # Make the created_at field read-only
    readonly_fields = ('created_at',)

# Register the TaskNotes model with the admin site
admin.site.register(TaskNotes, TaskNotesAdmin)