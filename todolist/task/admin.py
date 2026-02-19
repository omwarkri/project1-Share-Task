from django.contrib import admin
from .models import (
    Task,
    PartnerFeedback,
    TaskCompletionDetails,
    Comment,
    SubTask,
    ActivityLog,
    TeamInvitation,
    Team
)

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("name", "created_by", "created_at")  # Fields to show in list view
    search_fields = ("name", "created_by__email")  # Enable search by name or creator's email
    list_filter = ("created_at",)  # Add filter options
    ordering = ("-created_at",)  # Order teams by newest first
    filter_horizontal = ("members",)  # Better UI for many-to-many field
    readonly_fields = ("created_at",)  # Make created_at non-editable
    raw_id_fields = ("created_by",)  # Optimize foreign key lookup for large user tables

# Register Task model
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'user',
        'status',
        'priority',
        'due_date',
        'created_at',
        'reminder_sent',
        'assigned_to',
    )
    list_filter = ('status', 'priority', 'created_at','user')
    search_fields = ('title', 'description')
    filter_horizontal = ('allowed_users',)

    # Add ordering support
    ordering = ('-created_at',)  # default ordering in admin panel
    sortable_by = ('created_at', 'due_date', 'priority', 'last_visited_at')  # allow these to be sorted

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
    list_display = ('id','task', 'title', 'completed')
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

@admin.register(TeamInvitation)
class TeamInvitationAdmin(admin.ModelAdmin):
    list_display = ('team', 'email', 'invited_by','invited_user')  # Display these fields in the admin list




