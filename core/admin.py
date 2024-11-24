from django.contrib import admin
from .models import County, Bill, Comment, Vote

# Register your models here.

@admin.register(County)
class CountyAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)

@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ('title', 'county', 'status', 'deadline', 'created_at')
    list_filter = ('status', 'county', 'created_at')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'bill', 'created_at')
    list_filter = ('created_at', 'bill')
    search_fields = ('content', 'user__username', 'bill__title')

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'bill', 'choice', 'created_at')
    list_filter = ('choice', 'created_at', 'bill')
    search_fields = ('user__username', 'bill__title')
