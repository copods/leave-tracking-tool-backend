from datetime import timedelta
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
from LeaveTrackingApp.models import Leave
from PushNotificationApp.models import FCMToken, Notification
from PushNotificationApp.serializers import FCMTokenSerializer, FetchNotificationsSerializer
from PushNotificationApp.utils import multi_fcm_tokens_validate
from rest_framework import status
from rest_framework.parsers import JSONParser
from UserApp.decorators import user_is_authorized
from UserApp.models import User

load_dotenv()

@csrf_exempt
@user_is_authorized
def fcmTokenStore(request):
    if request.method == 'POST':
        try:
            user_email = getattr(request, 'user_email', None) 
            user = User.objects.get(email=user_email)
            fcm_token_data = JSONParser().parse(request)
            expires_at = timezone.now() + timedelta(days=60)
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
@user_is_authorized
def fcmTokenValidate(request):
    if request.method == 'POST':
        try:
            fcm_token_data = JSONParser().parse(request)
            user_email = getattr(request, 'user_email', None) 
            user = User.objects.get(email=user_email)
            token = fcm_token_data.get('fcm_token', None)
            fcm_token = FCMToken.objects.filter(fcm_token=token, user_id=user.id).first()
            valid_tokens = multi_fcm_tokens_validate([fcm_token])
            if valid_tokens:
                return JsonResponse({'isValid': True}, status=status.HTTP_200_OK)
            else:
                return JsonResponse({'isValid': False, 'error': 'Invalid token'}, status=status.HTTP_200_OK)
        except User.DoesNotExist as e:
            return JsonResponse({'isValid': False, 'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except FCMToken.DoesNotExist as e:
            return JsonResponse({'isValid': False, 'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({'isValid': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@csrf_exempt
@user_is_authorized
def fetchNotifications(request):
    if request.method == 'GET':
        try:
            user_email = getattr(request, 'user_email', None)
            query_params = request.GET.dict()
            platform = query_params.get('platform', 'mobile')
            my_requests = query_params.get('my_requests')
            isRead = query_params.get('isRead', None)
            user = User.objects.get(email=user_email)
            notifications = Notification.objects.filter(receivers__contains=[user.id])

            if platform:
                notifications = notifications.filter(target_platforms__contains=[platform])
            if my_requests:
                leaves = Leave.objects.filter(user=user)
                notifications = notifications.filter(object_id__in=[leave.id for leave in leaves])
            if isRead:
                notifications = notifications.filter(isRead=isRead)
            
            notifications = notifications.order_by('-created_at')
            notifications_serializer = FetchNotificationsSerializer(notifications, many=True)
            return JsonResponse(notifications_serializer.data, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@csrf_exempt
@user_is_authorized
def updateNotifications(request):
    if request.method == 'PUT':
        try:
            ids = JSONParser().parse(request)
            Notification.objects.filter(id__in=ids).update(isRead=True)
            return JsonResponse({'message': 'Notifications Updated Successfully!!'}, status=status.HTTP_200_OK)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)