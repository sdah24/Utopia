import random
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import UserRegisterForm
from .models import Question


from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ProfilePictureForm



PASS_PERCENT = 60

def home(request):
    return render(request, 'home.html')

def quiz(request):
    if request.method == "GET":
        if "quiz_ids" not in request.session:
            all_ids = list(Question.objects.values_list("id", flat=True))
            chosen = random.sample(all_ids, min(5, len(all_ids)))
            request.session["quiz_ids"] = chosen
        questions = Question.objects.filter(id__in=request.session["quiz_ids"])
        return render(request, "accounts/account_quiz.html", {"questions": questions})

    elif request.method == "POST":
        quiz_ids = request.session.get("quiz_ids", [])
        total = len(quiz_ids)
        correct = 0
        for qid in quiz_ids:
            selected = request.POST.get(f"q{qid}")
            q = Question.objects.get(id=qid)
            if selected and selected.upper() == q.correct_option.upper():
                correct += 1

        percent = int((correct / total) * 100) if total else 0
        request.session["quiz_score"] = percent
        request.session.pop("quiz_ids", None)

        if percent >= PASS_PERCENT:
            messages.success(request, f"You passed ({percent}%). Proceed to registration.")
            return redirect("accounts:register")
        else:
            messages.error(request, f"You scored {percent}%. Minimum {PASS_PERCENT}% required.")
            return redirect("accounts:quiz")

def register(request):
    score = request.session.get("quiz_score")
    if score is None:
        messages.error(request, "You must complete the quiz before registering.")
        return redirect("accounts:quiz")

    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            profile = user.profile
            profile.quiz_score = score
            if score >= 90:
                profile.badge = "Gold"
            elif score >= 75:
                profile.badge = "Silver"
            elif score >= 60:
                profile.badge = "Bronze"
            profile.save()
            login(request, user)
            request.session.pop("quiz_score", None)
            messages.success(request, "Registration successful — you are logged in.")
            return redirect("accounts:profile")
    else:
        form = UserRegisterForm()

    return render(request, "accounts/account_register.html", {"form": form, "score": score})

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("accounts:profile")
    else:
        form = AuthenticationForm()
    return render(request, "accounts/account_login.html", {"form": form})

def logout_view(request):
    logout(request)
    messages.info(request, "Logged out.")
    return redirect("home")






@login_required
def profile(request):
    # If ?user=username is passed in URL, view that user’s profile instead
    username = request.GET.get('user')

    if username and username != request.user.username:
        # View someone else’s profile (read-only)
        user = get_object_or_404(User, username=username)
        profile = user.profile
        editable = False
    else:
        # View your own profile (editable)
        user = request.user
        profile = user.profile
        editable = True

    if editable and request.method == "POST":
        form = ProfilePictureForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            if 'profile_picture-clear' in request.POST:
                if profile.profile_picture:
                    profile.profile_picture.delete(save=False)
                profile.profile_picture = None

            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('accounts:profile')
    else:
        form = ProfilePictureForm(instance=profile)

    return render(request, 'accounts/account_profile.html', {
        'form': form,
        'profile': profile,
        'editable': editable,  # ✅ Pass to template to hide edit form for others
        'user_viewed': user,
    })


@login_required
def people_list(request):
    from .models import Profile
    # Get all profiles except the current user's profile
    people = Profile.objects.exclude(user=request.user)

    # Get IDs of people the user is following (optional if you have a follow model)
    following_ids = []
    if hasattr(request.user, 'following'):
        following_ids = request.user.following.values_list('id', flat=True)

    return render(request, 'accounts/people_list.html', {
        'people': people,
        'following_ids': following_ids,
    })
