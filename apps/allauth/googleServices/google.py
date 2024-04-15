# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
# from allauth.socialaccount.providers.oauth2.client import OAuth2Client
# from rest_auth.registration.views import SocialLoginView
# from rest_framework_simplejwt.tokens import RefreshToken
# from apps.user.serializers import UserSerializer
# from apps.user.models import User

# class GoogleLoginAPIView(APIView):
#     def post(self, request, *args, **kwargs):
#         adapter = GoogleOAuth2Adapter()
#         client = adapter.get_provider().get_client(request)
#         code = request.data.get('code')
#         token = client.get_access_token(code)

#         # Retrieve user info from Google
#         user_info = client.userinfo()

#         # Check if user with email already exists
#         try:
#             user = User.objects.get(email=user_info['email'])
#         except User.DoesNotExist:
#             # Create a new user if not exists
#             user = User.objects.create_user(email=user_info['email'], username=user_info['email'])

#         # Generate JWT tokens
#         refresh = RefreshToken.for_user(user)

#         return Response({
#             'access_token': str(refresh.access_token),
#             'refresh_token': str(refresh),
#             'user': UserSerializer(user).data
#         }, status=status.HTTP_200_OK)
