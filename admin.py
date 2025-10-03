from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserProfile, Club, Announcement, ClubHeadRequest, JoinRequest

# Register CustomUser model with a custom admin
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email')
    ordering = ('-date_joined',)

# Register CustomUser model
admin.site.register(CustomUser, CustomUserAdmin)

# Register UserProfile model
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio', 'profile_picture')
    search_fields = ('user__username', 'bio')
    ordering = ('-created_at',)

# Register Club model with customizations
@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('-created_at',)

# Register Announcement model with customization
@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'club', 'posted_by', 'created_at', 'updated_at')
    search_fields = ('title', 'content', 'club__name', 'posted_by__username')  # Allows searching by title, club name, or username
    list_filter = ('club', 'posted_by', 'created_at')  # Filters for sorting by club, poster, and date
    ordering = ('-created_at',)  # Orders announcements by creation date (latest first)

# Register ClubHeadRequest model with actions
@admin.register(ClubHeadRequest)
class ClubHeadRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'club_name', 'status', 'created_at')
    actions = ['approve_requests', 'reject_requests']

    def approve_requests(self, request, queryset):
        for obj in queryset:
            obj.status = 'approved'
            obj.user.role = 'club_head'  # Set the user's role
            obj.user.save()
            obj.save()
        self.message_user(request, "Selected requests approved.")
    
    def reject_requests(self, request, queryset):
        queryset.update(status='rejected')
        self.message_user(request, "Selected requests rejected.")

@admin.register(JoinRequest)
class JoinRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'club', 'status', 'requested_at')
    actions = ['approve_requests', 'reject_requests']

    def approve_requests(self, request, queryset):
        for obj in queryset:
            # Approve the join request
            obj.status = 'approved'
            obj.save()

            # Add the user to the club's members
            club = obj.club
            user = obj.user

            # Add the user to the club's members if not already added
            if user not in club.members.all():
                club.members.add(user)

            # Optionally set a role for the user
            user.role = 'member'  # Set a role, if you need to
            user.save()

            # Notify admin
            self.message_user(request, f"User {user.username} has been approved and added to {club.name}.")

    def reject_requests(self, request, queryset):
        queryset.update(status='rejected')
        self.message_user(request, "Selected requests rejected.")
