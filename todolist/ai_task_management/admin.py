from django.contrib import admin
from .models import Microtask

@admin.register(Microtask)
class MicrotaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'task', 'subtask', 'completed')
    list_filter = ('completed', 'task', 'subtask')  # Optional: Add filters on the side
    search_fields = ('title',)  # Optional: Add search bar for title
