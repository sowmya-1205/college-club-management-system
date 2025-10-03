from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone


class CustomUser(AbstractUser):
    def __str__(self) -> str:
        return self.username


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    contact = models.CharField(max_length=15, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to="profile_pictures/", default="profile_pictures/default.jpg", blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return f"{self.user.username}'s Profile"


class Club(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    image = models.ImageField(upload_to="club_images/", blank=True, null=True)
    faculty_coordinator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="coordinated_clubs")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, through="ClubMembership", related_name="clubs")

    def __str__(self) -> str:
        return self.name

    def get_club_admins(self):
        return self.members.filter(clubmembership__role="admin")


class ClubMembership(models.Model):
    ROLE_CHOICES = [
        ("member", "Member"),
        ("admin", "Club Admin"),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="member")
    join_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "club")

    def __str__(self) -> str:
        return f"{self.user.username} in {self.club.name} as {self.get_role_display()}"


class Announcement(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    image = models.ImageField(upload_to="announcement_images/", blank=True, null=True)
    video = models.URLField(blank=True, null=True)
    club = models.ForeignKey(Club, related_name="announcements", on_delete=models.CASCADE)
    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="posted_announcements", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title


class Event(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=200)
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="events")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.title} by {self.club.name}"


class JoinRequest(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="join_requests")
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="join_requests")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    requested_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "club")

    def __str__(self) -> str:
        return f"Request from {self.user.username} to join {self.club.name}"


class ClubHeadRequest(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    club_name = models.CharField(max_length=100)
    club_description = models.TextField()
    message = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Club head request for '{self.club_name}' by {self.user.username}"
