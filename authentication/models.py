from django.db import models

from django.contrib.auth.models import User
from library.models import Friendship         

User.add_to_class(
    'get_friends',
    lambda self : [
        friendship.user2 if friendship.user1 == self else friendship.user1
        for friendship in Friendship.objects.filter(
            models.Q(user1=self) | models.Q(user2=self),
            status=Friendship.FriendshipStatus.ACCEPTED,
        )
    ] 
)
User.add_to_class(
    'get_friend_requests',
    lambda self : [
        friendship.user2 if friendship.user1 == self else friendship.user1
        for friendship in Friendship.objects.filter(
            models.Q(user1=self) | models.Q(user2=self),
            status=Friendship.FriendshipStatus.PENDING,
        )
    ]
)
User.add_to_class(
    'get_friend_status',
    lambda self, user: Friendship.objects.filter(
        models.Q(user1=self, user2=user) | models.Q(user1=user, user2=self)
    ).values_list('status', flat=True).first() or None
)
User.add_to_class(
    'accept_friend_request',
    lambda self, user: Friendship.objects.filter(
        models.Q(user1=self, user2=user) | models.Q(user1=user, user2=self),
        status=Friendship.FriendshipStatus.PENDING,
    ).update(status=Friendship.FriendshipStatus.ACCEPTED)
)
User.add_to_class(
    'reject_friend_request',
    lambda self, user: Friendship.objects.filter(
        models.Q(user1=self, user2=user) | models.Q(user1=user, user2=self),
        status=Friendship.FriendshipStatus.PENDING,
    ).delete()
)
User.add_to_class(
    'send_friend_request',
    lambda self, user: Friendship.objects.create(
        user1=self,
        user2=user,
        status=Friendship.FriendshipStatus.PENDING,
    )
)
User.add_to_class(
    'remove_friend',
    lambda self, user: Friendship.remove_friendship(self, user)
)
