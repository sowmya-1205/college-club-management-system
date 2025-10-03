# clubs1/urls.py

from django.urls import path
from . import views

app_name = 'clubs1'

urlpatterns = [
    # Auth
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard & Profile
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('dashboard/faculty/', views.faculty_admin_dashboard_view, name='faculty_admin_dashboard'),
    path('faculty/club-details/<int:club_id>/', views.faculty_club_detail_view, name='faculty_club_detail'),
    
    # Core Public Views
    path('', views.home_view, name='home'),
    path('clubs/', views.club_list_view, name='club_list'),
    path('clubs/<int:club_id>/', views.club_detail_view, name='club_detail'),

    # --- UPDATED & NEW MANAGEMENT URLS ---
    path('clubs/<int:club_id>/join/', views.submit_join_request, name='submit_join_request'),
    # This URL now points to the new, comprehensive member management view
    path('clubs/<int:club_id>/manage-members/', views.manage_club_members_view, name='manage_club_members'),
    path('requests/<int:request_id>/process/<str:action>/', views.process_join_request, name='process_join_request'),
    # New URLs for promoting and removing members
    path('members/promote/<int:membership_id>/', views.promote_member_view, name='promote_member'),
    path('members/remove/<int:membership_id>/', views.remove_member_view, name='remove_member'),

    # Content Creation
    path('clubs/<int:club_id>/announcements/create/', views.create_club_announcement, name='create_announcement'),
    path('clubs/<int:club_id>/events/create/', views.create_club_event, name='create_club_event'),
]