from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.contrib.auth.models import User
import json
from rest_framework import status
from rest_framework.decorators import api_view, action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import Song, Artist, Album, ListeningHistory, Playlist
from .serializers import SongSerializer, SimpleSongSerializer, ArtistSerializer, AlbumSerializer, PlaylistSerializer, PlaylistDetailSerializer, ListeningHistorySerializer
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
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return PlaylistDetailSerializer
        return PlaylistSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def list(self, request, *args, **kwargs):
        # Get playlists owned by the current user, ordered by creation date (newest first)
        queryset = self.get_queryset().filter(owner=request.user).order_by('-created_at')
        
        # Apply any additional filters here if needed
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def upload_cover(self, request, pk=None):
        """
        Upload cover image for a playlist
        """
        try:
            print(f"=== UPLOAD COVER DEBUG ===")
            print(f"User: {request.user.username}")
            print(f"Playlist ID: {pk}")
            print(f"Request FILES: {list(request.FILES.keys())}")
            print(f"Request DATA: {dict(request.data)}")
            
            playlist = self.get_object()
            print(f"Playlist found: {playlist.name} (owner: {playlist.owner.username})")
            
            # Check if user owns the playlist
            if playlist.owner != request.user:
                print(f"Permission denied: {request.user.username} != {playlist.owner.username}")
                return Response(
                    {"error": "You don't have permission to modify this playlist"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Check if file is provided
            if 'cover_image' not in request.FILES:
                print(f"No cover_image in request.FILES. Available keys: {list(request.FILES.keys())}")
                return Response(
                    {"error": "No cover image file provided"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            cover_image = request.FILES['cover_image']
            print(f"Cover image file: {cover_image.name}, size: {cover_image.size}, content_type: {cover_image.content_type}")
            
            # Validate file type by extension (more reliable than content_type for mobile uploads)
            import os
            file_extension = os.path.splitext(cover_image.name)[1].lower()
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif']
            allowed_content_types = ['image/jpeg', 'image/png', 'image/jpg', 'image/gif', 'application/octet-stream']
            
            print(f"File extension: {file_extension}")
            
            if file_extension not in allowed_extensions:
                print(f"Invalid file extension: {file_extension}. Allowed: {allowed_extensions}")
                return Response(
                    {"error": f"Invalid file format. Please upload an image file with extension: {', '.join(allowed_extensions)}"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Also check content type but be more lenient (mobile apps often send application/octet-stream)
            if hasattr(cover_image, 'content_type') and cover_image.content_type not in allowed_content_types:
                print(f"Invalid content type: {cover_image.content_type}. Allowed: {allowed_content_types}")
                return Response(
                    {"error": "Invalid file format. Please upload an image file (JPEG, PNG, GIF)"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Delete old cover image if it exists
            old_cover_path = None
            if playlist.cover_image:
                old_cover_path = playlist.cover_image.path
                old_cover_name = playlist.cover_image.name
                print(f"Found old cover image: {old_cover_name}")
                print(f"Old cover path: {old_cover_path}")
                
                # Delete the old file from filesystem
                try:
                    playlist.cover_image.delete(save=False)  # Don't save the model yet
                    print(f"Successfully deleted old cover image")
                except Exception as e:
                    print(f"Warning: Could not delete old cover image: {str(e)}")
            else:
                print("No existing cover image to delete")
            
            # Save the new cover image
            playlist.cover_image = cover_image
            playlist.save()
            
            print(f"New cover image saved: {playlist.cover_image.name}")
            print(f"Cover image URL: {playlist.cover_image.url}")
            print(f"Cover image path: {playlist.cover_image.path}")
            
            serializer = PlaylistDetailSerializer(playlist)
            print(f"=== UPLOAD COVER SUCCESS ===")
            return Response(
                {
                    "message": "Cover image uploaded successfully",
                    "playlist": serializer.data
                }, 
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            print(f"=== UPLOAD COVER ERROR ===")
            print(f"Error: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return Response(
                {"error": f"An error occurred while uploading cover image: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['delete'], permission_classes=[IsAuthenticated])
    def remove_cover(self, request, pk=None):
        """
        Remove cover image from a playlist
        """
        try:
            playlist = self.get_object()
            
            # Check if user owns the playlist
            if playlist.owner != request.user:
                return Response(
                    {"error": "You don't have permission to modify this playlist"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            if playlist.cover_image:
                old_cover_name = playlist.cover_image.name
                old_cover_path = playlist.cover_image.path
                print(f"Removing cover image: {old_cover_name}")
                print(f"Cover image path: {old_cover_path}")
                
                try:
                    # Delete the file from filesystem and clear the field
                    playlist.cover_image.delete(save=False)
                    playlist.cover_image = None
                    playlist.save()
                    print(f"Successfully removed cover image")
                    
                    return Response(
                        {"message": "Cover image removed successfully"}, 
                        status=status.HTTP_200_OK
                    )
                except Exception as e:
                    print(f"Error removing cover image: {str(e)}")
                    return Response(
                        {"error": f"Failed to remove cover image: {str(e)}"}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            else:
                return Response(
                    {"message": "No cover image to remove"}, 
                    status=status.HTTP_200_OK
                )
                
        except Exception as e:
            return Response(
                {"error": f"An error occurred while removing cover image: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

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
            
            # Check if this is the first song being added to the playlist
            is_first_song = playlist.songs.count() == 0
            
            # Add song to playlist
            playlist.songs.add(song)
            
            # If this is the first song and playlist doesn't have a cover image,
            # automatically copy the song's cover art as playlist cover
            if is_first_song and not playlist.cover_image and song.cover_art:
                try:
                    import os
                    import shutil
                    from django.core.files import File
                    from django.conf import settings
                    
                    print(f"Auto-copying cover from first song: {song.title}")
                    print(f"Song cover art path: {song.cover_art.path}")
                    
                    # Get file extension from song cover art
                    original_path = song.cover_art.path
                    file_extension = os.path.splitext(original_path)[1]
                    
                    # Create new filename with playlist ID
                    new_filename = f"{playlist.id}{file_extension}"
                    playlist_covers_dir = os.path.join(settings.MEDIA_ROOT, 'images', 'playlist_covers')
                    new_file_path = os.path.join(playlist_covers_dir, new_filename)
                    
                    print(f"Copying to: {new_file_path}")
                    
                    # Ensure the playlist covers directory exists
                    os.makedirs(playlist_covers_dir, exist_ok=True)
                    
                    # Copy the file
                    shutil.copy2(original_path, new_file_path)
                    
                    # Set the playlist cover_image field to the new file
                    relative_path = f"images/playlist_covers/{new_filename}"
                    playlist.cover_image.name = relative_path
                    playlist.save()
                    
                    print(f"Successfully copied and set playlist cover: {relative_path}")
                    
                except Exception as e:
                    print(f"Failed to copy song cover to playlist: {str(e)}")
                    import traceback
                    print(f"Traceback: {traceback.format_exc()}")
                    # Don't fail the entire operation if cover setting fails
            
            # Return updated playlist data
            from library.serializers import PlaylistDetailSerializer
            serializer = PlaylistDetailSerializer(playlist)
            return Response({
                "message": "Song added to playlist",
                "playlist": serializer.data
            }, status=200)
        except Playlist.DoesNotExist:
            return Response({"error": "Playlist not found"}, status=404)
        except Song.DoesNotExist:
            return Response({"error": "Song not found"}, status=404)

class RemoveSongFromPlaylistView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        playlist_id = request.data.get('playlist_id')
        song_id = request.data.get('song_id')

        if not playlist_id or not song_id:
            return Response({"error": "playlist_id and song_id fields are required"}, status=400)

        try:
            playlist = Playlist.objects.get(id=playlist_id, owner=request.user)
            song = Song.objects.get(id=song_id)
            
            # Check if song is in the playlist
            if song not in playlist.songs.all():
                return Response({"error": "Song not found in playlist"}, status=404)
            
            # Remove song from playlist
            playlist.songs.remove(song)
            
            # Return updated playlist data
            from library.serializers import PlaylistDetailSerializer
            serializer = PlaylistDetailSerializer(playlist)
            return Response({
                "message": "Song removed from playlist",
                "playlist": serializer.data
            }, status=200)
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

class UploadLyricsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, song_id):
        """
        Upload lyrics from JSON file for a specific song
        Expected JSON format:
        [
            {
                "startTime": 0,
                "text": "Lyrics line text",
                "duration": 5.59
            },
            ...
        ]
        """
        try:
            song = Song.objects.get(id=song_id)
        except Song.DoesNotExist:
            return Response({"error": "Song not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if file is provided
        if 'lyrics_file' not in request.FILES:
            return Response(
                {"error": "No lyrics file provided. Please upload a JSON file."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        lyrics_file = request.FILES['lyrics_file']
        
        # Validate file extension
        if not lyrics_file.name.endswith('.json'):
            return Response(
                {"error": "Invalid file format. Please upload a JSON file."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Read and parse JSON file
            file_content = lyrics_file.read().decode('utf-8')
            lyrics_data = json.loads(file_content)
            
            # Validate JSON structure
            if not isinstance(lyrics_data, list):
                return Response(
                    {"error": "Invalid JSON format. Expected an array of lyrics objects."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate each lyrics entry
            for i, entry in enumerate(lyrics_data):
                if not isinstance(entry, dict):
                    return Response(
                        {"error": f"Invalid entry at index {i}. Each entry must be an object."}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                required_fields = ['startTime', 'text', 'duration']
                for field in required_fields:
                    if field not in entry:
                        return Response(
                            {"error": f"Missing required field '{field}' in entry at index {i}."}, 
                            status=status.HTTP_400_BAD_REQUEST
                        )
                
                # Validate data types
                try:
                    float(entry['startTime'])
                    float(entry['duration'])
                    str(entry['text'])
                except (ValueError, TypeError):
                    return Response(
                        {"error": f"Invalid data types in entry at index {i}. startTime and duration must be numbers."}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Save lyrics to song
            song.lyric = lyrics_data
            song.save()
            
            return Response(
                {
                    "message": "Lyrics uploaded successfully",
                    "song_id": song.id,
                    "song_title": song.title,
                    "lyrics_count": len(lyrics_data)
                }, 
                status=status.HTTP_200_OK
            )
            
        except json.JSONDecodeError as e:
            return Response(
                {"error": f"Invalid JSON format: {str(e)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": f"An error occurred while processing the file: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def delete(self, request, song_id):
        """
        Remove lyrics from a specific song
        """
        try:
            song = Song.objects.get(id=song_id)
        except Song.DoesNotExist:
            return Response({"error": "Song not found"}, status=status.HTTP_404_NOT_FOUND)
        
        song.lyric = None
        song.save()
        
        return Response(
            {"message": "Lyrics removed successfully"}, 
            status=status.HTTP_200_OK
        )
