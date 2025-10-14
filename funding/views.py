from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import FundMePost, Donation
from .forms import FundMePostForm, DonationForm

def fundme_list(request):
    posts = FundMePost.objects.filter(is_active=True).order_by("-created_at")
    return render(request, "funding/fundme_list.html", {"posts": posts})


def fundme_detail(request, pk):
    post = get_object_or_404(FundMePost, pk=pk)
    donations = post.donations.all()
    if request.method == "POST":
        if request.user.is_authenticated:
            form = DonationForm(request.POST)
            if form.is_valid():
                donation = form.save(commit=False)
                donation.donor = request.user
                donation.fundme = post
                donation.save()
                messages.success(request, "Donation successful! 🎉")
                return redirect("funding:fundme_detail", pk=pk)
        else:
            messages.error(request, "You must be logged in to donate.")
            return redirect("login")
    else:
        form = DonationForm()
    return render(request, "funding/fundme_detail.html", {"post": post, "form": form, "donations": donations})


@login_required
def fundme_create(request):
    if request.method == "POST":
        form = FundMePostForm(request.POST, request.FILES)
        if form.is_valid():
            fundme = form.save(commit=False)
            fundme.author = request.user
            fundme.save()
            messages.success(request, "Your FundMe post has been created! 💰")
            return redirect("funding:fundme_list")
    else:
        form = FundMePostForm()
    return render(request, "funding/fundme_form.html", {"form": form, "title": "Create FundMe"})


@login_required
def fundme_update(request, pk):
    post = get_object_or_404(FundMePost, pk=pk, author=request.user)
    if request.method == "POST":
        form = FundMePostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Your FundMe post has been updated.")
            return redirect("fundme_detail", pk=pk)
    else:
        form = FundMePostForm(instance=post)
    return render(request, "funding/fundme_form.html", {"form": form, "title": "Edit FundMe"})


@login_required
def fundme_delete(request, pk):
    post = get_object_or_404(FundMePost, pk=pk, author=request.user)
    if request.method == "POST":
        post.delete()
        messages.success(request, "Your FundMe post has been deleted.")
        return redirect("funding:fundme_list")
    return render(request, "funding/fundme_confirm_delete.html", {"post": post})
