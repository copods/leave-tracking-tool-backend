from google.oauth2 import id_token
from google.auth.transport import requests
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework.response import Response
from apps.user.models import User

#util function to authenticate user and generate tokens
def authenticate_user(request, roles_allowed=None):
    token = request.data['token']
    email = request.data['email']

    try:
        id_info = id_token.verify_oauth2_token(token, requests.Request())
        if id_info['email'] != email:
            return Response({'error': 'Email mismatch'}, status=401)

        user = User.objects.get(email=email)
        if roles_allowed and user.role.role_name not in roles_allowed:
            return Response({'error': 'Access denied'}, status=403)

        access_token, refresh_token = generate_tokens(user)
        return Response({
            'access_token': str(access_token), 
            'refresh_token': str(refresh_token), 
            'user_role': user.role.role_name
            }, 
            status=200)

    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=401)
    except ValueError:
        return Response({'error': 'Invalid token'}, status=400)
    except Exception as e:
        return Response({'error': str(e)}, status=400)


def generate_tokens(user):
    access_token = AccessToken.for_user(user)
    refresh_token = RefreshToken.for_user(user)
    return access_token, refresh_token

