# posts/models.py
from django.db import models
from django.utils import timezone

# Use string reference to avoid circular import problems
# 'accounts.Profile' is the model that must exist in accounts app

class Post(models.Model):
    profile = models.ForeignKey("accounts.Profile", on_delete=models.CASCADE, related_name="posts")
    title = models.CharField(max_length=200, blank=True)
    content = models.TextField(blank=True)
    image = models.ImageField(upload_to="posts/", blank=True, null=True)
    is_emergency = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    likes_count = models.IntegerField(default=0)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Post {self.pk} by {self.profile.user.username}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    profile = models.ForeignKey("accounts.Profile", on_delete=models.CASCADE, null=True, blank=True)
    body = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment {self.pk} on Post {self.post.pk}"


class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    profile = models.ForeignKey("accounts.Profile", on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("post", "profile")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.profile.user.username} likes Post {self.post_id}"


class Follow(models.Model):
    follower = models.ForeignKey("accounts.Profile", on_delete=models.CASCADE, related_name="following_set")
    following = models.ForeignKey("accounts.Profile", on_delete=models.CASCADE, related_name="followers_set")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("follower", "following")

    def __str__(self):
        return f"{self.follower.user.username} -> {self.following.user.username}"

# posts/models.py
from django.db import models
from django.contrib.auth.models import User

class Question(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Answer by {self.user.username}"

