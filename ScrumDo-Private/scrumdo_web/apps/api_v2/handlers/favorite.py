from .common import *
from apps.projects.models import Project
from apps.projects.access import has_read_access
from apps.favorites.models import Favorite


class FavoritesHandler(BaseHandler):
    allowed_methods = ('POST', 'DELETE')

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def create(self, request, project_slug):
        project = Project.objects.get(slug=project_slug)
        if not has_read_access(project, request.user):
            raise PermissionDenied("You don't have access to that Project")
        Favorite.setFavorite(1, project.id, request.user, True)
        return []


    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def delete(self, request, project_slug):
        project = Project.objects.get(slug=project_slug)
        Favorite.setFavorite(1, project.id, request.user, False)
        return []

