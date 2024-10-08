from datetime import datetime
from django.http.response import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from rest_framework import status
from rest_framework.parsers import JSONParser
from LeaveTrackingApp.models import RuleSet, YearPolicy, yearCalendar, STATUS_CHOICES
from LeaveTrackingApp.serializers import YearCalendarSerializer, YearPolicySerializer
from PushNotificationApp.models import Notification
from PushNotificationApp.utils import send_notification
from UserApp.decorators import user_is_authorized
from UserApp.models import User

@csrf_exempt
@user_is_authorized
def getHolidayCalendar(request):
    if request.method=='GET':
        try:
            year = request.GET.get('year', None)
            if year:
                year_calendar = yearCalendar.objects.filter(status='published', year=year).order_by('-updated_at').first()
            else:
                year_calendar = yearCalendar.objects.filter(status='published').order_by('-updated_at').first()
            if not year_calendar:
                if year:
                    year_calendar = yearCalendar.objects.filter(status__in=['approved', 'draft', 'sent_for_approval'], year=year).first()
                else:
                    year_calendar = yearCalendar.objects.filter(status__in=['approved', 'draft', 'sent_for_approval']).first()
                if not year_calendar:
                    return JsonResponse({}, status=status.HTTP_200_OK)
            data = YearCalendarSerializer(year_calendar).data
            data['holidays'].sort(key=lambda x: datetime.strptime(x['date'], "%Y-%m-%d"))
            return JsonResponse(data, safe=False)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@user_is_authorized
