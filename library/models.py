from django.db import models
    
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
    audio = models.FileField(upload_to='songs/')

    def __str__(self):
        return f"{self.title} by {', '.join([artist.name for artist in self.artist.all()])}"
    
class Playlist(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    songs = models.ManyToManyField(Song, related_name='playlists')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
