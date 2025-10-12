from django import forms
from .models import FundMePost, Donation

class FundMePostForm(forms.ModelForm):
    class Meta:
        model = FundMePost
        fields = ["title", "description", "goal_amount", "image"]


class DonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = ["amount", "note"]
