from django.contrib import admin

from .models import Song, Artist, Album, Playlist, ListeningHistory

@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ['title', 'get_artists', 'get_available_qualities', 'duration']
    list_filter = ['release_date']
    search_fields = ['title', 'artist__name']
    filter_horizontal = ['artist', 'album', 'liked_by']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'artist', 'album', 'release_date', 'duration', 'cover_art', 'lyric')
        }),
        ('Audio Files', {
            'fields': ('audio_lossless', 'audio_320kbps', 'audio_128kbps'),
            'description': 'Upload audio files for different quality levels. Files will be automatically renamed using the song ID.'
        }),
        ('Legacy', {
            'fields': ('audio',),
            'description': 'Legacy audio field - will be phased out',
            'classes': ('collapse',)
        }),
    )
    
    def get_artists(self, obj):
        return ", ".join([artist.name for artist in obj.artist.all()])
    get_artists.short_description = 'Artists'
    
    def get_available_qualities(self, obj):
        qualities = obj.get_available_qualities()
        return ", ".join(qualities) if qualities else "No audio"
    get_available_qualities.short_description = 'Available Qualities'

@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ['name', 'bio']
    search_fields = ['name']

@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ['title', 'get_artists', 'release_date']
    list_filter = ['release_date']
    search_fields = ['title', 'artist__name']
    filter_horizontal = ['artist']
    
    def get_artists(self, obj):
        return ", ".join([artist.name for artist in obj.artist.all()])
    get_artists.short_description = 'Artists'

@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'get_songs_count', 'share_permission', 'created_at']
    list_filter = ['share_permission', 'created_at']
    search_fields = ['name', 'owner__username']
    filter_horizontal = ['songs']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_songs_count(self, obj):
        return obj.songs.count()
    get_songs_count.short_description = 'Songs Count'

@admin.register(ListeningHistory)
class ListeningHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'song', 'position', 'updated_at']
    list_filter = ['updated_at']
    search_fields = ['user__username', 'song__title']
