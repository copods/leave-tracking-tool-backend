from datetime import timedelta
from dotenv import load_dotenv
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from PushNotificationApp.models import FCMToken
from PushNotificationApp.serializers import FCMTokenSerializer
from PushNotificationApp.utils import fcm_token_list, fcm_token_validate, multi_fcm_tokens_validate
from UserApp.decorators import user_is_authorized
from UserApp.models import User
from rest_framework.parsers import JSONParser
from rest_framework import status
from django.http import JsonResponse

load_dotenv()

@csrf_exempt
# #@user_is_authorized
def fcmTokenStore(request):
    if request.method == 'POST':
        try:
            user_email = getattr(request, 'user_email', None) 
            user_email = "chandani.mourya@copods.co"
            user = User.objects.get(email=user_email)
            fcm_token_data = JSONParser().parse(request)
            # expires_at = timezone.now() + timedelta(days=60)
            expires_at = timezone.now() + timedelta(seconds=2)
            token = fcm_token_data.get('fcm_token')
            fcm_token = FCMToken.objects.filter(fcm_token=token, user_id=user.id).first()

            if fcm_token:
                return JsonResponse({'message': 'FCM token already exists'}, status = status.HTTP_200_OK)
            token_data = {
                'fcm_token': token,
                'expires_at': expires_at,
                'user': user.id
            }
            fcm_token_serializer = FCMTokenSerializer(data=token_data)
            if fcm_token_serializer.is_valid():
                fcm_token_serializer.save()
            else:
                errors = fcm_token_serializer.errors
                return JsonResponse({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)

            return JsonResponse({'message': 'Added FCM Tokens Successfully!!'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


        

@csrf_exempt
def fcmTokenValidate(request):
    if request.method == 'POST':
        try:
            fcm_token_data = JSONParser().parse(request)
            token = fcm_token_data.get('fcm_token')
            print("token: ", token)
            response = fcm_token_validate(token)
            print("response: ", response)
            if response['valid']:
                return JsonResponse({'valid': True}, status=status.HTTP_200_OK)
            else:
                return JsonResponse({'valid': False, 'error': response['error']}, status=status.HTTP_200_OK if 'expired' in response['error'] else status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({'valid': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@csrf_exempt
def FCMTokenList(request):
    if request.method=='GET':
        response = fcm_token_list(request)
        print("Response", response)
        return response
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)





@csrf_exempt
def MultiplefcmTokensValidate(request):
    if request.method=='POST':
        fcm_token_data = JSONParser().parse(request)
        fcm_tokens = fcm_token_data.get('fcm_tokens', [])
        response = multi_fcm_tokens_validate(fcm_tokens)
        print("Response", response)
        return response
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


