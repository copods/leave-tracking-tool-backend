from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from LeaveTrackingApp.models import DayDetails, Leave
from PushNotificationApp.models import Notification

@csrf_exempt
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
def clear_all_notifications(request):
    if request.method == 'DELETE':
        try:
            all_notifications = Notification.objects.all()
            notification_cnt = all_notifications.count()
            all_notifications.delete()
            return JsonResponse({'msg': f'{notification_cnt} notifications deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
              