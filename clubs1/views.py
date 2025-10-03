# clubs1/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.db import IntegrityError, transaction
from django.utils import timezone

from .decorators import user_is_club_admin
from .models import CustomUser, UserProfile, Club, ClubMembership, JoinRequest, ClubHeadRequest, Announcement, Event
from .forms import CustomUserCreationForm, UserProfileForm, AnnouncementForm, EventForm

# --- AUTHENTICATION VIEWS (No Changes) ---
def signup_view(request):
    if request.user.is_authenticated:
        return redirect('clubs1:dashboard')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('clubs1:login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'auth/signup.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('clubs1:dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_page = request.GET.get('next')
            if next_page:
                return redirect(next_page)
            return redirect('clubs1:dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'auth/login.html')


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('clubs1:home')


# --- DASHBOARD & PROFILE VIEWS (No Changes) ---
@login_required
def dashboard_view(request):
    if request.user.is_superuser:
        context = {
            'user_count': CustomUser.objects.count(),
            'club_count': Club.objects.count(),
            'pending_club_requests': ClubHeadRequest.objects.filter(status='pending'),
        }
        return render(request, 'dashboards/site_admin_dashboard.html', context)

    coordinated_clubs = request.user.coordinated_clubs.all()
    if coordinated_clubs.exists():
        return redirect('clubs1:faculty_admin_dashboard')

    administered_clubs = Club.objects.filter(clubmembership__user=request.user, clubmembership__role='admin')
    if administered_clubs.exists():
        context = {
            'administered_clubs': administered_clubs,
            'pending_join_requests': JoinRequest.objects.filter(club__in=administered_clubs, status='pending'),
            'joined_clubs': request.user.clubs.all()
        }
        return render(request, 'dashboards/club_admin_dashboard.html', context)
    
    context = {
        'joined_clubs': request.user.clubs.all()
    }
    return render(request, 'dashboards/student_dashboard.html', context)


@login_required
def faculty_admin_dashboard_view(request):
    coordinated_clubs = request.user.coordinated_clubs.all()
    if not coordinated_clubs.exists() and not request.user.is_superuser:
        raise PermissionDenied("You do not have permission to view this page.")
    context = {
        'coordinated_clubs': coordinated_clubs,
        'club_count': coordinated_clubs.count(),
    }
    return render(request, 'dashboards/faculty_admin_dashboard.html', context)


@login_required
def request_club_head_view(request):
    if request.method == 'POST':
        club_name = request.POST.get('club_name')
        club_description = request.POST.get('club_description') or ''
        message = request.POST.get('message') or ''
        # Prevent duplicates
        exists = ClubHeadRequest.objects.filter(user=request.user, club_name__iexact=club_name, status='pending').exists()
        if exists:
            messages.info(request, 'You have already submitted a request for this club. Please wait for approval.')
            return render(request, 'clubs/request_exists.html', { 'club': {'name': club_name} })
        ClubHeadRequest.objects.create(user=request.user, club_name=club_name, club_description=club_description, message=message)
        return render(request, 'clubs/request_success.html', { 'club': {'name': club_name} })
    return render(request, 'clubs/request_club_head.html')


@login_required
def faculty_club_detail_view(request, club_id):
    club = get_object_or_404(Club, pk=club_id, faculty_coordinator=request.user)
    context = {
        'club': club,
        'members': club.clubmembership_set.all().order_by('user__username'),
        'announcements': club.announcements.order_by('-created_at')[:5],
        'events': club.events.order_by('-date')[:5],
    }
    return render(request, 'dashboards/faculty_club_detail.html', context)


@login_required
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('clubs1:profile')
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'profile.html', {'form': form, 'profile': profile})


# --- PUBLIC & CLUB VIEWS (No Changes) ---
def home_view(request):
    announcements = Announcement.objects.all().order_by('-created_at')[:5]
    events = Event.objects.filter(date__gte=timezone.now().date()).order_by('date')[:5]
    return render(request, 'home.html', {'announcements': announcements, 'events': events})


def club_list_view(request):
    clubs = Club.objects.all()
    return render(request, 'clubs/club_list.html', {'clubs': clubs})


def club_detail_view(request, club_id):
    club = get_object_or_404(Club, pk=club_id)
    announcements = club.announcements.order_by('-created_at')[:3]
    events = club.events.filter(date__gte=timezone.now().date()).order_by('date')[:3]
    
    is_member = False
    is_club_admin = False
    join_request_pending = False
    if request.user.is_authenticated:
        membership = ClubMembership.objects.filter(user=request.user, club=club).first()
        if membership:
            is_member = True
            if membership.role == 'admin':
                is_club_admin = True
        else:
            join_request_pending = JoinRequest.objects.filter(user=request.user, club=club, status='pending').exists()
    context = {
        'club': club, 'announcements': announcements, 'events': events,
        'is_member': is_member, 'is_club_admin': is_club_admin, 'join_request_pending': join_request_pending,
    }
    return render(request, 'clubs/club_detail.html', context)


# --- CLUB ACTION & MANAGEMENT VIEWS (UPDATED SECTION) ---

@login_required
def submit_join_request(request, club_id):
    club = get_object_or_404(Club, pk=club_id)
    try:
        JoinRequest.objects.create(user=request.user, club=club)
        messages.success(request, f'Your request to join {club.name} has been sent.')
    except IntegrityError:
        messages.warning(request, f'You have already submitted a request to join {club.name}.')
    return redirect('clubs1:club_detail', club_id=club.id)


@login_required
@user_is_club_admin
def manage_club_members_view(request, club_id):
    club = get_object_or_404(Club, pk=club_id)
    pending_requests = JoinRequest.objects.filter(club=club, status='pending')
    current_members = ClubMembership.objects.filter(club=club).order_by('user__username')
    context = {
        'club': club,
        'requests': pending_requests,
        'members': current_members,
    }
    return render(request, 'clubs/manage_members.html', context)


@login_required
def process_join_request(request, request_id, action):
    join_request = get_object_or_404(JoinRequest, pk=request_id)
    club = join_request.club
    if not (ClubMembership.objects.filter(user=request.user, club=club, role='admin').exists() or request.user.is_superuser):
        raise PermissionDenied

    if action == 'approve':
        with transaction.atomic():
            join_request.status = 'approved'
            ClubMembership.objects.get_or_create(user=join_request.user, club=club, defaults={'role': 'member'})
            join_request.save()
        messages.success(request, f"{join_request.user.username}'s request has been approved.")
    elif action == 'reject':
        join_request.status = 'rejected'
        join_request.save()
        messages.info(request, f"{join_request.user.username}'s request has been rejected.")
    
    return redirect('clubs1:manage_club_members', club_id=club.id)


@login_required
def promote_member_view(request, membership_id):
    membership = get_object_or_404(ClubMembership, pk=membership_id)
    club = membership.club
    if not (ClubMembership.objects.filter(user=request.user, club=club, role='admin').exists() or request.user.is_superuser or request.user == club.faculty_coordinator):
        raise PermissionDenied("You do not have permission to perform this action.")

    membership.role = 'admin'
    membership.save()
    messages.success(request, f"{membership.user.username} has been promoted to Club Admin for {club.name}.")
    return redirect('clubs1:manage_club_members', club_id=club.id)


@login_required
def remove_member_view(request, membership_id):
    membership = get_object_or_404(ClubMembership, pk=membership_id)
    club = membership.club
    user_to_remove = membership.user

    if not (ClubMembership.objects.filter(user=request.user, club=club, role='admin').exists() or request.user.is_superuser):
        raise PermissionDenied("You do not have permission to perform this action.")
    
    if membership.role == 'admin' and club.get_club_admins().count() == 1:
        messages.error(request, f"You cannot remove {user_to_remove.username} as they are the last admin. Promote another member first.")
        return redirect('clubs1:manage_club_members', club_id=club.id)

    membership.delete()
    messages.info(request, f"{user_to_remove.username} has been removed from {club.name}.")
    return redirect('clubs1:manage_club_members', club_id=club.id)


@login_required
@user_is_club_admin
def create_club_announcement(request, club_id):
    club = get_object_or_404(Club, pk=club_id)
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, request.FILES)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.club = club
            announcement.posted_by = request.user
            announcement.save()
            messages.success(request, 'Announcement created successfully.')
            return redirect('clubs1:club_detail', club_id=club.id)
    else:
        form = AnnouncementForm()
    return render(request, 'clubs/create_announcement.html', {'form': form, 'club': club})


@login_required
@user_is_club_admin
def create_club_event(request, club_id):
    club = get_object_or_404(Club, pk=club_id)
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.club = club
            event.created_by = request.user
            event.save()
            messages.success(request, 'Event created successfully.')
            return redirect('clubs1:club_detail', club_id=club.id)
    else:
        form = EventForm()
    return render(request, 'clubs/create_event.html', {'form': form, 'club': club})
