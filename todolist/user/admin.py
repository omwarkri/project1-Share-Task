from django.contrib import admin
from .models import CustomUser, UserActivity, Badge, UserBadge

# Customize the display for CustomUser
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'phone_number', 'score',   'onboarding_completed')
    search_fields = ('username', 'email', 'phone_number')
    list_filter = ('is_staff', 'is_active')

# Customize the display for UserActivity
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'activity_date')
    search_fields = ('user__username', 'activity_type')
    list_filter = ('activity_date',)

# Customize the display for Badge
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'min_score')
    search_fields = ('name',)
    list_filter = ('min_score',)

# Customize the display for UserBadge
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ('user', 'badge', 'awarded_at')
    search_fields = ('user__username', 'badge__name')
    list_filter = ('awarded_at',)

# Register models with admin site
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(UserActivity, UserActivityAdmin)
admin.site.register(Badge, BadgeAdmin)
admin.site.register(UserBadge, UserBadgeAdmin)


# admin.py

from django.contrib import admin
from .models import ChallengeTemplate, DailyChallenge, UserChallenge

@admin.register(ChallengeTemplate)
class ChallengeTemplateAdmin(admin.ModelAdmin):
    list_display = ('title', 'challenge_type', 'target', 'xp_reward')
    list_filter = ('challenge_type',)
    search_fields = ('title', 'description')


@admin.register(DailyChallenge)
class DailyChallengeAdmin(admin.ModelAdmin):
    list_display = ('template', 'date')
    list_filter = ('date',)
    search_fields = ('template__title',)


@admin.register(UserChallenge)
class UserChallengeAdmin(admin.ModelAdmin):
    list_display = ('user', 'daily_challenge', 'accepted', 'completed', 'progress')
    list_filter = ('accepted', 'completed')
    search_fields = ('user__username', 'daily_challenge__template__title')


from .models import UserTaskAnalytics
@admin.register(UserTaskAnalytics)
class UserTaskAnalyticsAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'total_tasks',
        'completed_tasks',
        'overdue_tasks',
        'average_completion_time',
        'most_common_category',
        'last_updated'
    )
    search_fields = ('user__username', 'most_common_category')
    list_filter = ('last_updated',)


from django.contrib import admin
from .models import Schedule

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'start_time', 'end_time', 'task', 'completed')
    list_filter = ('date', 'completed', 'user')
    search_fields = ('task__title', 'user__username')
    ordering = ('date', 'start_time')
