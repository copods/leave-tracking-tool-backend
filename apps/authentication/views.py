from datetime import datetime
from google.oauth2 import id_token
from google.auth.transport import requests
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework.views import APIView
from rest_framework.response import Response
from dotenv import load_dotenv
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from apps.user.models import User

load_dotenv()

class GoogleSignInView(APIView):
    @csrf_exempt
    @staticmethod
    def post(self, request):
        token = request.data['token']
        email = request.data['email']

        #get platform from request
        platform = request.data['platform']

        try:
            id_info = id_token.verify_oauth2_token(token, requests.Request())
            if id_info['email'] != email:
                return Response({'error': 'Email mismatch'}, status=401)

            #check if user exists
            user = User.objects.get(email=email)

            #check platform and user's role
            if platform == 'web' and user.role.role_name not in {'ADMIN', 'SUPER-ADMIN'}:
                return Response({'error': 'Access denied, only admins are allowed'}, status=403)
            
            request.session['user_email'] = email
            access_token, refresh_token = generate_tokens(user)
            return Response({'access_token': str(access_token), 'refresh_token': str(refresh_token), 'user_role': user.role.role_name}, status=200)

        except User.DoesNotExist:
            return Response({'error': 'Email not registered'}, status=401)
        except ValueError:
            return Response({'error': 'Invalid token'}, status=400)
        except Exception as e:
            return Response({'error': str(e)}, status=400)


class AccessTokenValidateView(APIView):
   @csrf_exempt
   @staticmethod
   def post(self, request):
        token = request.data.get('access_token')

        #get platform and user_email from session
        platform = request.data.get('platform')
        user_email = request.session.get('user_email')

        try:
            #check if user exists
            user = User.objects.get(email=user_email)

            #check platform and user's role
            if platform == 'web' and user.role.role_name not in {'ADMIN', 'SUPER-ADMIN'}:
                return Response({'valid': False, 'error': 'Access denied, only admins are allowed'}, status=403)
            
            access_token = AccessToken(token)
            current_time = timezone.now()
            token_expires_at = access_token['exp']

            if current_time < datetime.fromtimestamp(token_expires_at):
                return Response({'valid': True})
            else:
                return Response({'valid': False, 'error': 'Access token has expired'})

        except User.DoesNotExist:
            return Response({'valid': False, 'error': 'User not found'}, status=404)
        except Exception as e:
            return Response({'valid': False, 'error': str(e)})


class RefreshTokenView(APIView):
    @csrf_exempt
    def post(self, request):
        refresh_token = request.data.get('refresh_token')

        if not refresh_token:
            return Response({'error': 'Refresh token is missing'}, status=400)

        #get platform and user_email from session
        platform = request.data.get('platform')
        user_email = request.session.get('user_email')

        try:
            #check if user exists
            user = User.objects.get(email=user_email)

            #check platform and user's role
            if platform == 'web' and user.role.role_name not in {'ADMIN', 'SUPER-ADMIN'}:
                return Response({'valid': False, 'error': 'Access denied, only admins are allowed'}, status=403)
            
            refresh_token_obj = RefreshToken(refresh_token)
            if not refresh_token_obj.token:
                return Response({'error': 'Invalid refresh token'}, status=400)
            
            access_token = refresh_token_obj.access_token
            return Response({'access_token': str(access_token)})

        except User.DoesNotExist:
            return Response({'valid': False, 'error': 'User not found'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=400)



def generate_tokens(user):
    access_token = AccessToken.for_user(user)
    refresh_token = RefreshToken.for_user(user)
    return access_token, refresh_token
