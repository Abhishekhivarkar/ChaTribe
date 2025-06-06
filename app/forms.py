from .models import Profile
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Post, Comment
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.csrf import csrf_protect
# Use this RegisterForm based on UserCreationForm (recommended)
class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

# Post form
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['caption', 'image']

# Comment form
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'
    }))


class ProfileImageForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_image']

from .models import Reel

class ReelForm(forms.ModelForm):
    class Meta:
        model = Reel
        fields = ['video', 'caption']
