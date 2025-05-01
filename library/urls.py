from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import SongViewSet, ArtistViewSet, AlbumViewSet
from .views import SearchView

router = DefaultRouter()
router.register(r'songs', SongViewSet, basename='song')
router.register(r'artists', ArtistViewSet, basename='artist')
router.register(r'albums', AlbumViewSet, basename='album')

urlpatterns = router.urls + [
    path('search/', SearchView.as_view(), name='search'),
]
