from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'user', 'created_at')  # Ensure 'user' is a field or method on Task
    list_filter = ('status', 'user')  # Make sure 'user' is a valid filter field
    search_fields = ('title', 'user__username')  # Use '__' to search through related fields like ForeignKey
