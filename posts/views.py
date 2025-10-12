# posts/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F
from django.contrib import messages
from django.urls import reverse
from .models import Post, Comment, Like, Follow
from .forms import PostForm, CommentForm

# Helper: get request.user.profile safely
def _get_profile(request):
    # If your Profile auto-creation is not set, ensure profile exists
    return getattr(request.user, "profile", None)

@login_required
def feed(request):
    profile = _get_profile(request)
    # posts from profiles the user follows + own posts
    following_ids = list(Follow.objects.filter(follower=profile).values_list("following_id", flat=True)) if profile else []
    posts = Post.objects.filter(profile__id__in=following_ids + ([profile.id] if profile else [])).select_related("profile__user").prefetch_related("comments")[:100]
    # liked posts ids for this user
    liked_post_ids = set()
    if profile:
        liked_post_ids = set(Like.objects.filter(profile=profile, post__in=posts).values_list("post_id", flat=True))
    return render(request, "posts/feed.html", {"posts": posts, "liked_post_ids": liked_post_ids})

@login_required
def create_post(request):
    profile = _get_profile(request)
    if profile is None:
        messages.error(request, "Profile missing. Contact admin.")
        return redirect("posts:feed")

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            p = form.save(commit=False)
            p.profile = profile
            p.save()
            messages.success(request, "Post created.")
            return redirect("posts:feed")
    else:
        form = PostForm()
    return render(request, "posts/post_form.html", {"form": form})

def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comment_form = CommentForm()
    user_liked = False
    if request.user.is_authenticated and getattr(request.user, "profile", None):
        user_liked = Like.objects.filter(post=post, profile=request.user.profile).exists()
    return render(request, "posts/post_detail.html", {"post": post, "comment_form": comment_form, "user_liked": user_liked})

@login_required
def add_comment(request, post_id):
    profile = _get_profile(request)
    if profile is None:
        messages.error(request, "Profile missing.")
        return redirect("posts:detail", post_id=post_id)

    post = get_object_or_404(Post, pk=post_id)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            c = form.save(commit=False)
            c.post = post
            c.profile = profile
            c.save()
            messages.success(request, "Comment added.")
    return redirect("posts:detail", post_id=post_id)

@login_required
@transaction.atomic
def toggle_like(request, post_id):
    profile = _get_profile(request)
    if profile is None:
        messages.error(request, "Profile missing.")
        return redirect("posts:detail", post_id=post_id)

    post = get_object_or_404(Post, pk=post_id)
    like, created = Like.objects.get_or_create(post=post, profile=profile)
    if created:
        Post.objects.filter(pk=post.pk).update(likes_count=F("likes_count") + 1)
    else:
        like.delete()
        Post.objects.filter(pk=post.pk).update(likes_count=F("likes_count") - 1)
    return redirect(request.META.get("HTTP_REFERER", reverse("posts:feed")))

@login_required
def toggle_follow(request, profile_id):
    profile = _get_profile(request)
    target_profile = get_object_or_404(request.user.__class__.objects.model._meta.apps.get_model("accounts", "Profile"), pk=profile_id)
    # simpler: get target_profile = get_object_or_404(Profile, pk=profile_id)
    # But to avoid circular import, you can import accounts.Profile inside function if needed
    from accounts.models import Profile
    target_profile = get_object_or_404(Profile, pk=profile_id)

    if target_profile == profile:
        messages.error(request, "You cannot follow yourself.")
        return redirect("posts:profile_posts", profile_id=profile_id)

    follow, created = Follow.objects.get_or_create(follower=profile, following=target_profile)
    if not created:
        follow.delete()
        messages.info(request, f"You unfollowed {target_profile.user.username}.")
    else:
        messages.success(request, f"You followed {target_profile.user.username}.")
    return redirect("posts:profile_posts", profile_id=profile_id)

def profile_posts(request, profile_id):
    from accounts.models import Profile
    profile_user = get_object_or_404(Profile, pk=profile_id)
    posts = profile_user.posts.all().select_related("profile__user").prefetch_related("comments")
    is_following = False
    if request.user.is_authenticated and getattr(request.user, "profile", None):
        is_following = Follow.objects.filter(follower=request.user.profile, following=profile_user).exists()
    followers_count = Follow.objects.filter(following=profile_user).count()
    following_count = Follow.objects.filter(follower=profile_user).count()
    return render(request, "posts/profile_posts.html", {
        "profile_user": profile_user,
        "posts": posts,
        "is_following": is_following,
        "followers_count": followers_count,
        "following_count": following_count,
    })
@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id, profile=request.user.profile)
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Post updated successfully.")
            return redirect("posts:detail", post_id=post_id)
    else:
        form = PostForm(instance=post)
    return render(request, "posts/post_form.html", {"form": form, "edit_mode": True})

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id, profile=request.user.profile)
    if request.method == "POST":
        post.delete()
        messages.success(request, "Post deleted.")
        return redirect("posts:feed")
    return render(request, "posts/post_confirm_delete.html", {"post": post})
