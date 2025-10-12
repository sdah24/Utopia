from django.contrib import admin
from .models import FundMePost, Donation

@admin.register(FundMePost)
class FundMePostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "goal_amount", "collected_amount", "is_active", "created_at")
    search_fields = ("title", "author__username")

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ("fundme", "donor", "amount", "donated_at")

