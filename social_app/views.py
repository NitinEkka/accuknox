from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import login, logout
from rest_framework.generics import RetrieveUpdateDestroyAPIView,ListCreateAPIView, ListAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView
from .models import FriendReq, CustomUser
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer, FriendRequestSerializer
from django.db.models import Q
from .pagination import CustomPagination
from datetime import timedelta
from django.utils import timezone
from rest_framework.exceptions import ValidationError



class RegisterAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)

        return Response({"token": "Login successful"}, status=status.HTTP_200_OK)

class LogoutAPI(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            logout(request)
            return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
        except Exception as error:
            return Response({"message": str(error)}, status=status.HTTP_400_BAD_REQUEST) 

class UserSearchView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        keyword = self.request.query_params.get('search', None)
        queryset = CustomUser.objects.all()

        if keyword:
            queryset = queryset.filter(
                Q(email__iexact=keyword) |  # Match exact email
                Q(username__icontains=keyword) |  # Match part of the username
                Q(first_name__icontains=keyword) |  # Match part of the first name
                Q(last_name__icontains=keyword)  # Match part of the last name
            )
        
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_paginated_response(self.get_serializer(page, many=True).data)
        else:
            serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
        

class FriendRequestAPIView(CreateAPIView,UpdateAPIView,DestroyAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]
    queryset = FriendReq.objects.all()

    def post(self, request, *args, **kwargs):
        # Handle sending a friend request (Create)
        user_to_id = request.data.get('user_to')
        user_from = request.user

        if user_from.id == user_to_id:
            return Response({"error": "You cannot send a friend request to yourself."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the user has sent more than 3 friend requests in the last minute
        one_minute_ago = timezone.now() - timedelta(minutes=1)
        recent_requests_count = FriendReq.objects.filter(user_from=user_from, timestamp__gte=one_minute_ago).count()

        if recent_requests_count >= 3:
            return Response({"error": "You can only send 3 friend requests per minute."}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        # Check if a friend request already exists
        if FriendReq.objects.filter(user_from=user_from, user_to_id=user_to_id).exists():
            return Response({"error": "Friend request already sent."}, status=status.HTTP_400_BAD_REQUEST)

        user_to = CustomUser.objects.get(id=user_to_id)
        friend_request = FriendReq.objects.create(user_from=user_from, user_to=user_to)

        return Response(FriendRequestSerializer(friend_request).data, status=status.HTTP_201_CREATED)

    def put(self, request, *args, **kwargs):
        # Handle accepting a friend request (Update)
        friend_request = self.get_object()
        print(friend_request)
        if friend_request.user_to != request.user:
            return Response({"error": "You can only accept friend requests sent to you."}, status=status.HTTP_403_FORBIDDEN)

        friend_request.status = "accepted"
        friend_request.save()

        return Response(FriendRequestSerializer(friend_request).data)

    def delete(self, request, *args, **kwargs):
        # Handle removing (rejecting or canceling) a friend request (Destroy)
        friend_request = self.get_object()

        if friend_request.user_from != request.user and friend_request.user_to != request.user:
            return Response({"error": "You can only delete your own friend requests."}, status=status.HTTP_403_FORBIDDEN)

        friend_request.delete()
        return Response({"message": "Friend request removed."}, status=status.HTTP_204_NO_CONTENT)


class FriendRequestsStatusAPIView(ListAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Get the status filter from query parameters (default is "pending")
        status_filter = self.request.query_params.get('status', 'pending').lower()
        
        # Ensure the status filter is either "pending" or "accepted"
        if status_filter not in ['pending', 'accepted']:
            raise ValidationError({"error": "Invalid status. Valid options are 'pending' or 'accepted'."})
        
        # Return friend requests for the logged-in user based on the status filter
        return FriendReq.objects.filter(user_to=self.request.user, status=status_filter)

