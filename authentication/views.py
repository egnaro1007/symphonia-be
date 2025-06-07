from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Friendship, FriendRequest, UserProfile
from .serializers import RegisterUserSerializer, UserProfilePictureSerializer, UserProfileSerializer

class RegisterUserAPIView(APIView):
    def post(self, request):
        serializer = RegisterUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User register successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response({"error": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)
        
        user.delete()
        return Response({"message": "Your account has been deleted successfully."}, status=status.HTTP_200_OK)

class UpdateProfilePictureAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    
    def post(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response({"error": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Get or create UserProfile for the user with default values
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'first_name': 'Jane',
                'last_name': 'Doe',
                'gender': 'O',
                'birth_date': '2000-01-01',
                'email': None,
                'profile_picture': None
            }
        )
        
        # Delete old profile picture if it exists
        if profile.profile_picture:
            old_picture = profile.profile_picture
            # Delete the physical file
            if old_picture.name:
                old_picture.delete(save=False)
        
        serializer = UserProfilePictureSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Profile picture updated successfully",
                "profile_picture_url": profile.profile_picture_url
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response({"error": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            profile = user.profile
            if profile.profile_picture:
                profile.profile_picture.delete()
                profile.profile_picture = None
                profile.save()
                return Response({
                    "message": "Profile picture deleted successfully",
                    "profile_picture_url": profile.profile_picture_url  # This will return default avatar URL
                }, status=status.HTTP_200_OK)
            else:
                return Response({"error": "No profile picture to delete"}, status=status.HTTP_400_BAD_REQUEST)
        except UserProfile.DoesNotExist:
            return Response({"error": "User profile not found"}, status=status.HTTP_404_NOT_FOUND)

class SearchUserAPIView(APIView):
    def get(self, request):
        user = request.user
        query = request.query_params.get('query', '')
        max_results = int(request.query_params.get('max_results', 10))
        if not query:
            return Response({"error": "query parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        results = User.objects.filter(username__icontains=query)
        
        if user.is_authenticated:
            results = results.exclude(id=user.id)
            results = results[:max_results]  # Limit to max_results
            user_data = [{
                "id": result.id, 
                "username": result.username, 
                "relationships_status": user.get_friend_status(result),
                "profile_picture_url": result.get_profile_picture_url()
            } for result in results]
        else:
            results = results[:max_results]  # Also limit results for unauthenticated users
            user_data = [{
                "id": result.id, 
                "username": result.username,
                "relationships_status": "none",
                "profile_picture_url": result.get_profile_picture_url()
            } for result in results]
        
        return Response(user_data, status=status.HTTP_200_OK)

class GetUserInfoAPIView(APIView):
    def get(self, request, requested_user_id=None):
        user = request.user

        if not user.is_authenticated:
            return Response({"error": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)
        

        if not requested_user_id:
            # Get profile info for current user
            profile_picture_url = user.get_profile_picture_url()
            try:
                profile = user.profile
                user_data = {
                    "id": user.id,
                    "username": user.username,
                    "email": profile.email,
                    "first_name": profile.first_name,
                    "last_name": profile.last_name,
                    "gender": profile.gender,
                    "birth_date": profile.birth_date,
                    "profile_picture_url": profile_picture_url,
                    "relationships_status": "none"
                }
            except UserProfile.DoesNotExist:
                # Create profile if it doesn't exist with default values
                profile = UserProfile.objects.create(
                    user=user,
                    first_name='Jane',
                    last_name='Doe',
                    gender='O',
                    birth_date='2000-01-01',
                    email=None,
                    profile_picture=None
                )
                user_data = {
                    "id": user.id,
                    "username": user.username,
                    "email": profile.email,
                    "first_name": profile.first_name,
                    "last_name": profile.last_name,
                    "gender": profile.gender,
                    "birth_date": profile.birth_date,
                    "profile_picture_url": profile_picture_url,
                    "relationships_status": "none"
                }
        else:
            try:
                requested_user = User.objects.get(id=requested_user_id)

            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

            # Get profile info for requested user
            profile_picture_url = requested_user.get_profile_picture_url()
            try:
                profile = requested_user.profile
                user_data = {
                    "id": requested_user.id,
                    "username": requested_user.username,
                    "email": profile.email,
                    "first_name": profile.first_name,
                    "last_name": profile.last_name,
                    "gender": profile.gender,
                    "birth_date": profile.birth_date,
                    "profile_picture_url": profile_picture_url,
                    "relationships_status": user.get_friend_status(requested_user)
                }
            except UserProfile.DoesNotExist:
                # Create profile if it doesn't exist with default values
                profile = UserProfile.objects.create(
                    user=requested_user,
                    first_name='Jane',
                    last_name='Doe',
                    gender='O',
                    birth_date='2000-01-01',
                    email=None,
                    profile_picture=None
                )
                user_data = {
                    "id": requested_user.id,
                    "username": requested_user.username,
                    "email": profile.email,
                    "first_name": profile.first_name,
                    "last_name": profile.last_name,
                    "gender": profile.gender,
                    "birth_date": profile.birth_date,
                    "profile_picture_url": profile_picture_url,
                    "relationships_status": user.get_friend_status(requested_user)
                }
        
        return Response(user_data, status=status.HTTP_200_OK)    

class UpdateUserProfileAPIView(APIView):
    def put(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response({"error": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Get or create UserProfile for the user with default values
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'first_name': 'Jane',
                'last_name': 'Doe',
                'gender': 'O',
                'birth_date': '2000-01-01',
                'email': None,
                'profile_picture': None
            }
        )
        
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Profile updated successfully",
                "profile": serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GetUserIDFromUsernameAPIView(APIView):
    def post(self, request):
        username = request.data.get('username')
        if not username:
            return Response({"error": "username field is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(username=username)
            return Response({"user_id": user.id}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

class FriendRequestAPIView(APIView):
    def post(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response({"error": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)

        friend_id = request.data.get('id')
        friend_username = request.data.get('username')
        if not friend_id and not friend_username:
            return Response({"error": "id or username field is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        if friend_id:
            try:
                friend = User.objects.get(id=friend_id)
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        elif friend_username:
            try:
                friend = User.objects.get(username=friend_username)
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        try:    
            user.send_friend_request(friend)
        except ValueError as e:
            return Response({"message": str(e)}, status=status.HTTP_200_OK)
        
        return Response({"message": "Friend request sent successfully"}, status=status.HTTP_201_CREATED)
    
    def get(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response({"error": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)
        
        friends = [
            {
                "id": friend.id,
                "username": friend.username,
                "profile_picture_url": friend.get_profile_picture_url()
            }
            for friend in user.get_friends()
        ]
        sent_requests_data = [
            {
                "id": request.id,  
                "receiver_user_id": request.receiver.id,
                "receiver_username": request.receiver.username
            }
            for request in user.get_sent_friend_requests()
        ]
        received_requests_data = [
            {
                "id": request.id,
                "sender_user_id": request.sender.id,
                "sender_username": request.sender.username,
                "profile_picture_url": request.sender.get_profile_picture_url()
            }
            for request in user.get_received_friend_requests()
        ]
        
        return Response({
            "friends": friends,
            "sent_requests": sent_requests_data,
            "received_requests": received_requests_data
        }, status=status.HTTP_200_OK)
    
class ResponseFriendRequestAPIView(APIView):
    def post(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response({"error": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)

        id = request.data.get('id')
        sender_user_id = request.data.get('user_id')
        if not id and not sender_user_id:
            return Response({"error": "id or user_id fields are required"}, status=status.HTTP_400_BAD_REQUEST)
        if id:
            friend_request = FriendRequest.objects.filter(id=id).first()
        elif sender_user_id:
            friend_request = FriendRequest.objects.filter(sender_id=sender_user_id, receiver_id=user.id).first()
        
        if not friend_request:
            return Response({"error": "Friend request not found"}, status=status.HTTP_404_NOT_FOUND)
        if friend_request.receiver != user:
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        
        response = request.data.get('response')
        if response not in ['accept', 'reject']:
            return Response({"error": "response field must be 'accept' or 'reject'"}, status=status.HTTP_400_BAD_REQUEST)
        
        if response == 'accept':
            friend_request.accept()
            return Response({"message": "Friend request accepted"}, status=status.HTTP_200_OK)
        elif response == 'reject':
            friend_request.reject()
            return Response({"message": "Friend request rejected"}, status=status.HTTP_200_OK)
        
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
class UnfriendAPIView(APIView):
    def post(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response({"error": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)

        friend_id = request.data.get('id')
        friend_username = request.data.get('username')
        if not friend_id and not friend_username:
            return Response({"error": "id or username field is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            if friend_id:
                friend = User.objects.get(id=friend_id)
            elif friend_username:
                friend = User.objects.get(username=friend_username)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        if not user.is_friend_with(friend):
            return Response({"error": "You are not friends with this user"}, status=status.HTTP_400_BAD_REQUEST)
        
        done = Friendship.remove_friendship(user, friend)
        if done: 
            return Response({"message": "Unfriended successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Failed to unfriend"}, status=status.HTTP_400_BAD_REQUEST)
