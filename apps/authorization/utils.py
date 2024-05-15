from django.http import JsonResponse
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from apps.user.models import User

def isJWTValid(token):
    try:
        token = AccessToken(token)
        return token.__getitem__('email')
    except:
        return False

def getRole(user_email):
    if not user_email:
        return False
    try:
        user = User.objects.get(email=user_email)
        return user.role.role_name
    except:
        return False