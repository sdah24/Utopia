# posts/views.py

from django.db import transaction
from django.db.models import F
from django.contrib import messages
from django.urls import reverse
from .models import Post, Comment, Like, Follow
from .forms import PostForm, CommentForm
from accounts.models import Profile

from posts.models import Post
from funding.models import FundMePost
from accounts.models import Question

from django.db.models import Q
from posts.models import Post
from funding.models import FundMePost
from django.contrib.auth.models import User


from accounts.models import Profile
from .forms import QuestionForm, AnswerForm
from .models import Question, Answer
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404


#This view was really very hard to implement so I had to take help and understand things that I wasnt familiar with
#I thought adding some comments would help me to remember things better when I look onto my codes again


# This is basically a Helper function to get request.user.profile safely
def _get_profile(request):
    # here i am ensuring profile exists by taking attribute
    return getattr(request.user, "profile", None)

@login_required
def feed(request):
    profile = _get_profile(request)
    # this is for posts from profiles the user follows + own posts
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
    post = get_object_or_404(Post, id=post_id, profile__user=request.user)
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Post updated successfully!")
            return redirect("posts:detail", post_id=post.id)
    else:
        form = PostForm(instance=post)
    return render(request, "posts/post_form.html", {"form": form, "is_edit": True})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, profile__user=request.user)
    if request.method == "POST":
        post.delete()
        messages.success(request, "Post deleted successfully!")
        return redirect("posts:feed")
    return render(request, "posts/post_confirm_delete.html", {"post": post})


def emergency_feed(request):
    posts = Post.objects.filter(is_emergency=True).select_related("profile__user")
    return render(request, "posts/emergency_feed.html", {"posts": posts})



@login_required
def people_list(request):
    profile = request.user.profile

    people = Profile.objects.exclude(id=profile.id)

    following_ids = Follow.objects.filter(follower=profile).values_list("following_id", flat=True)

    return render(request, "posts/people_list.html", {
        "people": people,
        "following_ids": set(following_ids)
    })


@login_required
def question_list(request):
    questions = Question.objects.all().order_by("-created_at")
    return render(request, "posts/question_list.html", {"questions": questions})

@login_required
def ask_question(request):
    if request.method == "POST":
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.user = request.user
            question.save()
            return redirect("posts:question_list")
    else:
        form = QuestionForm()
    return render(request, "posts/ask_question.html", {"form": form})

@login_required
def question_detail(request, pk):
    question = get_object_or_404(Question, pk=pk)
    answers = Answer.objects.filter(question=question)
    if request.method == "POST":
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.user = request.user
            answer.question = question
            answer.save()
            return redirect("posts:question_detail", pk=pk)
    else:
        form = AnswerForm()
    return render(request, "posts/question_detail.html", {"question": question, "answers": answers, "form": form})


#added search feature for most of my contents including posts,question etc
def search_view(request):
    query = request.GET.get('q')
    post_results = []
    fundme_results = []
    user_results = []
    question_results = []
    answer_results = []

    if query:
        post_results = Post.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )
        fundme_results = FundMePost.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
        user_results = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )
        question_results = Question.objects.filter(
            Q(title__icontains=query) | Q(body__icontains=query)
        )
        answer_results = Answer.objects.filter(
            Q(body__icontains=query)
        )

    context = {
        'query': query,
        'post_results': post_results,
        'fundme_results': fundme_results,
        'user_results': user_results,
        'question_results': question_results,
        'answer_results': answer_results,
    }
    return render(request, 'posts/search_results.html', context)
