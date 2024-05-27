from django.urls import path
from apps.role.views import *
from apps.user.views import *
from apps.authentication.views import *
from rest_framework_simplejwt import views as jwt_views

urlpatterns = [
    # USER APIs
    path('v1/user/', UserListCreateAPIView.as_view(), name='user'),
    path('v1/user/<int:pk>', UserRetrieveUpdateDestroyAPIView.as_view(), name='user-details'),
    path('token/', jwt_views.TokenObtainPairView.as_view(), name='token-obtain-pair-view'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token-refresh'),
    path('v1/approver-list/', ApproverListView.as_view() , name='approvers'),
    
    #ROLE APIs
    path('v1/role/', GetPostRoles.as_view(), name='role'),
    path('v1/role/<int:pk>', GetPutDeleteRole.as_view(), name='role-details'),


    #Google Sign In APIs
    path('v1/authenticate', GoogleSignInView.as_view(), name='googleSignIn'),
    path('v1/validate', AccessTokenValidateView.as_view(), name='validate_token'),
    path('v1/refresh', RefreshTokenView.as_view(), name='refresh_token'),

    # Endpoint for web app sign in
    path('v1/admin/authenticate', AdminPanelGoogleSignInView.as_view(), name='googleSignIn'),
]
