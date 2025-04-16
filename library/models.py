from django.db import models

from django.contrib.auth.models import User
    
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

class Friendship(models.Model):
    class FriendshipStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        ACCEPTED = 'accepted', 'Accepted'

    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friendship_user1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friendship_user2')
    status = models.CharField(
        max_length=10,
        choices=FriendshipStatus.choices,
        default=FriendshipStatus.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user1', 'user2')

    def __str__(self):
        return f"{self.user1.username} - {self.user2.username} - ({self.status})"
    
    def save(self, *args, **kwargs):
        if self.user1 == self.user2:
            raise ValueError("Users cannot be friends with themselves.")
        if self.user1.id > self.user2.id:
            self.user1, self.user2 = self.user2, self.user1

        existing_friendship = Friendship.objects.filter(
            user1=self.user1,
            user2=self.user2,
        ).first()

        if existing_friendship is None:
            super().save(*args, **kwargs)

        if existing_friendship:
            if existing_friendship.status == Friendship.FriendshipStatus.ACCEPTED:
                return
            elif existing_friendship.status == Friendship.FriendshipStatus.PENDING:
                existing_friendship.status = Friendship.FriendshipStatus.ACCEPTED
                existing_friendship.save()
                self.status = Friendship.FriendshipStatus.ACCEPTED
                return
            
    @classmethod
    def remove_friendship(cls, user1, user2):
        if user1 == user2:
            raise ValueError("Users cannot be friends with themselves.")
        friendship = Friendship.objects.filter(
            models.Q(user1=user1, user2=user2) | models.Q(user1=user2, user2=user1)
        ).first()
        if friendship:
            friendship.delete()
            return True
        return False


class Playlist(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='playlists')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    songs = models.ManyToManyField(Song, related_name='playlists')
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
            return self.owner.get_friend_status(user) == Friendship.FriendshipStatus.ACCEPTED
        return False
