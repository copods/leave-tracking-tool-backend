from django.utils import timezone
from PushNotificationApp.models import FCMToken
# from UserApp.decorators import user_is_authorized
from UserApp.models import User
from rest_framework.parsers import JSONParser
from rest_framework import status
from django.http import JsonResponse

# #@user_is_authorized
def fcm_token_validate(request):
    user_email="chandani.mourya@copods.co"
    user = User.objects.get(email=user_email)
    user_id = user.id 
    print("validate : ",request)
    token = request
    print(token)
    fcm_token = FCMToken.objects.filter(fcm_token=token, user_id=user_id).first()
    try:
        if fcm_token:
            current_time = timezone.now()
            token_expires_at = fcm_token.expires_at
            if current_time < token_expires_at:
                return {'valid': True}
            else:
                fcm_token.delete()
                return {'valid': False, 'error': 'FCM token has expired. Token deleted.'}
        else:
            return {'valid': False, 'error': 'FCM token not found for the user'}
    except Exception as e:
        return {'valid': False, 'error': str(e)}

def fcm_token_list(user_id):
    try:
        user_fcm_tokens = FCMToken.objects.filter(user_id=user_id).values_list('fcm_token', flat=True)
        print(list(user_fcm_tokens))
    except Exception as e:
        raise e

def multi_fcm_tokens_validate(fcm_tokens):
    try:
        valid_fcm_tokens = []
        for fcm_token in fcm_tokens:
            response = fcm_token_validate(fcm_token)
            if response['valid']:
                valid_fcm_tokens.append(fcm_token)   
        return valid_fcm_tokens
        # return JsonResponse({'valid_fcm_tokens': valid_fcm_tokens}, status = status.HTTP_200_OK)
    except Exception as e:
        raise e
    
