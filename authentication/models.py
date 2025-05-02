from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User

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
