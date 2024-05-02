from django.urls import path
from apps.user.views import UserListCreateAPIView, UserRetrieveUpdateDestroyAPIView
from apps.user import views
from apps.authentication.views import GoogleSignInView,AccessTokenValidateView, RefreshTokenView
from rest_framework_simplejwt import views as jwt_views


urlpatterns = [
    #USER API's
    path('v1/user/', UserListCreateAPIView.as_view(), name='user'),
    path('v1/user/<int:pk>', UserRetrieveUpdateDestroyAPIView.as_view(), name='user-details'),
  
    #Google Sign In API's
    path('v1/authenticate', GoogleSignInView.as_view(), name='googleSignIn'),
    path('v1/validate', AccessTokenValidateView.as_view(), name='validate_token'),
    path('v1/refresh', RefreshTokenView.as_view(), name='refresh_token'),
]
    



