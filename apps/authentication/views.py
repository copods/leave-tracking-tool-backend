from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from dotenv import load_dotenv
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .util_functions import authenticate_user

load_dotenv()

class GoogleSignInView(APIView):
    @csrf_exempt
    @staticmethod
    def post(self, request):
        return authenticate_user(request)

class AdminPanelGoogleSignInView(APIView):
    @csrf_exempt
    @staticmethod
    def post(self, request):
        return authenticate_user(request, roles_allowed={'ADMIN', 'SUPER-ADMIN'})


class AccessTokenValidateView(APIView):
    @csrf_exempt
    @staticmethod
    def post(self, request):
        token = request.data.get('access_token')
        try:
            access_token = AccessToken(token)
            current_time = timezone.now()
            token_expires_at = access_token['exp']
            if (access_token and current_time < datetime.fromtimestamp(token_expires_at)):
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
