from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Profile
from .forms import ProfileForm, UserForm

@login_required
def profile_view(request):
    """View for user's own profile."""
    profile = request.user.profile
    context = {
        'profile': profile,
        'user': request.user,
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def profile_edit(request):
    """View for editing user profile."""
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('accounts:profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'accounts/profile_edit.html', context)

def public_profile_view(request, username):
    """View for public profile of a user."""
    user = get_object_or_404(User, username=username)
    profile = user.profile
    
    # Get user's published posts
    posts = user.blog_posts.filter(status='published').order_by('-published_at')[:5]
    
    context = {
        'profile_user': user,
        'profile': profile,
        'posts': posts,
    }
    return render(request, 'accounts/public_profile.html', context)

@login_required
def dashboard_view(request):
    """View for user dashboard."""
    # Get user's posts
    posts = request.user.blog_posts.all().order_by('-created_at')
    
    # Get user's comments
    comments = request.user.comments.all().order_by('-created_at')
    
    context = {
        'posts': posts,
        'comments': comments,
    }
    return render(request, 'accounts/dashboard.html', context)
