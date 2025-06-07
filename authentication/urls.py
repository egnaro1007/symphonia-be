from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from authentication.views import RegisterUserAPIView, SearchUserAPIView, GetUserInfoAPIView, GetUserIDFromUsernameAPIView
from authentication.views import FriendRequestAPIView, ResponseFriendRequestAPIView, UnfriendAPIView, UpdateProfilePictureAPIView, UpdateUserProfileAPIView, ChangePasswordAPIView


urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify', TokenVerifyView.as_view(), name='token_verify'),

    path('register/', RegisterUserAPIView.as_view(), name='register_user'),

    path('search_user/', SearchUserAPIView.as_view(), name='search_user'),
    path('get_user_info/', GetUserInfoAPIView.as_view(), name='get_user_info'),
    path('get_user_info/<int:requested_user_id>/', GetUserInfoAPIView.as_view(), name='get_user_info'),
    path('get_user_id/', GetUserIDFromUsernameAPIView.as_view(), name='get_user_id_from_username'),
    path('friend_request/', FriendRequestAPIView.as_view(), name='friend_request'),
    path('response_friend_request/', ResponseFriendRequestAPIView.as_view(), name='response_friend_request'),
    path('unfriend/', UnfriendAPIView.as_view(), name='unfriend'),
    path('update_profile_picture/', UpdateProfilePictureAPIView.as_view(), name='update_profile_picture'),
    path('update_profile/', UpdateUserProfileAPIView.as_view(), name='update_user_profile'),
    path('change-password/', ChangePasswordAPIView.as_view(), name='change_password'),
]
