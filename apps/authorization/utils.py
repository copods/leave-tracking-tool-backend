from rest_framework_simplejwt.tokens import AccessToken
from apps.user.models import User

def isJWTValid(token):
    try:
        token = AccessToken(token)
        return token.__getitem__('user_id')  #user_id is set to have the email in the token (see base settings file)
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