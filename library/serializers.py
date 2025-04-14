from rest_framework import serializers
from .models import Song, Artist, Album, Playlist

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
                'cover_art': song.cover_art if song.cover_art else None
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

