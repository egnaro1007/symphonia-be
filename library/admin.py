from django.contrib import admin

from .models import Song, Artist, Album, Playlist, ListeningHistory

admin.site.register(Song)
admin.site.register(Artist)
admin.site.register(Album)
admin.site.register(Playlist)
admin.site.register(ListeningHistory)
