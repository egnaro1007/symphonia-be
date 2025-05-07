from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Friendship, FriendRequest
from .serializers import RegisterUserSerializer

class RegisterUserAPIView(APIView):
    def post(self, request):
        serializer = RegisterUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User register successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
                "relationships_status": user.get_friend_status(result)
            } for result in results]
        else:
            results = results[:max_results]  # Also limit results for unauthenticated users
            user_data = [{
                "id": result.id, 
                "username": result.username,
                "relationships_status": "none"
            } for result in results]
        
        return Response(user_data, status=status.HTTP_200_OK)

class GetUserInfoAPIView(APIView):
    def get(self, request, requested_user_id=None):
        user = request.user

        if not user.is_authenticated:
            return Response({"error": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)
        

        if not requested_user_id:
            user_data = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "relationships_status": "none"
            }
        else:
            try:
                requested_user = User.objects.get(id=requested_user_id)

            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

            user_data = {
                "id": requested_user.id,
                "username": requested_user.username,
                "email": requested_user.email,
                "first_name": requested_user.first_name,
                "last_name": requested_user.last_name,
                "relationships_status": user.get_friend_status(requested_user)
            }
        
        return Response(user_data, status=status.HTTP_200_OK)    

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
                "username": friend.username
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
                "sender_username": request.sender.username
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