def createHolidayCalendar(request):
    if request.method=='POST':
        try:
            year_calendar_data = JSONParser().parse(request)
            year_calendar_data['created_by'] = User.objects.get(email=getattr(request, 'user_email',None)).id
            admins = User.objects.filter(role__role_key='admin')
            if yearCalendar.objects.filter(status__in=['approved', 'draft', 'sent_for_approval']).exists():
                return JsonResponse({"error": "A draft or an approved calendar already exists"}, status=status.HTTP_403_FORBIDDEN)

            status_value = year_calendar_data.get('status', 'Draft')
            if status_value not in ['Draft', 'Sent For Approval']:
                year_calendar_data['status'] = 'draft'
            else:
                year_calendar_data['status'] = next((k for k, v in dict(STATUS_CHOICES).items() if v==status_value), 'draft')
            
            errors = []
            year_calendar_serializer = YearCalendarSerializer(data=year_calendar_data)
            if year_calendar_serializer.is_valid():
                calendar_instance = year_calendar_serializer.save()

                #create notification if sent for approval directly
                if calendar_instance.status == 'sent_for_approval':
                    notification_data = {
                        'type': 'calendar',  
                        'content_object': calendar_instance,
                        'receivers': [admin.id for admin in admins],  
                        'title': f"Calendar Sent by {calendar_instance.created_by.first_name}",
                        'subtitle': f"{calendar_instance.created_by.long_name()} has sent a calendar for your approval or rejection.",
                        'created_by': calendar_instance.created_by,
                        'target_platforms': ['web']
                    }
                    try:
                        notification = Notification(**notification_data)
                        notification.save()
                    except Exception as e:
                        errors.append(e)
                if errors:
                    return JsonResponse({"data": year_calendar_serializer.data, 'errors': errors}, status=status.HTTP_201_CREATED)
                return JsonResponse(year_calendar_serializer.data, status=status.HTTP_201_CREATED)
            return JsonResponse(year_calendar_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
@csrf_exempt
@user_is_authorized
def updateYearCalendar(request, id):
    if request.method=='PUT':
        try:
            user_email = getattr(request, 'user_email', None)
            user = User.objects.get(email=user_email)
            admins = User.objects.filter(role__role_key='admin')
            document_data = JSONParser().parse(request)
            calendar_obj = yearCalendar.objects.get(id=id)

            errors = []

            if calendar_obj.status == 'published':
                return JsonResponse({"error": "Can't edit published policy"}, status=status.HTTP_403_FORBIDDEN)
            
            elif calendar_obj.status == 'sent_for_approval':
                if (len(document_data.keys())>=1 and (not document_data.get('status'))) or len(document_data.keys())>1: # do not edit sent for approval document
                    return JsonResponse({"error": "Can't edit calendar which is sent for approval"}, status=status.HTTP_403_FORBIDDEN)
                
                elif document_data.get('status') == 'Sent For Approval': 
                    return JsonResponse({"error": "Calendar already sent for approval"}, status=status.HTTP_403_FORBIDDEN)
                
                elif document_data.get('status') == 'Approved': # approve calendar
                    if user.role.role_key == 'admin':
                        calendar_obj.status = 'approved'
                        calendar_obj.save()
                        notification_data = {
                            'type': 'calendar',  
                            'content_object': calendar_obj,
                            'receivers': [calendar_obj.created_by.id],  
                            'title': f"Calendar Approved by {user.first_name}",
                            'subtitle': f"{user.long_name()} has Approved the calendar you created.",
                            'created_by': user,
                            'target_platforms': ['web']
                        }
                        try:
                            notification = Notification(**notification_data)
                            notification.save()
                        except Exception as e:
                            errors.append(e)
                        data = YearCalendarSerializer(calendar_obj).data
                        return JsonResponse(data, status=status.HTTP_200_OK)
                    else:
                        return JsonResponse({"error": "Only admin can approve calendar"}, status=status.HTTP_403_FORBIDDEN)
                    
                elif document_data['status'] == 'Rejected': # reject calendar
                    if user.role.role_key == 'admin':
                        calendar_obj.status = 'draft'
                        calendar_obj.save()
                        notification_data = {
                            'type': 'calendar',  
                            'content_object': calendar_obj,
                            'receivers': [calendar_obj.created_by.id],  
                            'title': f"Calendar Rejected by {user.first_name}",
                            'subtitle': f"{user.long_name()} has Rejected the calendar you created.",
                            'created_by': user,
                            'target_platforms': ['web']
                        }
                        try:
                            notification = Notification(**notification_data)
                            notification.save()
                        except Exception as e:
                            errors.append(e)
                        data = YearCalendarSerializer(calendar_obj).data
                        return JsonResponse(data, status=status.HTTP_200_OK)
                    else:
                        return JsonResponse({"error": "Only admin can reject calendar"}, status=status.HTTP_403_FORBIDDEN)

            #edit calendar / send for approval with edited data
            elif (not document_data.get('status') or document_data['status'] == 'Draft') or (calendar_obj.status == 'draft' and document_data['status'] == 'Sent For Approval'):
                status_value = document_data.get('status', 'draft')
                document_data['status'] = next((k for k, v in dict(STATUS_CHOICES).items() if v==status_value), 'draft')
                year_calendar_serializer = YearCalendarSerializer(calendar_obj, document_data, partial=True)
                if year_calendar_serializer.is_valid():
                    calendar_instance = year_calendar_serializer.save()
                    if calendar_instance.status == 'sent_for_approval':
                        notification_data = {
                            'type': 'calendar',  
                            'content_object': calendar_obj,
                            'receivers': [admin.id for admin in admins],  
                            'title': f"Calendar Sent by {user.first_name}",
                            'subtitle': f"{user.long_name()} has sent a calendar for your approval or rejection.",
                            'created_by': user,
                            'target_platforms': ['web']
                        }
                        try:
                            notification = Notification(**notification_data)
                            notification.save()
                        except Exception as e:
                            errors.append(e)
                    return JsonResponse(year_calendar_serializer.data, status=status.HTTP_200_OK)
                return JsonResponse(year_calendar_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            elif calendar_obj.status == 'approved' and document_data['status'] == 'Approved':
                return JsonResponse({"error": "calendar already approved"}, status=status.HTTP_409_CONFLICT)
            
            elif calendar_obj.status in ['draft', 'sent_for_approval'] and document_data['status'] == 'Published':
                return JsonResponse({"error": "calendar is not approved yet"}, status=status.HTTP_403_FORBIDDEN)
            
            elif calendar_obj.status == 'draft' and document_data['status'] == 'Approved':
                return JsonResponse({"error": "calendar is not sent for approval yet"}, status=status.HTTP_403_FORBIDDEN)
            
            #publish calendar
            elif calendar_obj.status == 'approved' and document_data['status'] == 'Published':
                calendar_obj.status = 'published'
                calendar_obj.save()
                all_users = User.objects.all()
                notification_data = {
                    'type': 'calendar',  
                    'content_object': calendar_obj,
                    'receivers': [user.id for user in all_users],  
                    'title': f"New Calendar Published",
                    'subtitle': f"A new holidays calendar has been published for year {calendar_obj.year}.",
                    'created_by': user,
                    'target_platforms': ['mobile']
                }
                errors.append(send_notification(notification_data, notification_data['receivers']))
                data = YearCalendarSerializer(calendar_obj).data
                return JsonResponse(data, status=status.HTTP_200_OK)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@csrf_exempt
@user_is_authorized
def createYearPolicy(request):
    if request.method == 'POST':
        try:
            year_policy_data = JSONParser().parse(request)
            year_policy_data['created_by'] = User.objects.get(email=getattr(request, 'user_email', None)).id
            admins = User.objects.filter(role__role_key='admin')
            if YearPolicy.objects.filter(status__in=['approved', 'draft', 'sent_for_approval']).exists():
                return JsonResponse({"error": "A draft or an approved policy already exists"}, status=status.HTTP_403_FORBIDDEN)

            status_value = year_policy_data.get('status', 'Draft')
            if status_value not in ['Draft', 'Sent For Approval']:
                year_policy_data['status'] = 'draft'
            else:
                year_policy_data['status'] = next((k for k, v in dict(STATUS_CHOICES).items() if v==status_value), 'draft')

            errors=[]
            year_policy_serializer = YearPolicySerializer(data=year_policy_data)
            if year_policy_serializer.is_valid():
                policy_instance = year_policy_serializer.save()
                
                #create notification if sent for approval directly
                if policy_instance.status == 'sent_for_approval':
                    notification_data = {
                        'type': 'leave_policy',  
                        'content_object': policy_instance,
                        'receivers': [admin.id for admin in admins],  
                        'title': f"Leave Policy Sent by {policy_instance.created_by.first_name}",
                        'subtitle': f"{policy_instance.created_by.long_name()} has sent a leave policy for your approval or rejection.",
                        'created_by': policy_instance.created_by,
                        'target_platforms': ['web']
                    }
                    try:
                        notification = Notification(**notification_data)
                        notification.save()
                    except Exception as e:
                        errors.append(e)
                if errors:
                    return JsonResponse({"data": year_policy_serializer.data, 'errors': errors}, status=status.HTTP_201_CREATED)
                return JsonResponse(year_policy_serializer.data, status=status.HTTP_201_CREATED)
            return JsonResponse(year_policy_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@user_is_authorized
def getYearPolicy(request):
    if request.method=='GET':
        try:
            year = request.GET.get('year', None)
            if year:
                year_policy = YearPolicy.objects.filter(status='published', year=year).order_by('-updated_at').first()
            else:
                year_policy = YearPolicy.objects.filter(status='published').order_by('-updated_at').first()
            if not year_policy:
                year_policy = YearPolicy.objects.filter(status__in=['approved', 'draft', 'sent_for_approval'], year=year).order_by('-created_at').first()
                if not year_policy:
                    return JsonResponse({}, status=status.HTTP_200_OK)
                    
            year_policy_serializer = YearPolicySerializer(year_policy)
            return JsonResponse(year_policy_serializer.data, safe=False)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
@csrf_exempt
@user_is_authorized
def updateYearPolicy(request, id):
    if request.method=='PUT':
        try:
            user_email = getattr(request, 'user_email', None)
            user = User.objects.get(email=user_email)
            admins = User.objects.filter(role__role_key='admin')
            document_data = JSONParser().parse(request)
            policy_obj = YearPolicy.objects.get(id=id)

            errors = []

            if policy_obj.status == 'published':
                return JsonResponse({"error": "Can't edit published policy"}, status=status.HTTP_403_FORBIDDEN)
            
            elif policy_obj.status == 'sent_for_approval':
                if (len(document_data.keys())>=1 and (not document_data.get('status'))) or len(document_data.keys())>1: # do not edit sent for approval document
                    return JsonResponse({"error": "Can't edit policy which is sent for approval"}, status=status.HTTP_403_FORBIDDEN)
                
                elif document_data.get('status') == 'Sent For Approval': 
                    return JsonResponse({"error": "Policy already sent for approval"}, status=status.HTTP_403_FORBIDDEN)
                
                elif document_data.get('status') == 'Approved': # approve policy
                    if user.role.role_key == 'admin':
                        policy_obj.status = 'approved'
                        policy_obj.save()
                        notification_data = {
                            'type': 'leave_policy',  
                            'content_object': policy_obj,
                            'receivers': [policy_obj.created_by.id],  
                            'title': f"Leave Policy Approved By {user.first_name}",
                            'subtitle': f"{user.long_name()} has Approved the Leave Policy you created.",
                            'created_by': user,
                            'target_platforms': ['web']
                        }
                        try:
                            notification = Notification(**notification_data)
                            notification.save()
                        except Exception as e:

                            errors.append(e)
                        data = YearPolicySerializer(policy_obj).data
                        return JsonResponse(data, status=status.HTTP_200_OK)
                    else:
                        return JsonResponse({"error": "Only admin can approve policy"}, status=status.HTTP_403_FORBIDDEN)
                    
                elif document_data['status'] == 'Rejected': # reject policy
                    if user.role.role_key == 'admin':
                        policy_obj.status = 'draft'
                        policy_obj.save()
                        notification_data = {
                            'type': 'leave_policy',  
                            'content_object': policy_obj,
                            'receivers': [policy_obj.created_by.id],  
                            'title': f"Leave Policy Rejected By {user.first_name}",
                            'subtitle': f"{user.long_name()} has Rejected the Leave Policy you created.",
                            'created_by': user,
                            'target_platforms': ['web']
                        }
                        try:
                            notification = Notification(**notification_data)
                            notification.save()
                        except Exception as e:
                            errors.append(e)
                        data = YearPolicySerializer(policy_obj).data
                        return JsonResponse(data, status=status.HTTP_200_OK)
                    else:
                        return JsonResponse({"error": "Only admin can reject policy"}, status=status.HTTP_403_FORBIDDEN)

            #edit policy or (sent for approval with edited data)
            elif (not document_data.get('status') or document_data['status'] == 'Draft') or (policy_obj.status == 'draft' and document_data['status'] == 'Sent For Approval'):
                status_value = document_data.get('status', 'draft')
                document_data['status'] = next((k for k, v in dict(STATUS_CHOICES).items() if v==status_value), 'draft')
                year_policy_serializer = YearPolicySerializer(policy_obj, document_data, partial=True)
                if year_policy_serializer.is_valid():
                    policy_instance = year_policy_serializer.save()
                    if policy_instance.status == 'sent_for_approval':
                        notification_data = {
                            'type': 'leave_policy',  
                            'content_object': policy_obj,
                            'receivers': [admin.id for admin in admins],
                            'title': f"Leave Policy Sent by {user.first_name}",
                            'subtitle': f"{user.long_name()} has sent a Leave Policy for your approval or rejection.",
                            'created_by': user,
                            'target_platforms': ['web']
                        }
                        try:
                            notification = Notification(**notification_data)
                            notification.save()
                        except Exception as e:
                            errors.append(e)
                    return JsonResponse(year_policy_serializer.data, status=status.HTTP_200_OK)
                return JsonResponse(year_policy_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            elif policy_obj.status == 'approved' and document_data['status'] == 'Approved':
                return JsonResponse({"error": "Policy already approved"}, status=status.HTTP_409_CONFLICT)
            
            elif policy_obj.status in ['draft', 'sent_for_approval'] and document_data['status'] == 'Published':
                return JsonResponse({"error": "Policy is not approved yet"}, status=status.HTTP_403_FORBIDDEN)
            
            elif policy_obj.status == 'draft' and document_data['status'] == 'Approved':
                return JsonResponse({"error": "Policy is not sent for approval yet"}, status=status.HTTP_403_FORBIDDEN)
            
            #publish policy
            elif policy_obj.status == 'approved' and document_data['status'] == 'Published':
                policy_obj.status = 'published'
                policies = policy_obj.leave_policies.all()
                block_leave_pto_ruleset = RuleSet.objects.get(name='block_leave_pto')
                block_leave_wfh_ruleset = RuleSet.objects.get(name='block_leave_wfh')
                with transaction.atomic():
                    for policy in policies:
                        if policy.leave_type:
                            if policy.name == 'maternity_leave':
                                max_days = policy.details.get('paid')
                            elif policy.name == 'paternity_leave' or policy.name == 'marriage_leave':
                                max_days = policy.details.get('leaves')
                            elif policy.name == 'block_leave':
                                block_leave_pto_ruleset.max_days_allowed = policy.details.get('leaves')
                                block_leave_pto_ruleset.save()
                                block_leave_wfh_ruleset.max_days_allowed = policy.details.get('work_from_home')
                                block_leave_wfh_ruleset.save()
                                continue
                            elif policy.name == 'wfh' or policy.name == 'pto':
                                max_days = policy.details.get('quarterly')
                            else:
                                max_days = None 
                            policy.leave_type.rule_set.max_days_allowed = max_days
                            policy.leave_type.rule_set.save()
                    policy_obj.save()
                    data = YearPolicySerializer(policy_obj).data
                all_users = User.objects.all()
                notification_data = {
                    'type': 'leave_policy',  
                    'content_object': policy_obj,
                    'receivers': [user.id for user in all_users],  
                    'title': f"New Calendar Published",
                    'subtitle': f"A new holidays calendar has been published for year {policy_obj.year}.",
                    'created_by': user,
                    'target_platforms': ['mobile']
                }
                errors.append(send_notification(notification_data, notification_data['receivers']))
                return JsonResponse(data, status=status.HTTP_200_OK)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)