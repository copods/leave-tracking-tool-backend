from django.utils import timezone
from PushNotificationApp.models import FCMToken, Notification
import firebase_admin
from firebase_admin import credentials, messaging
import os

server_key = {
  "type": os.environ.get('TYPE'),
  "project_id": os.environ.get('PROJECT_ID'),
  "private_key_id": os.environ.get('PRIVATE_KEY_ID'),
  "private_key": os.environ.get('PRIVATE_KEY'),
  "client_email": os.environ.get('CLIENT_EMAIL'),
  "client_id": os.environ.get("CLIENT_ID"),
  "auth_uri": os.environ.get("AUTH_URI"),
  "token_uri": os.environ.get("TOKEN_URI"),
  "auth_provider_x509_cert_url": os.environ.get("AUTH_PROVIDER_x509_CERT_URL"),
  "client_x509_cert_url": os.environ.get("CLIENT_x509_CERT_URL"),
  "universe_domain": os.environ.get("UNIVERSE_DOMAIN")
}

# Initialize Firebase app
firebase_cred = credentials.Certificate(server_key)
firebase_app = firebase_admin.initialize_app(firebase_cred)

def multi_fcm_tokens_validate(fcm_tokens):
    try:
        valid_fcm_tokens = []
        for fcm_token in fcm_tokens:
            current_time = timezone.now()
            if current_time < fcm_token.expires_at:
                valid_fcm_tokens.append(fcm_token.fcm_token)
            else:
                fcm_token.delete()
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


# Create Notification
def send_notification(notification_data, recievers):
    errors = []
    # Create Notification
    try:
        notification = Notification(**notification_data)
        notification.save()
    except Exception as e:
        errors.append(e)

    fcm_tokens_queryset = FCMToken.objects.filter(user_id__in=recievers)

    # Send Push Notification
    valid_tokens = multi_fcm_tokens_validate(fcm_tokens_queryset)
    if valid_tokens:
        response = send_token_push(notification_data['title'], notification_data['subtitle'], valid_tokens)
        if not 'success' in response:
            errors.append(response['error'])

    return errors