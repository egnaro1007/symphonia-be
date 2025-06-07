from django.contrib import admin

from .models import UserProfile, FriendRequest, Friendship

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__username', 'user__email')

@admin.register(FriendRequest)
class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('sender__username', 'receiver__username')

@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ('user1', 'user2', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user1__username', 'user2__username')
