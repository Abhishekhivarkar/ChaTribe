from django.contrib import admin
from .models import Profile, Post,Like, Comment,UserProfile

admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(Like)
admin.site.register(Comment)
admin.site.register(UserProfile)
# Register your models here.
