from UserApp.models import User
from google.oauth2 import id_token
from google.auth.transport import requests
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework.parsers import JSONParser
from django.http import JsonResponse

def isJWTValid(token):
    try:
        token = AccessToken(token)
        return token.__getitem__('user_id')  #user_id is set to have the email in the token (see base settings file)
    except:
        return False

def getRole(user_email):
    if user_email:
        try:
            user = User.objects.get(email=user_email)
            return user.role.role_name
        except:
            return False
    else:
        return False

def verify_google_id_token(token):
    try:
        id_info = id_token.verify_oauth2_token(token, requests.Request())
        return id_info
    except:
        return ''

def generate_tokens(user):
    access_token = AccessToken.for_user(user)
    refresh_token = RefreshToken.for_user(user)
    return access_token, refresh_token


def sign_in_web(request):
    data = JSONParser().parse(request)
    google_token = data['token']
    user_info = verify_google_id_token(google_token)

    if user_info != '':
        try:
            user = User.objects.get(email=user_info['email'])
            user.profile_image = user_info['picture']
            user.save()
            if user.role.role_key in {'admin', 'hr'}:
                access_token, refresh_token = generate_tokens(user)
                return JsonResponse({
                    'access_token': str(access_token), 
                    'refresh_token': str(refresh_token), 
                    'user_role': user.role.role_name,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'profile_image': user.profile_image
                }, status=200)
    
            else:
                return JsonResponse({'error': 'Access denied'}, status=403)
            
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    else:
        return JsonResponse({'error': 'Invalid token'}, status=498)

def sign_in_app(request):
    data = JSONParser().parse(request)
    google_token = data['token']
    user_info = verify_google_id_token(google_token)

    if user_info != '':
        try:
            user = User.objects.get(email=user_info['email'])
            user.profile_image = user_info['picture']
            user.app_registration_status = True
            user.save()
            access_token, refresh_token = generate_tokens(user)
            return JsonResponse({
                'access_token': str(access_token), 
                'refresh_token': str(refresh_token),
                'user_id': user.id,
                'user_role': user.role.role_name,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'profile_image': user.profile_image,
            })
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    else:
        return JsonResponse({'error': 'Invalid token'}, status=498)
