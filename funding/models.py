from django.db import models
from django.conf import settings
from django.utils import timezone

User = settings.AUTH_USER_MODEL


class FundMePost(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="fundme_posts")
    title = models.CharField(max_length=255)
    description = models.TextField()
    goal_amount = models.DecimalField(max_digits=12, decimal_places=2)
    collected_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    image = models.ImageField(upload_to="funding_images/", blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    def progress_percent(self):
        if self.goal_amount > 0:
            return round((self.collected_amount / self.goal_amount) * 100, 2)
        return 0


class Donation(models.Model):
    fundme = models.ForeignKey(FundMePost, on_delete=models.CASCADE, related_name="donations")
    donor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    note = models.TextField(blank=True)
    donated_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        total = self.fundme.donations.aggregate(models.Sum("amount"))["amount__sum"] or 0
        self.fundme.collected_amount = total
        self.fundme.save()

    def __str__(self):
        donor_name = self.donor.username if self.donor else "Anonymous"
        return f"{donor_name} donated {self.amount}"
