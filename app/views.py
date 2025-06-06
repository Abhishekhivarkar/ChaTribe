# from cProfile import Profile
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from .forms import PostForm
from .models import Post, Profile
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from .models import Like, Profile, Post 
from .models import Post, Comment, Profile
from .forms import PostForm, CommentForm, RegisterForm, ProfileImageForm
from django.contrib.auth.views import LoginView
from .forms import LoginForm
from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models.signals import post_save
from .models import UserProfile
from django.dispatch import receiver
from .models import Post

def home_view(request):
    posts = Post.objects.all().order_by('-created_at')  
    return render(request, 'home.html', {'posts': posts})




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

def feed_view(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request,'feed.html', {'posts': posts})

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


from django.shortcuts import render, redirect, get_object_or_404
from .forms import PostForm
from .models import Post, Profile
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required


from django.db.models import Prefetch

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




def post_detail_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = Comment.objects.filter(post=post).order_by('-created_at')
    liked = False
    if request.user.is_authenticated:
        liked = Like.objects.filter(post=post, user=request.user).exists()

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
# Create your views here.



@login_required
def toggle_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user

    like_qs = Like.objects.filter(post=post, user=user)
    if like_qs.exists():
        # Unlike
        like_qs.delete()
    else:
        # Like
        Like.objects.create(post=post, user=user)

    return redirect('post_detail', post_id=post.id)


from django.contrib.auth.views import LoginView
from .forms import LoginForm

class CustomLoginView(LoginView):
    template_name = 'login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('feed')

from django.db.models import Q
def user_search_view(request):
    query = request.GET.get('q', '')
    users = []

    if query:
        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )

    context = {
        'query': query,
        'users': users,
    }
    return render(request, 'user_search_results.html', context)

@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user

    if user in post.likes.all():
        post.likes.remove(user)
    else:
        post.likes.add(user)

    return redirect(request.META.get('HTTP_REFERER', 'home'))



from django.contrib.auth.models import User

@login_required
def follow_user(request, username):
    if request.method == 'POST':
        try:
            user_to_follow = User.objects.get(username=username)
            profile_to_follow = user_to_follow.profile 
            current_profile = request.user.profile

            if current_profile in profile_to_follow.followers.all():
                profile_to_follow.followers.remove(current_profile)
                is_following = False
            else:
                profile_to_follow.followers.add(current_profile)
                is_following = True

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


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)



from .forms import ReelForm
from .models import Reel

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

from .models import Reel 

def reels_feed(request):
    reels = Reel.objects.all().order_by('-created_at')
    return render(request, 'reels_feed.html', {'reels': reels})
