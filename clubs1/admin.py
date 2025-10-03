from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserProfile, Club, Announcement, ClubHeadRequest, JoinRequest, ClubMembership


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("username", "email", "first_name", "last_name", "is_staff", "is_active", "date_joined")
    search_fields = ("username", "email")
    ordering = ("-date_joined",)


admin.site.register(CustomUser, CustomUserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "bio", "profile_picture")
    search_fields = ("user__username", "bio")
    ordering = ("-created_at",)


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "created_at")
    search_fields = ("name", "description")
    ordering = ("-created_at",)


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ("title", "club", "posted_by", "created_at", "updated_at")
    search_fields = ("title", "content", "club__name", "posted_by__username")
    list_filter = ("club", "posted_by", "created_at")
    ordering = ("-created_at",)


@admin.register(ClubHeadRequest)
class ClubHeadRequestAdmin(admin.ModelAdmin):
    list_display = ("user", "club_name", "status", "created_at")
    actions = ["approve_requests", "reject_requests"]

    def approve_requests(self, request, queryset):
        for obj in queryset:
            obj.status = "approved"
            obj.save()
        self.message_user(request, "Selected requests approved.")

    def reject_requests(self, request, queryset):
        queryset.update(status="rejected")
        self.message_user(request, "Selected requests rejected.")


@admin.register(JoinRequest)
class JoinRequestAdmin(admin.ModelAdmin):
    list_display = ("user", "club", "status", "requested_at")
    actions = ["approve_requests", "reject_requests"]

    def approve_requests(self, request, queryset):
        from django.db import transaction
        from .models import ClubMembership

        for obj in queryset.select_related("club", "user"):
            with transaction.atomic():
                if obj.status != "approved":
                    obj.status = "approved"
                    obj.save()
                ClubMembership.objects.get_or_create(user=obj.user, club=obj.club, defaults={"role": "member"})
        self.message_user(request, "Selected requests approved and members added.")

    def reject_requests(self, request, queryset):
        queryset.update(status="rejected")
        self.message_user(request, "Selected requests rejected.")
