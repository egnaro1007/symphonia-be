from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from django.db.models import Q

from .models import Song, Artist, Album
from .serializers import SongSerializer, ArtistSerializer, AlbumSerializer

class SearchView(APIView):  # Fix typo: ApiView -> APIView
    def get(self, request, *args, **kwargs):
        query = request.query_params.get('query', None)
        max_results = int(request.query_params.get('max_results', 5))  # Default to 5 results

        if not query:
            return Response({'error': 'Query parameter is required'}, status=400)

        # Search for songs, artists, and albums
        songs = Song.objects.filter(Q(title__icontains=query))[:max_results]
        artists = Artist.objects.filter(Q(name__icontains=query))[:max_results]
        albums = Album.objects.filter(Q(title__icontains=query))[:max_results]

        # Serialize the results
        song_serializer = SongSerializer(songs, many=True)
        artist_serializer = ArtistSerializer(artists, many=True)
        album_serializer = AlbumSerializer(albums, many=True)

        return Response({
            'songs': song_serializer.data,
            'artists': artist_serializer.data,
            'albums': album_serializer.data,
        })

class SongViewSet(ReadOnlyModelViewSet):
    queryset = Song.objects.all()
    serializer_class = SongSerializer

class ArtistViewSet(ReadOnlyModelViewSet):
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer

class AlbumViewSet(ReadOnlyModelViewSet):
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer