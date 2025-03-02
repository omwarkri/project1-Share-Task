from django.contrib import admin
from .models import (
    Task,
    PartnerFeedback,
    TaskCompletionDetails,
    Comment,
    SubTask,
    ActivityLog,
)

# Register Task model
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'status', 'priority', 'due_date', 'created_at',"reminder_sent","assigned_to")
    list_filter = ('status', 'priority', 'created_at')
    search_fields = ('title', 'description')
    filter_horizontal = ('allowed_users',)  # For easier management of ManyToManyField

# Register PartnerFeedback model
@admin.register(PartnerFeedback)
class PartnerFeedbackAdmin(admin.ModelAdmin):
    list_display = ('task', 'partner', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('task__title', 'partner__username')

# Register TaskCompletionDetails model
@admin.register(TaskCompletionDetails)
class TaskCompletionDetailsAdmin(admin.ModelAdmin):
    list_display = ('task', 'created_at')
    search_fields = ('task__title',)

# Register Comment model
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('task', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('task__title', 'user__username', 'text')

# Register SubTask model
@admin.register(SubTask)
class SubTaskAdmin(admin.ModelAdmin):
    list_display = ('task', 'title', 'completed')
    list_filter = ('completed',)
    search_fields = ('task__title', 'title')

# Register ActivityLog model
@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('task', 'user', 'action', 'timestamp')
    list_filter = ('action', 'timestamp')
    search_fields = ('task__title', 'user__username', 'details')


from django.contrib import admin
from .models import TeamScoreboard

@admin.register(TeamScoreboard)
class TeamScoreboardAdmin(admin.ModelAdmin):
    list_display = ('member', 'team', 'score')  # Display these fields in the admin list
    list_filter = ('team',)  # Add filtering by team
    search_fields = ('member__username', 'team__name')  # Enable search by member name or team name
    ordering = ('-score',)  # Order by highest score first
