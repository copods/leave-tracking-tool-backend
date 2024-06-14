from django.utils import timezone
from PushNotificationApp.models import FCMToken
from UserApp.models import User
from UserApp.decorators import user_is_authorized
import firebase_admin
from firebase_admin import credentials, messaging

server_key = 'PushNotificationApp/views/firebase.json'

# Initialize Firebase app
firebase_cred = credentials.Certificate(server_key)
firebase_app = firebase_admin.initialize_app(firebase_cred)

def fcm_token_validate(token, user_id):
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

def multi_fcm_tokens_validate(fcm_tokens):
    try:
        user_email = getattr(fcm_tokens, 'user_email', None) 
        user = User.objects.get(email=user_email)
        valid_fcm_tokens = []
        user_id = user.id
        for fcm_token in fcm_tokens:
            response = fcm_token_validate(fcm_token, user_id)
            if response['valid']:
                valid_fcm_tokens.append(fcm_token)   
        return valid_fcm_tokens
    except Exception as e:
        raise e
    
def send_token_push(title, body, tokens):
    message = messaging.MulticastMessage(
        notification=messaging.Notification(
            title=title,
            body=body
        ),
        tokens=tokens
    )
    response = messaging.send_multicast(message)
    try:
        if response.failure_count > 0:
            error_reasons = [str(res.exception) for res in response.responses if not res.success]
            return {
                'error': f'Failed to send to {response.failure_count} tokens due to: {", ".join(error_reasons)}'
            }
        else:
            return {
                'success': True,
                'message': 'Notification sent successfully to all tokens'}
    except Exception as e:
        return {'error': str(e)}
    