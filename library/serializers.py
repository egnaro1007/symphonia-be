from rest_framework import serializers
from .models import Song, Artist, Album, Playlist, ListeningHistory
from datetime import timedelta

class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = ['id', 'name', 'bio', 'artist_picture']

class SimpleArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = ['id', 'name', 'artist_picture']

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
    artist = SimpleArtistSerializer(many=True) 
    album = SimpleAlbumSerializer(many=True)
    available_qualities = serializers.SerializerMethodField()
    audio_urls = serializers.SerializerMethodField()
    audio_file_sizes = serializers.SerializerMethodField()

    class Meta:
        model = Song
        fields = ['id', 'title', 'artist', 'album', 'release_date', 'duration', 'cover_art', 'audio', 'audio_urls', 'available_qualities', 'audio_file_sizes', 'lyric']

    def get_available_qualities(self, obj):
        return obj.get_available_qualities()
    
    def get_audio_urls(self, obj):
        return {
            'lossless': obj.audio_lossless.url if obj.audio_lossless and obj.audio_lossless.name else None,
            '320kbps': obj.audio_320kbps.url if obj.audio_320kbps and obj.audio_320kbps.name else None,
            '128kbps': obj.audio_128kbps.url if obj.audio_128kbps and obj.audio_128kbps.name else None,
            'legacy': obj.audio.url if obj.audio and obj.audio.name else None,
        }
    
    def get_audio_file_sizes(self, obj):
        return {
            'lossless': obj.get_file_size('lossless'),
            '320kbps': obj.get_file_size('320kbps'),
            '128kbps': obj.get_file_size('128kbps'),
        }

class SimpleSongSerializer(serializers.ModelSerializer):
    artist = serializers.SerializerMethodField()
    album = serializers.SerializerMethodField()
    cover_art = serializers.SerializerMethodField()
    duration_seconds = serializers.SerializerMethodField()
    available_qualities = serializers.SerializerMethodField()
    audio_urls = serializers.SerializerMethodField()

    class Meta:
        model = Song
        fields = ['id', 'title', 'artist', 'album', 'release_date', 'cover_art', 'audio', 'audio_urls', 'available_qualities', 'lyric', 'duration_seconds']

    def get_artist(self, obj):
        return [{'id': artist.id, 'name': artist.name} for artist in obj.artist.all()]
    
    def get_album(self, obj):
        return [{'id': album.id, 'title': album.title, 'release_date': album.release_date} for album in obj.album.all()]
    
    def get_cover_art(self, obj):
        return obj.cover_art.url if obj.cover_art else None
    
    def get_duration_seconds(self, obj):
        if obj.duration:
            return int(obj.duration.total_seconds())
        return 0
    
    def get_available_qualities(self, obj):
        return obj.get_available_qualities()
    
    def get_audio_urls(self, obj):
        return {
            'lossless': obj.audio_lossless.url if obj.audio_lossless and obj.audio_lossless.name else None,
            '320kbps': obj.audio_320kbps.url if obj.audio_320kbps and obj.audio_320kbps.name else None,
            '128kbps': obj.audio_128kbps.url if obj.audio_128kbps and obj.audio_128kbps.name else None,
            'legacy': obj.audio.url if obj.audio and obj.audio.name else None,
        }

class PlaylistSerializer(serializers.ModelSerializer):
    songs = serializers.PrimaryKeyRelatedField(queryset=Song.objects.all(), many=True, required=False)

    class Meta:
        model = Playlist
        fields = ['id', 'owner', 'name', 'description', 'songs', 'cover_image', 'created_at', 'updated_at', 'share_permission']
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']

class PlaylistDetailSerializer(serializers.ModelSerializer):
    songs = SimpleSongSerializer(many=True, read_only=True)
    owner_name = serializers.SerializerMethodField()
    owner_avatar_url = serializers.SerializerMethodField()
    total_duration_seconds = serializers.SerializerMethodField()
    songs_count = serializers.SerializerMethodField()
    cover_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Playlist
        fields = ['id', 'owner', 'owner_name', 'owner_avatar_url', 'name', 'description', 'songs', 'cover_image', 'cover_image_url', 'created_at', 'updated_at', 'share_permission', 'total_duration_seconds', 'songs_count']
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']

    def get_owner_name(self, obj):
        return obj.owner.username if obj.owner else 'Unknown'
    
    def get_owner_avatar_url(self, obj):
        return obj.owner.get_profile_picture_url() if obj.owner else None
    
    def get_total_duration_seconds(self, obj):
        total_seconds = 0
        for song in obj.songs.all():
            if song.duration:
                total_seconds += int(song.duration.total_seconds())
        return total_seconds
    
    def get_songs_count(self, obj):
        return obj.songs.count()
    
    def get_cover_image_url(self, obj):
        return obj.cover_image.url if obj.cover_image else None

class ListeningHistorySerializer(serializers.ModelSerializer):
    song = serializers.SerializerMethodField()

    class Meta:
        model = ListeningHistory
        fields = ['id', 'song', 'position', 'updated_at']

    def get_song(self, obj):
        return {
            'id': obj.song.id,
            'title': obj.song.title,
            'cover_art': obj.song.cover_art.url if obj.song.cover_art else None,
        }
