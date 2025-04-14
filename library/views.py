from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Song, Artist, Album
from .serializers import SongSerializer, ArtistSerializer, AlbumSerializer

class SongViewSet(ReadOnlyModelViewSet):
    queryset = Song.objects.all()
    serializer_class = SongSerializer

class ArtistViewSet(ReadOnlyModelViewSet):
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer

class AlbumViewSet(ReadOnlyModelViewSet):
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer