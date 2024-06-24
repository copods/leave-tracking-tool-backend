from datetime import date, datetime, timedelta
from django.db import transaction
from django.db.models import Q
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from LeaveTrackingApp.models import DayDetails, Leave, LeaveType, StatusReason
from LeaveTrackingApp.serializers import *
from LeaveTrackingApp.utils import (
    check_leave_overlap,
    get_users_for_day,
    getYearLeaveStats
)
from PushNotificationApp.models import FCMToken
from PushNotificationApp.serializers import NotificationSerializer
from PushNotificationApp.utils import (
    multi_fcm_tokens_validate,
    send_token_push
)
from rest_framework import status
from rest_framework.parsers import JSONParser
from UserApp.decorators import user_is_authorized
from UserApp.models import User
from UserApp.serializers import UserSerializer
from common.utils import send_email


@csrf_exempt
@user_is_authorized
def getLeaveTypes(request):
    if request.method=='GET':
        leave_types = LeaveType.objects.all()
        leave_types_serializer = LeaveTypeSerializer(leave_types, many=True)
        return JsonResponse(leave_types_serializer.data, safe=False)

@csrf_exempt
# @user_is_authorized
def createLeaveRequest(request):
    if request.method == 'POST':
        try:
            leave_data = JSONParser().parse(request)

            try:
                user = User.objects.get(id=leave_data['user'])
            except User.DoesNotExist:
                return JsonResponse({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            
            try:
                approver = User.objects.get(id=leave_data['approver'])
                approver_id = approver.id
            except User.DoesNotExist:
                return JsonResponse({'error': 'Approver not found'}, status=status.HTTP_404_NOT_FOUND)
            
            #validations
            if check_leave_overlap(leave_data):
                return JsonResponse({'error': 'You have already applied leave for some of these days'}, status=status.HTTP_400_BAD_REQUEST)

            with transaction.atomic():
                leave_serializer = LeaveSerializer(data=leave_data)
                if leave_serializer.is_valid():
                    leave_instance = leave_serializer.save()

                    leave_data = leave_serializer.data
                    approver_data = UserSerializer(approver).data
                    user_data = UserSerializer(user).data
                    leave_text = f'''Your Team member {user_data['first_name']} {user_data['last_name']} has requested 
                                 a leave request from {leave_data['start_date']} to {leave_data['end_date']}.
                                 Reason: {leave_data['leave_reason']}. Take action now on the app! '''
                    subject = f'Leave Request by {user_data['first_name']} {user_data['last_name']}'

                    send_email(
                        recipients=[approver_data],
                        subject=subject,
                        template_name='leave_notification_template.html',
                        context={'leave_text': leave_text},
                        app_name='LeaveTrackingApp'
                    )

                    notification_data = {
                        'types': 'Leave-Request',  
                        'leaveApplicationId': leave_instance.id,
                        'receivers': [approver.id],  
                        'title': f"Leave Request by {user.long_name()}",
                        'subtitle': f"{user.long_name()} has requested leave.",
                        'created_by': user.id,
                    }
                    notification_serializer = NotificationSerializer(data=notification_data)
                    if notification_serializer.is_valid():
                        notification_serializer.save()
                    else:
                        return JsonResponse(notification_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                else:
                    return JsonResponse(leave_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            fcm_tokens_queryset = FCMToken.objects.filter(user_id=approver_id)
            fcm_tokens = [token.fcm_token for token in fcm_tokens_queryset]
            valid_tokens = multi_fcm_tokens_validate(fcm_tokens, approver_id)

            if valid_tokens:
                response = send_token_push(notification_data['title'], notification_data['subtitle'], valid_tokens)
                if 'success' in response:
                    return JsonResponse({"message": response['message']}, status=status.HTTP_201_CREATED)
                else:
                    # return JsonResponse({"error": response['error']}, status=status.HTTP_400_BAD_REQUEST)
                    pass
            
            # return JsonResponse({"error": "No valid FCM tokens found"}, status=status.HTTP_400_BAD_REQUEST)
            return JsonResponse({"message": "Leave request created successfully"}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# filter query param format=> filter=role:9f299ed6-caf0-4241-9265-7576af1d6426,status:P
@csrf_exempt
@user_is_authorized
def leavesForApprover(request):
    if request.method=='GET':
        try:
            user_email = getattr(request, 'user_email', None)  #user_email is fetched from token while authorizing, then added to request object
            filters = request.GET.get('filter', None)
            search = request.GET.get('search', None)
            sort = request.GET.get('sort', None)
            page = request.GET.get('page', 1)
            pageSize = request.GET.get('pageSize', 100)
            user = User.objects.get(email=user_email)
            leaves = Leave.objects.filter(approver=user)
            if filters:
                leaves = leaves.filter(Q(**{f.split(':')[0]: f.split(':')[1] for f in filters.split(',')})) 
            if search:
                leaves = leaves.filter(Q(user__first_name__icontains=search) | Q(user__last_name__icontains=search))
            if sort:
                leaves = leaves.order_by(sort)
            if page or pageSize:
                leaves = leaves[(int(page)-1)*int(pageSize):int(page)*int(pageSize)]
            leaves_serializer = LeaveListSerializer(leaves, many=True)
            return JsonResponse(leaves_serializer.data, safe=False)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@user_is_authorized
def getUserLeaves(request):
    if request.method=='GET':
        try:
            user_email = getattr(request, 'user_email', None)  #user_email is fetched from token while authorizing, then added to request object
            page = request.GET.get('page', 1)
            pageSize = request.GET.get('pageSize', 100)
            user = User.objects.get(email=user_email)
            user_leaves = Leave.objects.filter(user_id=user.id)
            if page or pageSize:
                user_leaves = user_leaves[(int(page)-1)*int(pageSize):int(page)*int(pageSize)]
            user_leaves_serializer = UserLeaveListSerializer(user_leaves, many=True)
            return JsonResponse(user_leaves_serializer.data, safe=False)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@user_is_authorized
def getLeaveDetails(request, id):
    if request.method=='GET':
        try:
            leave = Leave.objects.get(id=id)
            leave_serializer = LeaveDetailSerializer(leave)
            return JsonResponse(leave_serializer.data, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
@csrf_exempt
# @user_is_authorized
def getUserLeaveStats(request):
    if request.method == 'GET':
        try:
            # user_email = getattr(request, 'user_email', None) 
            user_email = "tejas.jaybhai+4@copods.co"
            year = request.GET.get('year', None)
            user = User.objects.get(email=user_email)
            leave_stats = getYearLeaveStats(user.id, year)
            return JsonResponse(leave_stats, safe=False)
        except ValueError as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# change leave status with status message
@csrf_exempt
@user_is_authorized
def addLeaveStatus(request):
    if request.method == 'POST':
        try:
            # future aspect: based on the deadline to get leave accepted, withdrawn or rejected, status reason creation can be done
            status_data = JSONParser().parse(request)
            user_email = getattr(request, 'user_email', None) 
            status = status_data.get('status')
            reason_value = status_data.get('reason')
            leave_id = status_data.get('leave_id')

            if not all([status, reason_value, user_email, leave_id]):
                return JsonResponse({'error': 'Missing required fields'}, status=400)

            user = User.objects.only('id').get(email=user_email)
            leave = Leave.objects.only('id').get(id=leave_id)
            
            status_reason = StatusReason.objects.create(user=user, status=status, reason=reason_value)
            status_reason.save()
            leave.status_reasons.add(status_reason)
            leave.status = status
            leave.save()

            approver_data = UserSerializer(user).data
            user_data = UserSerializer(leave.user).data
            subject = f'Leave Status Updated by {approver_data["first_name"]} {approver_data["last_name"]}'
            leave_text = f'''Your leave request from {leave.start_date} to {leave.end_date} has been {leave.status}!.
                             For more details, check out on the app.''' 
            send_email(
                recipients=[user_data],
                subject=subject,
                template_name='leave_notification_template.html',
                context={'leave_text': leave_text},
                app_name='LeaveTrackingApp'
            )

            return JsonResponse(StatusReasonSerializer(status_reason).data, status=201)
        
        except  User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        except Leave.DoesNotExist:
            return JsonResponse({'error': 'Leave not found'}, status=404)
        except StatusReason.DoesNotExist:
            return JsonResponse({'error': 'Status reason not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@user_is_authorized
def getEmployeeAttendance(request):
    if request.method == 'GET':
        try:
            current_date = request.GET.get('date', None)
            current_date = datetime.strptime(current_date, "%Y-%m-%d").date() if current_date else datetime.now().date()
            last_date = current_date 
            #exclude saturday and sunday
            i=1
            while i<=7:
                last_date += timedelta(days=1)
                if not (last_date.weekday()==5 or last_date.weekday()==6):
                    i+=1
            
            leaves = Leave.objects.filter(
                Q(status='A') &
                (Q(start_date__gte=current_date) & Q(start_date__lte=last_date)) | 
                (Q(end_date__gte=current_date) & Q(end_date__lte=last_date))
            )
            
            leaves = LeaveUtilSerializer(leaves, many=True).data
            
            resp_obj = {}
            resp_obj['users_on_leave'] = {
                'today': [],
                'next_seven_days': []
            }
            resp_obj['users_on_wfh'] = {
                'today': [],
                'next_seven_days': []
            }

            #calculate for on_leave
            today_data = get_users_for_day(leaves, current_date)
            temp_curr_date = current_date + timedelta(days=1)
            next_seven_day_data = set({})
            while temp_curr_date <= last_date:
                if temp_curr_date.weekday()==5 or temp_curr_date.weekday()==6:
                    temp_curr_date += timedelta(days=1)
                    continue
                
                x = get_users_for_day(leaves, temp_curr_date).get('users')
                for user in x:
                    next_seven_day_data.add(frozenset(user.items()))

                temp_curr_date += timedelta(days=1)
            
            resp_obj['users_on_leave']['today'] = today_data.get('users')
            resp_obj['users_on_leave']['next_seven_days'] = [dict(data) for data in next_seven_day_data]
            

            #calculate for on_wfh
            today_data = get_users_for_day(leaves, current_date, wfh=True)
            temp_curr_date = current_date + timedelta(days=1)
            next_seven_day_data = set({})
            while temp_curr_date <= last_date:
                if temp_curr_date.weekday()==5 or temp_curr_date.weekday()==6:
                    temp_curr_date += timedelta(days=1)
                    continue
                
                x = get_users_for_day(leaves, temp_curr_date, wfh=True).get('users')
                for user in x:
                    next_seven_day_data.add(frozenset(user.items()))

                temp_curr_date += timedelta(days=1)

            resp_obj['users_on_wfh']['today'] = today_data.get('users')
            resp_obj['users_on_wfh']['next_seven_days'] = [dict(data) for data in next_seven_day_data]
            
            on_leave_wfh_count = DayDetails.objects.filter(date=current_date).count()
            users = User.objects.all().count()

            resp_obj['users_present'] = users - on_leave_wfh_count
            resp_obj['total_users'] = users
            return JsonResponse(resp_obj, safe=False)
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# enable editing of leave request
@csrf_exempt
@user_is_authorized
def enableEditLeave(request):
    if request.method == 'POST':
        try:
            leave_data = JSONParser().parse(request)
            leave = Leave.objects.get(id=leave_data['id'])
            if not leave.editStatus:
                leave.editStatus = 'Requested-For-Edit'
                leave.editReason = leave_data['edit_reason']
                leave.save()
                return JsonResponse({'message': 'Leave request sent to Edit'}, status=200)   
            else:
                return JsonResponse({'message': 'Leave request already sent to Edit'}, status=400)

        except Leave.DoesNotExist:
            return JsonResponse({'error': 'Leave not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
@csrf_exempt
@user_is_authorized
def editLeave(request, id):
    if(request.method == 'PUT'):
        try:
            leave_data = JSONParser().parse(request)
            leave = Leave.objects.get(id=id)
            if leave.editStatus == 'Requested-For-Edit':
                #update leave logic

                #after update
                # leave.editStatus = 'Edited'
                pass
            else:
                return JsonResponse({'error': 'Leave request is not editable'}, status=400)
        
        except Leave.DoesNotExist:
            return JsonResponse({'error': 'Leave not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
