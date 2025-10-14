# posts/forms.py
from django import forms
from .models import Post, Comment
from django import forms
from .models import Question, Answer

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "content", "image", "is_emergency"]
        widgets = {
            "content": forms.Textarea(attrs={"rows":3, "placeholder":"What's happening?"}),
            "title": forms.TextInput(attrs={"placeholder":"Title (optional)"}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["body"]
        widgets = {
            "body": forms.Textarea(attrs={"rows":2, "placeholder":"Write a comment..."})
        }


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ["title", "body"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter your question title"}),
            "body": forms.Textarea(attrs={"class": "form-control", "placeholder": "Describe your question in detail"}),
        }

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ["body"]
        widgets = {
            "body": forms.Textarea(attrs={"class": "form-control", "placeholder": "Write your answer here"}),
        }