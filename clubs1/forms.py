from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, UserProfile, Announcement, Event


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ("username", "first_name", "last_name", "email")


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ("contact", "bio", "profile_picture")


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ["title", "content", "image", "video"]


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ["title", "description", "date", "time", "location"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "time": forms.TimeInput(attrs={"type": "time"}),
        }
