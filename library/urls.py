from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import SongViewSet, ArtistViewSet, AlbumViewSet, PlaylistViewSet
from .views import SearchView, UpdateListeningHistoryView, ListeningHistoryView

router = DefaultRouter()
router.register(r'songs', SongViewSet, basename='song')
router.register(r'artists', ArtistViewSet, basename='artist')
router.register(r'albums', AlbumViewSet, basename='album')
router.register(r'playlists', PlaylistViewSet, basename='playlist')

urlpatterns = router.urls + [
    path('search/', SearchView.as_view(), name='search'),
    path('update-position/', UpdateListeningHistoryView.as_view(), name='update_position'),
    path('history/', ListeningHistoryView.as_view(), name='listening_history'),
]
