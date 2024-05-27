from google.oauth2 import id_token
from google.auth.transport import requests
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

#Global sign in function
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
