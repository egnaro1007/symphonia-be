from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import os
from uuid import uuid4

def user_profile_picture_path(instance, filename):
    """
    Generate file path for user profile picture.
    File will be saved to MEDIA_ROOT/profile_pictures/{user_id}.{extension}
    """
    # Get file extension
    ext = filename.split('.')[-1]
    # Create filename using user ID
    filename = f"{instance.user.id}.{ext}"
    return os.path.join('profile_pictures', filename)

# UserProfile model to store additional user information like profile picture
class UserProfile(models.Model):
    GENDER_CHOICES = [
        ('M', 'Nam'),
        ('F', 'Nữ'),
        ('O', 'Khác'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(upload_to=user_profile_picture_path, blank=True, null=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True, unique=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    birth_date = models.DateField(default='2000-01-01')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Convert empty email string to None to ensure unique constraint works properly
        if self.email == '':
            self.email = None
        super().save(*args, **kwargs)

    def __str__(self):
        email_info = f" ({self.email})" if self.email else ""
        return f"{self.user.username}'s Profile{email_info}"

    @property
    def profile_picture_url(self):
        if self.profile_picture:
            return self.profile_picture.url
        # Return None if no profile picture is set - let frontend handle default
        return None

# Add method to User model to get profile picture
def get_profile_picture_url(self):
    try:
        return self.profile.profile_picture_url
    except UserProfile.DoesNotExist:
        # Create a profile if it doesn't exist with default values
        UserProfile.objects.create(
            user=self,
            first_name='Jane',
            last_name='Doe',
            gender='O',  # 'O' for Khác
            birth_date='2000-01-01',
            email=None,  # để trống
            profile_picture=None  # để trống (avatar)
        )
        return None

User.add_to_class('get_profile_picture_url', get_profile_picture_url)

User.add_to_class(
    'get_friends',
    lambda self: (
        [
            friendship.user2 if friendship.user1 == self else friendship.user1
            for friendship in Friendship.objects.filter(Q(user1=self) | Q(user2=self))
        ]
    )
)
User.add_to_class(
    'send_friend_request',
    lambda self, user: (
        FriendRequest.objects.create(sender=self, receiver=user)
    )
)
User.add_to_class(
    'get_sent_friend_requests',
    lambda self: (
        FriendRequest.objects.filter(sender=self)
    )
)

User.add_to_class(
    'get_received_friend_requests',
    lambda self: (
        FriendRequest.objects.filter(receiver=self)
    )
)
User.add_to_class(
    'get_friend_status',
    lambda self, user: (
        "friend" if Friendship.objects.filter(Q(user1=self, user2=user) | Q(user1=user, user2=self)).exists()
        else "pending_sent" if FriendRequest.objects.filter(sender=self, receiver=user).exists()
        else "pending_received" if FriendRequest.objects.filter(sender=user, receiver=self).exists()
        else "none"
    )
)
User.add_to_class(
    'is_friend_with',
    lambda self, user: (
        Friendship.objects.filter(Q(user1=self, user2=user) | Q(user1=user, user2=self)).exists()
    )
)
User.add_to_class(
    'accept_friend_request',
    lambda self, user: (
        (friendrequest := FriendRequest.objects.filter(sender=user, receiver=self).first())
        and friendrequest.accept()
        or (_ for _ in ()).throw(ValueError("Friend request not found."))
    )
)
User.add_to_class(
    'reject_friend_request',
    lambda self, user: (
        (friendrequest := FriendRequest.objects.filter(sender=user, receiver=self).first())
        and friendrequest.reject()
        or (_ for _ in ()).throw(ValueError("Friend request not found."))
    )
)
User.add_to_class(
    'remove_friend',
    lambda self, user: (
        FriendRequest.objects.filter(sender=self, receiver=user).delete() or
        FriendRequest.objects.filter(sender=user, receiver=self).delete() or
        Friendship.remove_friendship(self, user)
    )
)


class FriendRequest(models.Model):
    sender = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_requests', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('sender', 'receiver')

    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username}"
    
    def save(self, *args, **kwargs):
        if self.sender == self.receiver:
            raise ValueError("A user cannot send a friend request to themselves.")

        if FriendRequest.objects.filter(sender=self.sender, receiver=self.receiver).exists():
            raise ValueError("Friend request already exists.")
        
        reversed_request = FriendRequest.objects.filter(sender=self.receiver, receiver=self.sender).first()
        if reversed_request:
            reversed_request.accept()
            return

        super().save(*args, **kwargs)

    def accept(self):
        try:
            Friendship.objects.create(user1=self.sender, user2=self.receiver)
        except ValueError:
            pass
        self.delete()

    def reject(self):
        self.delete()
        
class Friendship(models.Model):
    user1 = models.ForeignKey(User, related_name='friendship_user1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, related_name='friendship_user2', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user1', 'user2')

    def __str__(self):
        return f"{self.user1.username} <-> {self.user2.username}"
    
    def save(self, *args, **kwargs):
        if self.user1 == self.user2:
            raise ValueError("A user cannot be friends with themselves.")
        
        if self.user1.id > self.user2.id:
            self.user1, self.user2 = self.user2, self.user1

        if Friendship.objects.filter(user1=self.user1, user2=self.user2).exists():
            raise ValueError("Friendship already exists.")
    
        super().save(*args, **kwargs)

    @classmethod
    def remove_friendship(cls, user1, user2):
        if user1 == user2:
            raise ValueError("A user cannot be friends with themselves.")
        
        if user1.id > user2.id:
            user1, user2 = user2, user1

        friendship = cls.objects.get(user1=user1, user2=user2)
        if friendship:
            friendship.delete()
            return True
        return False

# Signal to automatically create UserProfile when User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(
            user=instance,
            first_name='Jane',
            last_name='Doe',
            gender='O',  # 'O' for Khác
            birth_date='2000-01-01',
            email=None,  # để trống
            profile_picture=None  # để trống (avatar)
        )

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(
            user=instance,
            first_name='Jane',
            last_name='Doe',
            gender='O',  # 'O' for Khác
            birth_date='2000-01-01',
            email=None,  # để trống
            profile_picture=None  # để trống (avatar)
        )