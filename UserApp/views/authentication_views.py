from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from dotenv import load_dotenv
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from UserApp.utils import sign_in_app, sign_in_web
from rest_framework.parsers import JSONParser
from django.http import JsonResponse


load_dotenv()

@csrf_exempt
def googleSignIn(request):  
    if request.method=='POST':
        return sign_in_app(request)

@csrf_exempt
def adminPanelGoogleSignIn(request):
    if request.method=='POST':
        return sign_in_web(request)

@csrf_exempt
@staticmethod
def accessTokenValidate(request):
    if request.method=='POST':
        data = JSONParser().parse(request)
        token = data['access_token']

        try:
            access_token = AccessToken(token)
            current_time = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
            token_expires_at = access_token['exp']
            token_expiry_time = datetime.fromtimestamp(token_expires_at).strftime("%Y-%m-%d %H:%M:%S")

            if (access_token and current_time < token_expiry_time):
                return JsonResponse({'valid': True})
            else:
                return JsonResponse({'valid': False, 'error': 'Access token has expired'})

        except Exception as e:
            return JsonResponse({'valid': False, 'error': str(e)})

@csrf_exempt
def refreshToken(request):   
    if request.method=='POST':
        data = JSONParser().parse(request)
        refresh_token = data['refresh_token']

        if not refresh_token:
            return JsonResponse({'error': 'Refresh token is missing'}, status=400)    
        try:
            refresh_token_obj = RefreshToken(refresh_token)
            if not refresh_token_obj.token:
                return JsonResponse({'error': 'Invalid refresh token'}, status=400)        
            access_token = refresh_token_obj.access_token
            return JsonResponse({'access_token': str(access_token)})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)