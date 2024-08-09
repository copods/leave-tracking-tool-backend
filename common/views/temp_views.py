from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from rest_framework import status
from LeaveTrackingApp.models import DayDetails, Leave
from PushNotificationApp.models import FCMToken, Notification
from PushNotificationApp.serializers import FCMTokenSerializer
from PushNotificationApp.serializers import FetchNotificationsSerializer
from PushNotificationApp.utils import send_notification
from rest_framework.parsers import JSONParser
from rest_framework import serializers

@csrf_exempt
@transaction.atomic
def clear_all_leaves(request):
    if request.method == 'DELETE':
        try:
            all_leaves = Leave.objects.all()
            day_details = DayDetails.objects.all()
            day_details_cnt = leave_cnt = 0
            for leave in all_leaves:
                leave.day_details.clear()
                leave.delete()
                leave_cnt += 1
            for day_detail in day_details:
                day_detail.delete()
                day_details_cnt += 1
            return JsonResponse({'msg': f'{day_details_cnt} day details and {leave_cnt} leaves deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
@csrf_exempt
@transaction.atomic
def clear_all_notifications(request):
    if request.method == 'DELETE':
        try:
            all_notifications = Notification.objects.all()
            notification_cnt = all_notifications.count()
            all_notifications.delete()
            return JsonResponse({'msg': f'{notification_cnt} notifications deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

@csrf_exempt
def send_dummy_notification(request):
    if request.method == 'POST':
        try:
            notification_data = JSONParser().parse(request)
            send_notification(notification_data, notification_data['receivers'])
            return JsonResponse({'msg': 'notification sent successfully'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
              
@csrf_exempt
def get_fcm_tokens(request):
    if request.method == 'GET':
        try:
            class DummyFCMTokenSerializer(serializers.ModelSerializer):
                user = serializers.SerializerMethodField()
                class Meta:
                    model = FCMToken
                    fields = '__all__'
                def get_user(self, obj):
                    return {
                        'id': obj.user.id,
                        'name': obj.user.long_name()
                    }
            fcm_tokens = FCMToken.objects.all()
            fcm_tokens = DummyFCMTokenSerializer(fcm_tokens, many=True).data
            return JsonResponse(fcm_tokens, safe=False)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
@csrf_exempt
def fetch_notifications(request):
    if request.method == 'GET':
        try:
            query_params = request.GET.dict()
            platform = query_params.get('platform', 'mobile')
            notifications = Notification.objects.all()

            if platform:
                notifications = notifications.filter(target_platforms__contains=[platform])
            
            notifications = notifications.order_by('-created_at')
            notifications_serializer = FetchNotificationsSerializer(notifications, many=True)
            return JsonResponse(notifications_serializer.data, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)