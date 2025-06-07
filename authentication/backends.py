from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from .models import UserProfile


class EmailOrUsernameBackend(ModelBackend):
    """
    Custom authentication backend that allows users to log in with either
    their username or email address.
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            return None
            
        try:
            # First try to find user by username
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # If not found by username, try to find by email in UserProfile
            try:
                # Find UserProfile with matching email
                profile = UserProfile.objects.get(email=username)
                user = profile.user
            except UserProfile.DoesNotExist:
                return None
        
        # Check if the password is correct
        if user.check_password(password):
            return user
        
        return None 