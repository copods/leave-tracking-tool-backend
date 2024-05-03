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

def get_user(email):
    users = User.objects.filter(email=email)
    if users.count() > 1:
        user = users.first()
    else:
        user= User.objects.get(email=email)
    return user

def generate_tokens(user):
    access_token = AccessToken.for_user(user)
    refresh_token = RefreshToken.for_user(user)
    return access_token, refresh_token


class GoogleSignInView(APIView):
    @csrf_exempt
    @staticmethod
    def post(self,request):
        token = request.data.get('token')
        email = request.data.get('email')

        try:
            id_info = id_token.verify_oauth2_token(token, requests.Request())
            if id_info['email'] == email:
                request.session['user_email'] = email
                user = get_user(email)
                access_token, refresh_token = generate_tokens(user)
                return Response({
                    'access_token': str(access_token),
                    'refresh_token': str(refresh_token),
                })
            else:
                return Response({'error': 'Invalid Credentials.'}, status=400)
        except ValueError as e:
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
            return Response({'error': str(e)}, status=400)
