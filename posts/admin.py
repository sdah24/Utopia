# posts/admin.py
from django.contrib import admin
from .models import Post, Comment, Like, Follow

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "profile", "created_at", "likes_count")
    search_fields = ("content", "profile__user__username")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "post", "profile", "created_at")
    search_fields = ("body", "profile__user__username")


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("id", "post", "profile", "created_at")


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ("id", "follower", "following", "created_at")
