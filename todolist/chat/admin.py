from django.contrib import admin
from .models import Message

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'receiver', 'content', 'timestamp')
    search_fields = ('content', 'sender__username', 'receiver__username')
    list_filter = ('timestamp', 'sender', 'receiver')
    list_display_links = ('id', 'content')
    readonly_fields = ('timestamp',)

    # Grouping fields in the detailed view
    fieldsets = (
        (None, {
            'fields': ('sender', 'receiver', 'content')
        }),
        ('Timestamps', {
            'fields': ('timestamp',),
            'classes': ('collapse',),
        }),
    )
