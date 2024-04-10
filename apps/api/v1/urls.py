from django.urls import path
from apps.user.views import UserListCreateAPIView, UserRetrieveUpdateDestroyAPIView

urlpatterns = [
    path('v1/user/', UserListCreateAPIView.as_view(), name='user'),
    path('v1/user/<int:pk>', UserRetrieveUpdateDestroyAPIView.as_view(), name='user-details')
]


