from django.db import models
from django.db.models import Model
from django.contrib.auth.models import User

# Create your models here.


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=150, blank=True)
    bio = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    quiz_score = models.IntegerField(null=True, blank=True)    # percent or raw
    badge = models.CharField(max_length=50, choices=[("Bronze","Bronze"),("Silver","Silver"),("Gold","Gold")], default="Bronze")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return self.user.username


class Question(models.Model):
    question_text = models.TextField()
    opt_a = models.CharField(max_length=240)
    opt_b = models.CharField(max_length=240)
    opt_c = models.CharField(max_length=240)
    opt_d = models.CharField(max_length=240)
    correct_option = models.CharField(max_length=1, choices=[
        ("A", "Option A"),
        ("B", "Option B"),
        ("C", "Option C"),
        ("D", "Option D"),
    ])

    def __str__(self):
        return self.question_text[:500]
