from django.contrib import admin
from .models import Post, Comment, Like, Follow, Question, Answer

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



@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "user", "created_at")
    search_fields = ("title", "body", "user__username")


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("id", "question", "user", "created_at")
    search_fields = ("body", "user__username")
