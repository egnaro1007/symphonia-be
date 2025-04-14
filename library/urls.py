from rest_framework.routers import DefaultRouter
from .views import SongViewSet, ArtistViewSet, AlbumViewSet

router = DefaultRouter()
router.register(r'songs', SongViewSet, basename='song')
router.register(r'artists', ArtistViewSet, basename='artist')
router.register(r'albums', AlbumViewSet, basename='album')

urlpatterns = router.urls
