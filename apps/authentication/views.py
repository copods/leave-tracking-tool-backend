from datetime import datetime
from django.http import JsonResponse
from google.oauth2 import id_token
from google.auth.transport import requests
import os
from django.core.exceptions import MultipleObjectsReturned
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from dotenv import load_dotenv
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

load_dotenv()

class GoogleSignInView(APIView):
    @csrf_exempt
    @staticmethod
    def post(self,request):
        token = request.data['token']
        email = request.data['email']

        #getting the platform from which the user is logging in
        platform = request.data.get('platform')

        try:
            #verify token and email
            id_info = id_token.verify_oauth2_token(token, requests.Request())
            if id_info['email'] == email:
                try:
                    #check if user exists
                    user = User.objects.get(email=email)

                    #check platform type and user's role
                    if platform == 'web' and user.role not in {'ADMIN', 'SUPER-ADMIN'}:
                        return Response({'error': 'Access denied, only admins are allowed'}, status=403)
                    else:
                        request.session['user_email'] = email
                        access_token, refresh_token = generate_tokens(user)
                        return Response({'access_token': str(access_token), 'refresh_token': str(refresh_token), 'user_role': user.role}, status=200)
                except User.DoesNotExist:
                    return Response({'error': 'Email not registered'}, status=401)
            else:
                return Response({'error': 'Email mismatch'}, status=401)
        except ValueError:
            return Response({'error': 'Invalid token'}, status=400)
        except Exception as e:
            return Response({'error': str(e)}, status=400)


class AccessTokenValidateView(APIView):
    @csrf_exempt
    @staticmethod
    def post(self,request):
        token = request.data.get('access_token')
        try:
            access_token = AccessToken(token)
            current_time = timezone.now()
            token_expires_at = access_token['exp']

            if (access_token):
                if current_time < datetime.fromtimestamp(token_expires_at):
                    return Response({'valid': True})
                else:
                    return Response({'valid': False, 'error': 'Access token has expired'})

        except Exception as e:
            return Response({'valid': False, 'error': str(e)})

class RefreshTokenView(APIView):
    @csrf_exempt
    def post(self,request):
        
        refresh_token = request.data.get('refresh_token')
        if not refresh_token:
            return Response({'error': 'Refresh token is missing'}, status=400)
        
        try:
            refresh_token_obj = RefreshToken(refresh_token)
            if not refresh_token_obj.token:
                return Response({'error': 'Invalid refresh token'}, status=400)
            
            access_token = refresh_token_obj.access_token
            return Response({'access_token': str(access_token)})
        except Exception as e:
            print(str(e))
            return Response({'error': str(e)}, status=400)



def generate_tokens(user):
    access_token = AccessToken.for_user(user)
    refresh_token = RefreshToken.for_user(user)
    return access_token, refresh_token
