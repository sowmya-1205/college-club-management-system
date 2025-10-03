from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from .models import Club, ClubMembership

def user_is_club_admin(function):
    def wrap(request, *args, **kwargs):
        club_id = kwargs.get('club_id')
        if not club_id:
            raise ValueError("Decorator requires a 'club_id' URL parameter.")
        club = get_object_or_404(Club, pk=club_id)
        if request.user.is_authenticated and (ClubMembership.objects.filter(user=request.user, club=club, role='admin').exists() or request.user.is_superuser):
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return wrap