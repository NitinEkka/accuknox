from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterAPIView.as_view()),
    path('login/', views.LoginAPIView.as_view()),
    path('logout/', views.LogoutAPI.as_view()),
    path('search/', views.UserSearchView.as_view()),
    path('req-action/', views.FriendRequestAPIView.as_view()),
    path('req-action/<int:pk>/', views.FriendRequestAPIView.as_view()),
    path('friend-request/', views.FriendRequestsStatusAPIView.as_view())
]