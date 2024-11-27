from django.contrib import admin
from .models import County, Bill, Comment, UserProfile, Notification

# Register your models here.

@admin.register(County)
class CountyAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'governor', 'created_at')
    search_fields = ('name', 'code', 'governor')
    list_filter = ('created_at',)

@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ('title', 'county', 'status', 'public_participation_deadline', 'created_at')
    list_filter = ('status', 'county', 'created_at')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'bill', 'created_at', 'is_approved')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('user__username', 'content', 'bill__title')
    actions = ['approve_comments']

    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)
    approve_comments.short_description = "Approve selected comments"

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'county', 'is_county_admin', 'created_at')
    list_filter = ('is_county_admin', 'county', 'created_at')
    search_fields = ('user__username', 'bio', 'phone_number')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'title', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__username', 'title', 'message')
