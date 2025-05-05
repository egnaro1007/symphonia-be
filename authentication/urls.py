from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from authentication.views import RegisterUserAPIView, SearchUserAPIView, GetUserIDFromUsernameAPIView, FriendRequestAPIView, ResponseFriendRequestAPIView


urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify', TokenVerifyView.as_view(), name='token_verify'),

    path('register/', RegisterUserAPIView.as_view(), name='register_user'),

    path('get_user_id/', GetUserIDFromUsernameAPIView.as_view(), name='get_user_id_from_username'),
    path('friend_request/', FriendRequestAPIView.as_view(), name='friend_request'),
    path('response_friend_request/', ResponseFriendRequestAPIView.as_view(), name='response_friend_request'),
    path('search_user/', SearchUserAPIView.as_view(), name='search_user')
]
