from datetime import date, datetime, timedelta
import calendar
from django.db import transaction
from django.db.models import Count, Q, Prefetch
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from LeaveTrackingApp.constant import LEAVE_TYPES
from LeaveTrackingApp.models import DayDetails, Leave, LeaveType, StatusReason
from LeaveTrackingApp.serializers import *
from LeaveTrackingApp.utils import (
    get_unpaid_data,
    get_users_for_day,
    is_leave_valid,
    is_maternity_leave_request,
    user_leave_stats_hr_view,
    user_leave_stats_user_view
)
from PushNotificationApp.utils import send_notification
from rest_framework import status
from rest_framework.parsers import JSONParser
from UserApp.decorators import user_is_authorized
from UserApp.models import User
from UserApp.serializers import UserSerializer
from common.utils import send_email
import json


@csrf_exempt
@user_is_authorized
def getLeaveTypes(request):
    if request.method=='GET':
        leave_types = LeaveType.objects.all() 
        leave_types_serializer = LeaveTypeSerializer(leave_types, many=True)
        return JsonResponse(leave_types_serializer.data, safe=False)
    
@csrf_exempt
@user_is_authorized
def getConstants(request):
    return JsonResponse({'leaveTypes': LEAVE_TYPES})

@csrf_exempt
@user_is_authorized
def createLeaveRequest(request):
    if request.method == 'POST':
        try:
            if request.content_type.startswith('application/json'):
                leave_data = JSONParser().parse(request)
            else:
                leave_data = request.POST.dict()
                leave_data['day_details'] = json.loads(request.POST.get('day_details', '[]'))
                leave_data['assets_documents'] = request.FILES.get('assets_documents')

            try:
                user = User.objects.get(id=leave_data['user'])
            except User.DoesNotExist:
                return JsonResponse({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            
            try:
                approver = User.objects.get(id=leave_data['approver'])
            except User.DoesNotExist:
                return JsonResponse({'error': 'Approver not found'}, status=status.HTTP_404_NOT_FOUND)
            
            #validations
            response = is_leave_valid(leave_data)
            if not response['valid']:
                return JsonResponse({'message': response['messages']}, status=status.HTTP_400_BAD_REQUEST)
                
            with transaction.atomic():
                leave_serializer = LeaveSerializer(data=leave_data)
                if leave_serializer.is_valid():
                    leave_instance = leave_serializer.save()
                else:
                    return JsonResponse(leave_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            leave_data = leave_serializer.data
            approver_data = UserSerializer(approver).data
            user_data = UserSerializer(user).data

            errors = []

            # Send Email
            try:
                leave_text = f'''Your Team member {user_data['first_name']} {user_data['last_name']} has requested 
                                 a leave request from {leave_data['start_date']} to {leave_data['end_date']}.
                                 Reason: {leave_data['leave_reason']}.'''
                subject = f'Leave Request by {user_data['first_name']} {user_data['last_name']}'
                send_email(
                    recipients=[approver_data],
                    subject=subject,
                    template_name='leave_notification_template.html',
                    context={'leave_text': leave_text},
                    app_name='LeaveTrackingApp'
                )
            except Exception as e:
                errors.append(f"Could not send email. Error: {e}")

            # Create Notification
            notification_data = {
                'type': 'leave_request_for_approver',  
                'content_object': leave_instance,
                'receivers': [approver.id],  
                'title': f"Leave Request by {user.long_name()}",
                'subtitle': f"{user.long_name()} has requested leave.",
                'created_by': user,
                'target_platforms': ['mobile']
            }
            errors.append(send_notification(notification_data, notification_data['receivers']))
            
            if errors:
                return JsonResponse({"message": "Leave request created successfully but sending email or notification failed", 'errors': errors}, status=status.HTTP_201_CREATED)
            else:
                return JsonResponse({"message": "Leave request created successfully"}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@user_is_authorized
def getLeavesList(request):
    if request.method == 'GET':
        try:
            query_params = {key: request.GET.getlist(key) for key in request.GET.keys()}
            search = query_params.get('search', [None])[0]
            sort = query_params.get('sort', [None])[0]
            page = query_params.get('page', [1])[0]
            pageSize = query_params.get('pageSize', [10])[0]
            for_approver = query_params.get('for_approver', [False])[0]
            user_email = getattr(request, 'user_email', None)
            user = User.objects.get(email=user_email)

            if for_approver:
                query_params.pop('for_approver')
                leaves = Leave.objects.filter(approver=user)
                serializer_class = LeaveListSerializer
            else:
                leaves = Leave.objects.filter(user=user)
                serializer_class = UserLeaveListSerializer

            filters = {}
            for key, value in query_params.items():
                if key not in ['search', 'sort', 'page', 'pageSize']:
                    if key == 'leave_type':
                        filters['leave_type__name__in'] = value
                    else:
                        filters[f'{key}__in'] = value

            leaves = leaves.filter(**filters)

            if search:
                leaves = leaves.filter(
                    Q(user__first_name__icontains=search) |
                    Q(user__last_name__icontains=search) |
                    Q(leave_type__name__icontains=search)
                )

            if sort:
                leaves = leaves.order_by(sort)

            if page or pageSize:
                leaves = leaves[(int(page)-1)*int(pageSize):int(page)*int(pageSize)]

            leaves_serializer = serializer_class(leaves, many=True)
            return JsonResponse(leaves_serializer.data, safe=False)

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
@user_is_authorized
def getUserLeaveStats(request):
    if request.method == 'GET':
        try:
            user_email = getattr(request, 'user_email', None) 
            year = request.GET.get('year', None)
            user = User.objects.get(email=user_email)
            leave_stats = user_leave_stats_user_view(user.id, year)
            return JsonResponse(leave_stats, safe=False)
        except ValueError as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
# @user_is_authorized
def getEmployeeLeaveStats(request, id):
    if request.method == 'GET':
        try:
            year = request.GET.get('year', None)
            # year= "2025-2026"
            user = User.objects.get(id=id)
            leave_stats = user_leave_stats_hr_view(user.id, year)
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
            reason_value = status_data.get('reason', None)
            leave_id = status_data.get('leave_id')

            if (not all([status, leave_id])) or (status in ['R', 'W'] and not reason_value):
                return JsonResponse({'error': 'Missing required fields'}, status=400)

            user = User.objects.only('id').get(email=user_email)
            leave = Leave.objects.only('id').get(id=leave_id)

            status_reason = StatusReason.objects.create(user=user, status=status, reason=reason_value)
            status_reason.save()
            leave.status_reasons.add(status_reason)
            leave.status = status
            leave.save()

            errors = []
            status = dict(Leave.STATUS_CHOICES).get(leave.status)

            # send email
            try:
                approver_data = UserSerializer(user).data
                user_data = UserSerializer(leave.user).data
                subject = f'Leave {status.capitalize()} by {approver_data["first_name"]} {approver_data["last_name"]}'
                leave_text = f'''Your request from {leave.start_date.strftime('%d %b')} to {leave.end_date.strftime('%d %b')} has been {status.capitalize()}!.
                                For more details, check out on the app''' 
                send_email(
                    recipients=[user_data],
                    subject=subject,
                    template_name='leave_notification_template.html',
                    context={'leave_text': leave_text},
                    app_name='LeaveTrackingApp'
                )
            except Exception as e:
                errors.append(str(e))

            # send notification
            notification_data = {
                'type': 'leave_requested_by_creator',  
                'content_object': leave,
                'receivers': [leave.user.id],  
                'title': f"Your Leave is {status.capitalize()}",
                'subtitle': f"{user.long_name()} has {status.lower()} your leave for {leave.start_date.strftime('%d %b')} to {leave.end_date.strftime('%d %b')}",
                'created_by': user,
                'target_platforms': ['mobile']
            }
            errors.append(send_notification(notification_data, notification_data['receivers']))

            if errors:
                return JsonResponse({'data': StatusReasonSerializer(status_reason).data, 'error': errors}, status=201)
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
                if not (last_date.weekday()==5 or last_date.weekday()==6): #TODO: also check for confirmed holidays
                    i+=1
            
            leaves = Leave.objects.filter( Q(status='A') & (Q(start_date__lte=last_date) & Q(end_date__gte=current_date)) )
            leaves = LeaveUtilSerializer(leaves, many=True).data

            resp_obj = {
                'users_on_leave': {
                    'today': [],
                    'next_seven_days': []
                },
                'users_on_wfh' : {
                    'today': [],
                    'next_seven_days': []
                }
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
            resp_obj['total_users'] = User.objects.all().count()
            resp_obj['users_present'] = resp_obj['total_users'] - (len(resp_obj['users_on_wfh']['today']) + len(resp_obj['users_on_leave']['today']))
            
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
            user_email = getattr(request, 'user_email', None)
            user = User.objects.get(email=user_email)
            leave = Leave.objects.get(id=leave_data['id'])
            if not leave.editStatus:
                leave.editStatus = 'requested_for_edit'
                leave.editReason = leave_data['edit_reason']
                leave.save()
                errors = []

                try:
                    user_data = UserSerializer(leave.user).data
                    subject = f'{user.first_name.capitalize()} has Requested For Edit.'
                    leave_text = f'''{user.long_name()} has requested to edit your leave for {leave.start_date.strftime('%d %b')} to {leave.end_date.strftime('%d %b')}. Reason: {leave_data['editReason']}.''',
                    send_email(
                        recipients=[user_data],
                        subject=subject,
                        template_name='leave_notification_template.html',
                        context={'leave_text': leave_text},
                        app_name='LeaveTrackingApp'
                    )
                except Exception as e:
                    errors.append(str(e))

                # send notification
                notification_data = {
                    'type': 'leave_requested_by_creator',  
                    'content_object': leave,
                    'receivers': [leave.user.id],  
                    'title': f"{user.first_name.capitalize()} has Requested For Edit.",
                    'subtitle': f"{user.long_name()} has requested to edit your leave for {leave.start_date.strftime('%d %b')} to {leave.end_date.strftime('%d %b')}.",
                    'created_by': user,
                    'target_platforms': ['mobile']
                }
                errors.append(send_notification(notification_data, notification_data['receivers']))
                if errors:
                    return JsonResponse({'message': 'Leave request sent to Edit', 'errors': errors}, status=200)
                else:
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
            if leave.editStatus == 'requested_for_edit':
                leave_serializer = LeaveSerializer(leave, data=leave_data, partial=True)
                if leave_serializer.is_valid():
                    leave_serializer.save()
                    errors = []
                    # send email
                    try:
                        user_data = UserSerializer(leave.user).data
                        subject = f'{leave.user.first_name.capitalize()} has Edited the leave.'
                        leave_text =  f'''{leave.user.long_name()} has made the changes you requested.''',
                        send_email(
                            recipients=[user_data],
                            subject=subject,
                            template_name='leave_notification_template.html',
                            context={'leave_text': leave_text},
                            app_name='LeaveTrackingApp'
                        )
                    except Exception as e:
                        errors.append(str(e))
                
                    notification_data = {
                        'type': 'leave_request_for_approver',  
                        'content_object': leave,
                        'receivers': [leave.approver.id],  
                        'title': f"{leave.user.first_name.capitalize()} has Edited the leave.",
                        'subtitle': f"{leave.user.long_name()} has made the changes you requested.",
                        'created_by': leave.user,
                        'target_platforms': ['mobile']
                    }
                    errors.append(send_notification(notification_data, notification_data['receivers']))
                    response_data = LeaveDetailSerializer(leave).data
                    if errors:
                        return JsonResponse({'data': response_data, 'errors': errors}, status=200)
                    else:
                        return JsonResponse({'data': response_data}, status=200)  
                    
                return JsonResponse(leave_serializer.errors, status=400)
            else:
                return JsonResponse({'error': 'Leave request is not editable'}, status=400)
        
        except Leave.DoesNotExist:
            return JsonResponse({'error': 'Leave not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@user_is_authorized
def getUnpaidData(request):
    if request.method == 'GET':
        try:
            curr_year = datetime.now().year
            curr_month = datetime.now().month
            months = [calendar.month_abbr[i] for i in range(1, curr_month+1)]
            response_obj = {
                'months': months,
                'months_data': {month: [] for month in months}
            }

            leave_types = LeaveType.objects.all()
            users = User.objects.prefetch_related( Prefetch('user_of_leaves', queryset=Leave.objects.filter(status='A')) )

            for month in months:
                for user in users:
                    user_leaves = user.user_of_leaves.all()
                    if not user_leaves:
                        continue
                    unpaids_for_month = get_unpaid_data(user, user_leaves, leave_types, curr_year, month)
                    if len(unpaids_for_month):
                        response_obj['months_data'][month].append({
                            'id': user.id,
                            'name': user.long_name(),
                            'email': user.email,
                            'profile_image': user.profile_image,
                            'unpaid_leaves': unpaids_for_month
                        })
                        
            return JsonResponse(response_obj, safe=False)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        

@csrf_exempt
@user_is_authorized
def getLeaveStatusCount(request):
    if request.method == 'GET':
        try:
            user_email = getattr(request, 'user_email', None)
            user = User.objects.get(email=user_email)
            approver = request.GET.get('approver', None)
            if approver:
                leave_status_counts = Leave.objects.aggregate(
                    approved=Count('id', filter=Q(status='A')&Q(approver=user)),
                    pending=Count('id', filter=Q(status='P')&Q(approver=user)),
                    rejected=Count('id', filter=Q(status='R')&Q(approver=user)),
                )
            else:
                leave_status_counts = Leave.objects.aggregate(
                    approved=Count('id', filter=Q(status='A')&Q(user=user)),
                    pending=Count('id', filter=Q(status='P')&Q(user=user)),
                    rejected=Count('id', filter=Q(status='R')&Q(user=user)),
                )
            return JsonResponse(leave_status_counts, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
@csrf_exempt
@user_is_authorized
def withdrawLeave(request, id):
    if(request.method == 'PUT'):
        try:
            data =  JSONParser().parse(request)
            day_ids = data.get('day_ids', [])
            reason = data.get('reason', None)
            leave = Leave.objects.get(id=id)
            if leave.status in ['R', 'W']:
                return JsonResponse({'error': "Can't withdraw leave"}, status=400)
            if not reason:
                return JsonResponse({'error': 'Reason is required'}, status=400)
            if day_ids:
                non_withdrawn_days_cnt = leave.day_details.filter(is_withdrawn=False).count()
                DayDetails.objects.filter(id__in=day_ids).update(is_withdrawn=True)
                status_reason = StatusReason.objects.create(user=leave.user, status='W', reason=reason)
                leave.status_reasons.add(status_reason)
                if len(day_ids) == non_withdrawn_days_cnt:
                    leave.status = 'W'
                    leave.save()
                else:
                    days = leave.day_details.all().order_by('date')
                    start_flag = False
                    for day in days:
                        if not day.is_withdrawn:
                            if not start_flag:
                                leave.start_date = day.date
                                start_flag = True
                            leave.end_date = day.date
                    leave.save()

                try:
                    user_data = UserSerializer(leave.approver).data
                    subject = f'{leave.user.first_name.capitalize()} has Withdrawn the leave.' if len(day_ids)==leave.day_details.count() else f'{leave.user.first_name.capitalize()} has Withdrawn Some Days of Leave.'
                    leave_text =  f'''{leave.user.long_name()} has withdrawn the leave from {leave.start_date.strftime('%d %b')} to {leave.end_date.strftime('%d %b')}.''' if len(day_ids)==leave.day_details.count() else f'''{leave.user.long_name()} has withdrawn {len(day_ids)} days of their leave. Reason: {leave.status_reasons}.'''
                    send_email(
                        recipients=[user_data],
                        subject=subject,
                        template_name='leave_notification_template.html',
                        context={'leave_text': leave_text},
                        app_name='LeaveTrackingApp'
                    )
                except Exception as e:
                    errors.append(str(e))
                    
                #notify approver
                title = f"{leave.user.first_name.capitalize()} has Withdrawn the leave." if len(day_ids)==leave.day_details.count() else f"{leave.user.first_name.capitalize()} has Withdrawn Some Days of Leave."
                subtitle = f"{leave.user.long_name()} has withdrawn the leave from {leave.start_date.strftime('%d %b')} to {leave.end_date.strftime('%d %b')}." if len(day_ids)==leave.day_details.count() else f"{leave.user.long_name()} has withdrawn {len(day_ids)} days of their leave."
                notification_data = {
                    'type': 'leave_request_for_approver',  
                    'content_object': leave,
                    'receivers': [leave.approver.id],  
                    'title': title,
                    'subtitle': subtitle,
                    'created_by': leave.user,
                    'target_platforms': ['mobile']
                }
                errors = send_notification(notification_data, notification_data['receivers'])
                if errors:
                    return JsonResponse({'msg': 'Withdrawn Successfully', 'errors': errors}, status=200)
                else:
                    return JsonResponse({'msg': 'Withdrawn Successfully'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)