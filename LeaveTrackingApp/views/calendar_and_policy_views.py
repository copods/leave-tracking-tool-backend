from datetime import datetime
from django.http.response import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from rest_framework import status
from rest_framework.parsers import JSONParser
from LeaveTrackingApp.models import LeaveType, YearPolicy, yearCalendar
from LeaveTrackingApp.serializers import YearCalendarSerializer, YearPolicySerializer
from UserApp.decorators import user_is_authorized
from UserApp.models import User

 
@csrf_exempt
@user_is_authorized
def getHolidayCalendars(request):
    if request.method=='GET':
        try:
            year = request.GET.get('year', None)
            if year:
                year_calendar = yearCalendar.objects.filter(status='published', year=year).order_by('-updated_at').first()
            else:
                year_calendar = yearCalendar.objects.filter(status='published').order_by('-updated_at').first()
            if not year_calendar:
                if year:
                    year_calendar = yearCalendar.objects.filter(status__in=['approved', 'draft', 'sent_for_approval'], year=year).order_by('-updated_at').first()
                else:
                    year_calendar = yearCalendar.objects.filter(status__in=['approved', 'draft', 'sent_for_approval']).order_by('-updated_at').first()
                if not year_calendar:
                    return JsonResponse({"error": "No year calendar found for this year"}, status=status.HTTP_404_NOT_FOUND)
            holiday_calendars_serializer = YearCalendarSerializer(year_calendar)
            return JsonResponse(holiday_calendars_serializer.data, safe=False)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@user_is_authorized
