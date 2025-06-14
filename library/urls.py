from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import SongViewSet, ArtistViewSet, AlbumViewSet, PlaylistViewSet
from .views import SearchView, UpdateListeningHistoryView, ListeningHistoryView, AddSongToPlaylistView, RemoveSongFromPlaylistView, LikedSongsView, UploadLyricsView, UserPlaylistsView, PublicPlaylistsView, FriendsPlaylistsView

router = DefaultRouter()
router.register(r'songs', SongViewSet, basename='song')
router.register(r'artists', ArtistViewSet, basename='artist')
router.register(r'albums', AlbumViewSet, basename='album')
router.register(r'playlists', PlaylistViewSet, basename='playlist')

urlpatterns = router.urls + [
    path('search/', SearchView.as_view(), name='search'),
    path('update-position/', UpdateListeningHistoryView.as_view(), name='update_position'),
    path('history/', ListeningHistoryView.as_view(), name='listening_history'),
    path('add-song-to-playlist/', AddSongToPlaylistView.as_view(), name='add_song_to_playlist'),
    path('remove-song-from-playlist/', RemoveSongFromPlaylistView.as_view(), name='remove_song_from_playlist'),
    path('like/', LikedSongsView.as_view(), name='like_song'),
    path('like/<int:song_id>/', LikedSongsView.as_view(), name='like_song'),
    path('songs/<int:song_id>/lyrics/', UploadLyricsView.as_view(), name='upload_lyrics'),
    path('user-playlists/<int:user_id>/', UserPlaylistsView.as_view(), name='user_playlists'),
    path('public-playlists/', PublicPlaylistsView.as_view(), name='public_playlists'),
    path('friends-playlists/', FriendsPlaylistsView.as_view(), name='friends_playlists'),
]
