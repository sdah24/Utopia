from django.shortcuts import render
from .models import Question
# Create your views here.

def questions(request):
    q = Question.objects.order_by('?')[:5]
    return render(request,'account_quiz.html',{"questions":q})