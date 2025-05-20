from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.contrib.auth.models import User

from .models import Song, Artist, Album, ListeningHistory, Playlist
from .serializers import SongSerializer, SimpleSongSerializer, ArtistSerializer, AlbumSerializer, PlaylistSerializer, ListeningHistorySerializer
from .permissions import CanAcessPermission

class SearchView(APIView):
    def get(self, request, *args, **kwargs):
        query = request.query_params.get('query', None)
        max_results = int(request.query_params.get('max_results', 5))  # Default to 5 results

        if not query:
            return Response({'error': 'Query parameter is required'}, status=400)

        songs = Song.objects.filter(Q(title__icontains=query))[:max_results]
        artists = Artist.objects.filter(Q(name__icontains=query))[:max_results]
        albums = Album.objects.filter(Q(title__icontains=query))[:max_results]

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

class PlaylistViewSet(ModelViewSet):
    queryset = Playlist.objects.all()
    serializer_class = PlaylistSerializer
    permission_classes = [CanAcessPermission]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
        
    def list(self, request, *args, **kwargs):
        user = request.user if request.user.is_authenticated else None
        query_user_id = request.data.get('user_id', None)
        
        if query_user_id:
            try:
                query_user = User.objects.get(id=query_user_id)
                serializer = self.get_serializer(self.get_queryset().filter(owner=query_user), many=True)
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=404)
        else:
            serializer = self.get_serializer(self.get_queryset().filter(owner=user), many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        playlist_data = super().retrieve(request, *args, **kwargs).data

        serialized_songs = SimpleSongSerializer(self.get_object().songs.all(), many=True).data
        playlist_data['songs'] = serialized_songs

        return Response(playlist_data)
    
class AddSongToPlaylistView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        playlist_id = request.data.get('playlist_id')
        song_id = request.data.get('song_id')

        if not playlist_id or not song_id:
            return Response({"error": "playlist_id and song_id fields are required"}, status=400)

        try:
            playlist = Playlist.objects.get(id=playlist_id, owner=request.user)
            song = Song.objects.get(id=song_id)
            playlist.songs.add(song)
            return Response({"message": "Song added to playlist"}, status=200)
        except Playlist.DoesNotExist:
            return Response({"error": "Playlist not found"}, status=404)
        except Song.DoesNotExist:
            return Response({"error": "Song not found"}, status=404)

class UpdateListeningHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        song_id = request.data.get('song_id')
        if not song_id:
            return Response({"error": "song_id field is required"}, status=400)

        try:
            song = Song.objects.get(id=song_id)
        except Song.DoesNotExist:
            return Response({"error": "Song not found"}, status=404)
        
        listening_history, created = ListeningHistory.objects.update_or_create(
                user=request.user,
                song=song,
                defaults={'position': int(request.data.get('position', 0))}
            )
        
        serializer = ListeningHistorySerializer (listening_history)

        return Response(serializer.data, status=201 if created else 200)
    
    def delete(self, request):
        song_id = request.data.get('song_id')
        history_id = request.data.get('id')
        if not song_id and not history_id:
            return Response({"error": "Either id or song_id field is required"}, status=400)

        try:
            if history_id:
                listening_history = ListeningHistory.objects.get(id=history_id, user=request.user)
            elif song_id:
                song = Song.objects.get(id=song_id)
                listening_history = ListeningHistory.objects.get(song=song, user=request.user)

            listening_history.delete()        
            return Response({"message": "Deleted"},status=204)
        except ListeningHistory.DoesNotExist:
            return Response({"error": "Listening history not found"}, status=404)
        except Song.DoesNotExist:
            return Response({"error": "Song not found"}, status=404)
        
class ListeningHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        histories = ListeningHistory.objects.filter(user=request.user).order_by('-updated_at')
        serializer = ListeningHistorySerializer(histories, many=True)
        return Response(serializer.data, status=200) 
    
class LikedSongsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, song_id=None):
        if not song_id:
            liked_songs = Song.objects.filter(liked_by=request.user)
            return Response(SimpleSongSerializer(liked_songs, many=True).data, status=200)
        else:
            try:
                song = Song.objects.get(id=song_id)
                liked_status = request.user in song.liked_by.all()
                return Response({"liked": liked_status}, status=200)
            except Song.DoesNotExist:
                return Response({"error": "Song not found"}, status=404)

    def post(self, request, song_id):
        if not song_id:
            return Response({"error": "song_id field is required"}, status=400)
        
        try:
            song = Song.objects.get(id=song_id)
            song.liked_by.add(request.user)
            return Response({"message": "Song liked"}, status=200)
        except Song.DoesNotExist:
            return Response({"error": "Song not found"}, status=404)

    def delete(self, request, song_id):
        if not song_id:
            return Response({"error": "song_id field is required"}, status=400)
        
        try:
            song = Song.objects.get(id=song_id)
            if request.user in song.liked_by.all():
                song.liked_by.remove(request.user)
                return Response({"message": "Song disliked"}, status=200)
            else:
                return Response({"error": "Song not liked"}, status=200)

        except Song.DoesNotExist:
            return Response({"error": "Song not found"}, status=404)
