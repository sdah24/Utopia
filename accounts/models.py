from django.db import models
from django.db.models import Model


# Create your models here.

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
