import random
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Question

PASS_PERCENT = 60  # adjust

def quiz(request):
    if request.method == "GET":
        # pick 5 random ids and store in session (locked for this session)
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

    # POST: grade
    elif request.method == "POST":
        quiz_ids = request.session.get("quiz_ids", [])
        if not quiz_ids:
            messages.error(request, "Quiz session expired. Try again.")
            return redirect("quiz")

        total = len(quiz_ids)
        correct = 0
        for qid in quiz_ids:
            selected = request.POST.get(f"q{qid}")   # template uses name="q{{ q.id }}"
            try:
                q = Question.objects.get(id=qid)
            except Question.DoesNotExist:
                continue
            if selected and selected.upper() == q.correct.upper():
                correct += 1

        percent = int((correct / total) * 100) if total else 0
        request.session["quiz_score"] = percent
        # optional: clear quiz_ids to force new quiz next time
        request.session.pop("quiz_ids", None)

        if percent >= PASS_PERCENT:
            messages.success(request, f"You passed ({percent}%). Proceed to registration.")
            return redirect("register")
        else:
            messages.error(request, f"You scored {percent}%. Minimum {PASS_PERCENT}% required.")
            return redirect("quiz")