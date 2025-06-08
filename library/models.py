from django.db import models
import os

from django.contrib.auth.models import User
    
def song_audio_upload_path(instance, filename, quality):
    """
    Custom upload path for song audio files.
    Files will be saved as: songs/{quality}/{song_id}.{extension}
    """
    # Get file extension from original filename
    file_extension = os.path.splitext(filename)[1]
    # Use song ID as filename
    new_filename = f"{instance.id}{file_extension}"
    return f"songs/{quality}/{new_filename}"

def lossless_upload_path(instance, filename):
    return song_audio_upload_path(instance, filename, 'lossless')

def high_quality_upload_path(instance, filename):
    return song_audio_upload_path(instance, filename, '320kbps')

def standard_quality_upload_path(instance, filename):
    return song_audio_upload_path(instance, filename, '128kbps')

class Artist(models.Model):
    name = models.CharField(max_length=255)
    bio = models.TextField(blank=True, null=True)
    artist_picture = models.ImageField(upload_to='images/artist_picture/', blank=True, null=True)

    def __str__(self):
        return self.name
    
class Album(models.Model):
    title = models.CharField(max_length=255)
    artist = models.ManyToManyField(Artist, related_name='albums')
    release_date = models.DateField(blank=True, null=True)
    cover_art = models.ImageField(upload_to='images/album_art/', blank=True, null=True)

    def __str__(self):
        return self.title
    
class Song(models.Model):
    title = models.CharField(max_length=255)
    artist = models.ManyToManyField('Artist', related_name='songs')
    album = models.ManyToManyField('Album', related_name='songs')
    release_date = models.DateField(blank=True, null=True)
    duration = models.DurationField(blank=True, null=True)
    cover_art = models.ImageField(upload_to='images/cover_art/', blank=True, null=True)
    
    # Multiple audio quality fields
    audio_lossless = models.FileField(upload_to=lossless_upload_path, blank=True, null=True, help_text="FLAC/WAV lossless audio")
    audio_320kbps = models.FileField(upload_to=high_quality_upload_path, blank=True, null=True, help_text="MP3 320kbps high quality audio")
    audio_128kbps = models.FileField(upload_to=standard_quality_upload_path, blank=True, null=True, help_text="MP3 128kbps standard quality audio")
    
    # Keep old field for backward compatibility during migration
    audio = models.FileField(upload_to='songs/', blank=True, null=True, help_text="Legacy audio field - will be migrated")
    
    liked_by = models.ManyToManyField(User, related_name='liked_songs', blank=True)
    lyric = models.JSONField(blank=True, null=True)

    def get_audio_url(self, quality='320kbps'):
        """
        Get audio URL for the requested quality with fallback logic
        """
        quality_map = {
            'lossless': self.audio_lossless,
            '320kbps': self.audio_320kbps,
            '128kbps': self.audio_128kbps,
        }
        
        # Try to get the requested quality
        audio_file = quality_map.get(quality)
        if audio_file and audio_file.name:
            return audio_file.url
        
        # Fallback to legacy audio field if no quality-specific file
        if self.audio and self.audio.name:
            return self.audio.url
            
        # Fallback to any available quality (prioritize higher quality)
        for fallback_quality in ['lossless', '320kbps', '128kbps']:
            fallback_file = quality_map.get(fallback_quality)
            if fallback_file and fallback_file.name:
                return fallback_file.url
                
        return None

    def get_available_qualities(self):
        """
        Get list of available quality options for this song
        """
        qualities = []
        if self.audio_lossless and self.audio_lossless.name:
            qualities.append('lossless')
        if self.audio_320kbps and self.audio_320kbps.name:
            qualities.append('320kbps')
        if self.audio_128kbps and self.audio_128kbps.name:
            qualities.append('128kbps')
        
        # Include legacy audio if no quality-specific files
        if not qualities and self.audio and self.audio.name:
            qualities.append('320kbps')  # Assume legacy files are 320kbps as mentioned
            
        return qualities

    def get_file_size(self, quality='320kbps'):
        """
        Get file size for the requested quality
        """
        quality_map = {
            'lossless': self.audio_lossless,
            '320kbps': self.audio_320kbps,
            '128kbps': self.audio_128kbps,
        }
        
        audio_file = quality_map.get(quality)
        if audio_file and audio_file.name:
            try:
                return audio_file.size
            except:
                return 0
        return 0

    def __str__(self):
        return f"{self.title} by {', '.join([artist.name for artist in self.artist.all()])}"
    
class ListeningHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listening_history')
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='listening_history')
    position = models.IntegerField(default=0)  
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'song')

    def __str__(self):
        return f"{self.user.username} - {self.song.title} at {self.position}s"


class SharingPermission(models.TextChoices):
    PUBLIC = 'public', 'Public'
    FRIENDS = 'friends', 'Friends'
    PRIVATE = 'private', 'Private'


def playlist_cover_upload_path(instance, filename):
    """
    Custom upload path for playlist cover images.
    Files will be saved as: images/playlist_covers/{playlist_id}.{extension}
    """
    import os
    # Get file extension from original filename
    file_extension = os.path.splitext(filename)[1]
    # Use playlist ID as filename
    new_filename = f"{instance.id}{file_extension}"
    return f"images/playlist_covers/{new_filename}"

class Playlist(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='playlists')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    songs = models.ManyToManyField(Song, related_name='playlists')
    cover_image = models.ImageField(upload_to=playlist_cover_upload_path, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    share_permission = models.CharField(
        max_length=10,
        choices=SharingPermission.choices,
        default=SharingPermission.PRIVATE,
    )

    def __str__(self):
        return self.name
    
    def is_accessible_by(self, user):
        if self.owner == user:
            return True

        if self.share_permission == SharingPermission.PUBLIC:
            return True
        elif self.share_permission == SharingPermission.FRIENDS:
            return self.owner.is_friend_with(user)
        return False