def createHolidayCalendar(request):
    if request.method=='POST':
        try:
            year_calendar_data = JSONParser().parse(request)
            if yearCalendar.objects.filter(status__in=['approved', 'draft', 'sent_for_approval']).exists():
                return JsonResponse({"error": "A draft or an approved calendar already exists"}, status=status.HTTP_403_FORBIDDEN)
            
            if not year_calendar_data.get('status') or year_calendar_data['status'] != 'Draft':
                year_calendar_data['status'] = 'Draft'

            year_calendar_serializer = YearCalendarSerializer(data=year_calendar_data)
            if year_calendar_serializer.is_valid():
                year_calendar_serializer.save()
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
            document_data = JSONParser().parse(request)
            calendar_obj = yearCalendar.objects.get(id=id)

            if calendar_obj.status == 'published':
                return JsonResponse({"error": "Can't edit published policy"}, status=status.HTTP_403_FORBIDDEN)
            
            elif calendar_obj.status == 'sent_for_approval':
                if (len(document_data.keys())>=1 and (not document_data.get('status'))) or len(document_data.keys())>1: # do not edit sent for approval document
                    return JsonResponse({"error": "Can't edit calendar sent for approval"}, status=status.HTTP_403_FORBIDDEN)
                
                elif document_data.get('status') == 'Approved': # approve calendar
                    if user.role.role_key == 'admin':
                        calendar_obj.status = 'approved'
                        calendar_obj.save()
                        return JsonResponse({'message': 'calendar approved'}, status=status.HTTP_200_OK)
                    else:
                        return JsonResponse({"error": "Only admin can approve calendar"}, status=status.HTTP_403_FORBIDDEN)
                    
                elif document_data['status'] == 'Rejected': # reject calendar
                    if user.role.role_key == 'admin':
                        calendar_obj.status = 'draft'
                        calendar_obj.save()
                        return JsonResponse({'message': 'calendar rejected'}, status=status.HTTP_200_OK)
                    else:
                        return JsonResponse({"error": "Only admin can reject calendar"}, status=status.HTTP_403_FORBIDDEN)

            #edit calendar
            elif not document_data.get('status') or document_data['status'] == 'Draft':
                year_calendar_serializer = YearCalendarSerializer(calendar_obj, document_data, partial=True)
                if year_calendar_serializer.is_valid():
                    year_calendar_serializer.save()
                    return JsonResponse(year_calendar_serializer.data, status=status.HTTP_200_OK)
                return JsonResponse(year_calendar_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            elif calendar_obj.status == 'approved' and document_data['status'] == 'Approved':
                return JsonResponse({"error": "calendar already approved"}, status=status.HTTP_409_CONFLICT)
            
            elif calendar_obj.status in ['draft', 'sent_for_approval'] and document_data['status'] == 'Published':
                return JsonResponse({"error": "calendar is not approved yet"}, status=status.HTTP_403_FORBIDDEN)
            
            elif calendar_obj.status == 'draft' and document_data['status'] == 'Approved':
                return JsonResponse({"error": "calendar is not sent for approval yet"}, status=status.HTTP_403_FORBIDDEN)
            
            elif calendar_obj.status == 'draft' and document_data['status'] == 'Sent For Approval':
                calendar_obj.status = 'sent_for_approval'
                calendar_obj.save()
                return JsonResponse({'message': 'calendar sent for approval'}, status=status.HTTP_200_OK)
            
            #publish calendar
            elif calendar_obj.status == 'approved' and document_data['status'] == 'Published':
                calendar_obj.status = 'published'
                calendar_obj.save()
                return JsonResponse({'message': 'calendar published'}, status=status.HTTP_200_OK)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@csrf_exempt
@user_is_authorized
def createYearPolicy(request):
    if request.method=='POST':
        try:
            year_policy_data = JSONParser().parse(request)
            if YearPolicy.objects.filter(status__in=['approved', 'draft', 'sent_for_approval']).exists():
                return JsonResponse({"error": "A draft or an approved policy already exists"}, status=status.HTTP_403_FORBIDDEN)
            
            if not year_policy_data.get('status') or year_policy_data['status'] != 'Draft':
                year_policy_data['status'] = 'Draft'

            year_policy_serializer = YearPolicySerializer(data=year_policy_data)
            if year_policy_serializer.is_valid():
                year_policy_serializer.save()
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
                    return JsonResponse({"error": "No year policy found for this year"}, status=status.HTTP_404_NOT_FOUND)
                    
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
            document_data = JSONParser().parse(request)
            policy_obj = YearPolicy.objects.get(id=id)

            if policy_obj.status == 'published':
                return JsonResponse({"error": "Can't edit published policy"}, status=status.HTTP_403_FORBIDDEN)
            
            elif policy_obj.status == 'sent_for_approval':
                if (len(document_data.keys())>=1 and (not document_data.get('status'))) or len(document_data.keys())>1: # do not edit sent for approval document
                    return JsonResponse({"error": "Can't edit policy sent for approval"}, status=status.HTTP_403_FORBIDDEN)
                
                elif document_data.get('status') == 'Approved': # approve policy
                    if user.role.role_key == 'admin':
                        policy_obj.status = 'approved'
                        policy_obj.save()
                        return JsonResponse({'message': 'Policy approved'}, status=status.HTTP_200_OK)
                    else:
                        return JsonResponse({"error": "Only admin can approve policy"}, status=status.HTTP_403_FORBIDDEN)
                    
                elif document_data['status'] == 'Rejected': # reject policy
                    if user.role.role_key == 'admin':
                        policy_obj.status = 'draft'
                        policy_obj.save()
                        return JsonResponse({'message': 'Policy rejected'}, status=status.HTTP_200_OK)
                    else:
                        return JsonResponse({"error": "Only admin can reject policy"}, status=status.HTTP_403_FORBIDDEN)

            #edit policy
            elif not document_data.get('status') or document_data['status'] == 'Draft':
                year_policy_serializer = YearPolicySerializer(policy_obj, document_data, partial=True)
                if year_policy_serializer.is_valid():
                    year_policy_serializer.save()
                    return JsonResponse(year_policy_serializer.data, status=status.HTTP_200_OK)
                return JsonResponse(year_policy_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            elif policy_obj.status == 'approved' and document_data['status'] == 'Approved':
                return JsonResponse({"error": "Policy already approved"}, status=status.HTTP_409_CONFLICT)
            
            elif policy_obj.status in ['draft', 'sent_for_approval'] and document_data['status'] == 'Published':
                return JsonResponse({"error": "Policy is not approved yet"}, status=status.HTTP_403_FORBIDDEN)
            
            elif policy_obj.status == 'draft' and document_data['status'] == 'Approved':
                return JsonResponse({"error": "Policy is not sent for approval yet"}, status=status.HTTP_403_FORBIDDEN)
            
            elif policy_obj.status == 'draft' and document_data['status'] == 'Sent For Approval':
                policy_obj.status = 'sent_for_approval'
                policy_obj.save()
                return JsonResponse({'message': 'Policy sent for approval'}, status=status.HTTP_200_OK)
            
            #publish policy
            elif policy_obj.status == 'approved' and document_data['status'] == 'Published':
                policy_obj.status = 'published'
                policies = policy_obj.leave_policies.all()
                with transaction.atomic():
                    for policy in policies:
                        if policy.leave_type:
                            if policy.name == 'maternity_leave':
                                max_days = policy.details.get('paid')
                            elif policy.name == 'paternity_leave' or policy.name == 'marriage_leave':
                                max_days = policy.details.get('leaves')
                            elif policy.name == 'wfh' or policy.name == 'pto':
                                max_days = policy.details.get('quarterly')
                            else:
                                max_days = None 
                            policy.leave_type.rule_set.max_days_allowed = max_days
                            policy.leave_type.rule_set.save()
                    policy_obj.save()
                return JsonResponse({'message': 'Policy published'}, status=status.HTTP_200_OK)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)