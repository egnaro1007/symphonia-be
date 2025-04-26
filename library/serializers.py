from rest_framework import serializers
from .models import Song, Artist, Album, Playlist, ListeningHistory

class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = ['id', 'name', 'bio', 'artist_picture']

class AlbumSerializer(serializers.ModelSerializer):
    artist = ArtistSerializer(many=True)
    songs = serializers.SerializerMethodField()

    class Meta:
        model = Album
        fields = ['id', 'title', 'artist', 'songs', 'release_date', 'cover_art']

    def get_songs(self, obj):
        return [
            {
                'id': song.id,
                'title': song.title,
                'cover_art': song.cover_art.url if song.cover_art else None
            }
            for song in obj.songs.all()
        ]
    
class SimpleAlbumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Album
        fields = ['id', 'title', 'artist', 'release_date', 'cover_art']

class SongSerializer(serializers.ModelSerializer):
    artist = ArtistSerializer(many=True) 
    album = SimpleAlbumSerializer(many=True) 

    class Meta:
        model = Song
        fields = ['id', 'title', 'artist', 'album', 'release_date', 'duration', 'cover_art', 'audio']

class SimpleSongSerializer(serializers.ModelSerializer):
    artist = serializers.SerializerMethodField()
    cover_art = serializers.SerializerMethodField()

    class Meta:
        model = Song
        fields = ['id', 'title', 'artist', 'cover_art']

    def get_artist(self, obj):
        return [{'id': artist.id, 'name': artist.name} for artist in obj.artist.all()]
    
    def get_cover_art(self, obj):
        return obj.cover_art if obj.cover_art else None
    
class PlaylistSerializer(serializers.ModelSerializer):
    songs = serializers.PrimaryKeyRelatedField(queryset=Song.objects.all(), many=True)

    class Meta:
        model = Playlist
        fields = ['id', 'owner', 'name', 'description', 'songs', 'created_at', 'updated_at', 'share_permission']
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']

class ListeningHistorySerializer(serializers.ModelSerializer):
    song = serializers.SerializerMethodField()

    class Meta:
        model = ListeningHistory
        fields = ['id', 'song', 'position', 'updated_at']

    def get_song(self, obj):
        return {
            'id': obj.song.id,
            'title': obj.song.title,
            'cover_art': obj.song.cover_art if obj.song.cover_art else None,
        }
