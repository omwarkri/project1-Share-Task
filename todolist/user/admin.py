from django.contrib import admin
from .models import CustomUser, UserActivity, Badge, UserBadge

# Customize the display for CustomUser
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'phone_number', 'score')
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
