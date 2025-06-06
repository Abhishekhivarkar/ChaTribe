from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.db.models import Q, Prefetch
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.utils.decorators import method_decorator
from django.middleware.csrf import get_token

from .models import Post, Profile, Comment, Like, Reel, UserProfile
from .forms import (
    PostForm, 
    CommentForm, 
    RegisterForm, 
    ProfileImageForm, 
    LoginForm, 
    ReelForm
)

# Home
def home_view(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'home.html', {'posts': posts})

# Registration
@csrf_exempt
@csrf_protect
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful. You can now log in.')
            return redirect('login')
    else:
        form = UserCreationForm()
    print("DEBUG CSRF TOKEN:", get_token(request))
    return render(request, 'register.html', {'form': form})

# Feed
def feed_view(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'feed.html', {'posts': posts})

# Profile
@login_required
def profile_view(request, username):
    profile = get_object_or_404(Profile, user__username=username)
    posts = Post.objects.filter(author=profile.user).order_by('-created_at')
    
    post_form = PostForm()
    profile_form = ProfileImageForm(instance=profile)

    if request.method == 'POST':
        if 'image' in request.FILES:
            post_form = PostForm(request.POST, request.FILES)
            if post_form.is_valid():
                post = post_form.save(commit=False)
                post.author = request.user
                post.save()
                return redirect('profile', username=username)
        elif 'profile_image' in request.FILES:
            profile_form = ProfileImageForm(request.POST, request.FILES, instance=profile)
            if profile_form.is_valid():
                profile_form.save()
                return redirect('profile', username=username)

    return render(request, 'profile.html', {
        'profile': profile,
        'posts': posts,
        'form': post_form,
        'profile_form': profile_form
    })

# Post Detail
def post_detail_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = Comment.objects.filter(post=post).order_by('-created_at')
    liked = request.user.is_authenticated and Like.objects.filter(post=post, user=request.user).exists()

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.post = post
            new_comment.user = request.user
            new_comment.save()
            return redirect('post_detail', post_id=post.id)
    else:
        form = CommentForm()

    return render(request, 'post_detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': form,
        'liked': liked,
    })

# Upload Post
@login_required
def upload_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()
            return redirect('feed')
    else:
        form = PostForm()
    return render(request, 'upload_post.html', {'form': form})

# Like/Unlike a Post
@login_required
def toggle_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like_qs = Like.objects.filter(post=post, user=request.user)
    if like_qs.exists():
        like_qs.delete()
    else:
        Like.objects.create(post=post, user=request.user)
    return redirect('post_detail', post_id=post.id)

@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    return redirect(request.META.get('HTTP_REFERER', 'home'))

# Login
class CustomLoginView(LoginView):
    template_name = 'login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('feed')

# User Search
def user_search_view(request):
    query = request.GET.get('q', '')
    users = User.objects.filter(
        Q(username__icontains=query) |
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query)
    ) if query else []
    return render(request, 'user_search_results.html', {'query': query, 'users': users})

# Follow/Unfollow User
@login_required
def follow_user(request, username):
    if request.method == 'POST':
        try:
            user_to_follow = User.objects.get(username=username)
            profile_to_follow = user_to_follow.profile
            current_profile = request.user.profile

            is_following = current_profile not in profile_to_follow.followers.all()
            if is_following:
                profile_to_follow.followers.add(current_profile)
            else:
                profile_to_follow.followers.remove(current_profile)

            return JsonResponse({
                'success': True,
                'is_following': is_following,
                'followers_count': profile_to_follow.followers.count()
            })

        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'User not found'})
        except UserProfile.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'UserProfile not found'})

    return JsonResponse({'success': False, 'error': 'Invalid request'})

# Signals
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

# Reels
@login_required
def upload_reel(request):
    if request.method == 'POST':
        form = ReelForm(request.POST, request.FILES)
        if form.is_valid():
            reel = form.save(commit=False)
            reel.user = request.user
            reel.save()
            return redirect('reels_feed')
    else:
        form = ReelForm()
    return render(request, 'upload_reel.html', {'form': form})

def reels_feed(request):
    reels = Reel.objects.all().order_by('-created_at')
    return render(request, 'reels_feed.html', {'reels': reels})
