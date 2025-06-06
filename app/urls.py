from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('feed/', views.feed_view, name='feed'),
    path('register/', views.register_view, name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='logout.html', next_page='login'), name='logout'),
    path('search/', views.user_search_view, name='user_search'),
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('post/<int:post_id>/', views.post_detail_view, name='post_detail'),
    path('upload/', views.upload_post, name='upload_post'),
    path('post/<int:post_id>/like/', views.toggle_like, name='toggle_like'),
    path('like/<int:post_id>/', views.like_post, name='like_post'),
    path('follow/<str:username>/', views.follow_user, name='follow_user'),
    path('reels/upload/', views.upload_reel, name='upload_reel'),
    path('reels/', views.reels_feed, name='reels_feed'),


]
