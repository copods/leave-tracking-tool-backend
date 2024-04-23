from django.urls import path
from apps.user.views import UserListCreateAPIView, UserRetrieveUpdateDestroyAPIView
from apps.user import views
from apps.authentication.views import googleSignIn, validate_token
from rest_framework_simplejwt import views as jwt_views
from allauth.account.views import LoginView
# from apps.auth.googleServices.google import GoogleLoginAPIView
from apps.allauth.accounts import views

urlpatterns = [
    #USER API's
    path('v1/user/', UserListCreateAPIView.as_view(), name='user'),
    path('v1/user/<int:pk>', UserRetrieveUpdateDestroyAPIView.as_view(), name='user-details'),
    path('token/', jwt_views.TokenObtainPairView.as_view(), name='token-obtain-pair-view'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token-refresh'),
    


    path('v1/authenticate', googleSignIn , name='googleSignIn'),
    path('v1/validate', validate_token , name='validate_token'),
    
    # path('login/', LoginView.as_view(), name='signup'),
    # path("profile/", views.profile),
    # path('home/', views.home),
    # path('logout/', views.logout_view),
    # path('auth/google/', GoogleLoginAPIView.as_view(), name='google-login'),
]


