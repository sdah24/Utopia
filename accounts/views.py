import random

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib import messages

from .forms import UserRegisterForm
from .models import Question

PASS_PERCENT = 60

def home(request):
    return render(request, 'home.html')

def quiz(request):
    if request.method == "GET":
        if "quiz_ids" not in request.session:
            all_ids = list(Question.objects.values_list("id", flat=True))
            if len(all_ids) < 5:
                # fallback: use all available
                chosen = all_ids
            else:
                chosen = random.sample(all_ids, 5)
            request.session["quiz_ids"] = chosen
        questions = Question.objects.filter(id__in=request.session["quiz_ids"])
        return render(request, "accounts/account_quiz.html", {"questions": questions})

    elif request.method == "POST":
        quiz_ids = request.session.get("quiz_ids", [])
        if not quiz_ids:
            messages.error(request, "Quiz session expired. Try again.")
            return redirect("quiz")

        total = len(quiz_ids)
        correct = 0
        for qid in quiz_ids:
            selected = request.POST.get(f"q{qid}")
            try:
                q = Question.objects.get(id=qid)
            except Question.DoesNotExist:
                continue
            if selected and selected.upper() == q.correct_option.upper():
                correct += 1

        percent = int((correct / total) * 100) if total else 0
        request.session["quiz_score"] = percent
        request.session.pop("quiz_ids", None)

        if percent >= PASS_PERCENT:
            messages.success(request, f"You passed ({percent}%). Proceed to registration.")
            return redirect("register")
        else:
            messages.error(request, f"You scored {percent}%. Minimum {PASS_PERCENT}% required.")
            return redirect("quiz")

def register(request):
        score = request.session.get("quiz_score")
        if score is None:
            messages.error(request, "You must complete the quiz before registering.")
            return redirect("quiz")

        if request.method == "POST":
            form = UserRegisterForm(request.POST)
            if form.is_valid():
                user = form.save()
                # profile is auto-created by signal learned this from internet
                profile = user.profile
                profile.quiz_score = score
                # badge logic that i will add later on html file
                if score >= 90:
                    profile.badge = "Gold"
                elif score >= 75:
                    profile.badge = "Silver"
                elif score >= 60:
                    profile.badge = "Bronze"
                else:
                    profile.badge = "No Badge"
                profile.save()
                login(request, user)
                request.session.pop("quiz_score", None)
                messages.success(request, "Registration successful — you are logged in.")
                return redirect("profile")
        else:
            form = UserRegisterForm()

        return render(request, "accounts/account_register.html", {"form": form, "score": score})

def login_view(request):
        if request.method == "POST":
            form = AuthenticationForm(request, data=request.POST)
            if form.is_valid():
                user = form.get_user()
                login(request, user)
                return redirect("profile")
        else:
            form = AuthenticationForm()
        return render(request, "accounts/account_login.html", {"form": form})

def logout_view(request):
        logout(request)
        messages.info(request, "Logged out.")
        return redirect("home")

@login_required
def profile(request):
    profile = request.user.profile  # via OneToOne relation
    return render(request, 'accounts/account_profile.html', {'profile': profile})