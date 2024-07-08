from datetime import datetime
from django.http.response import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from rest_framework import status
from rest_framework.parsers import JSONParser
from LeaveTrackingApp.models import LeaveType, YearPolicy, yearCalendar
from LeaveTrackingApp.serializers import YearCalendarSerializer, YearCalendarSerializerList, YearPolicySerializer
from UserApp.decorators import user_is_authorized
from UserApp.models import User

 
@csrf_exempt
@user_is_authorized
def getHolidayCalendars(request):
    if request.method=='GET':
        # filter based on status in queryparam with default value approved
        status = request.GET.get('status', 'Published')
        year = request.GET.get('year', None)
        if year:
            holiday_calendars = yearCalendar.objects.filter(status=status, year=year)
        else:
            holiday_calendars = yearCalendar.objects.filter(status=status)
        holiday_calendars_serializer = YearCalendarSerializerList(holiday_calendars, many=True)
        return JsonResponse(holiday_calendars_serializer.data, safe=False)

@csrf_exempt
@user_is_authorized
def createHolidayCalendar(request):
    if request.method=='POST':
        holiday_calendar_data = JSONParser().parse(request)
        holiday_calendar_serializer = YearCalendarSerializer(data=holiday_calendar_data)
        if holiday_calendar_serializer.is_valid():
            holiday_calendar_serializer.save()
            return JsonResponse(holiday_calendar_serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(holiday_calendar_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
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
            year = request.GET.get('year', datetime.now().year)
            year_policy = YearPolicy.objects.filter(status='published', year=year).order_by('-updated_at').first()
            if not year_policy:
                year_policy = YearPolicy.objects.filter(status__in=['approved', 'draft'], year=year).order_by('-created_at').first()
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
                            policy.leave_type.rule_set.max_days_allowed = policy.max_days_allowed
                            policy.leave_type.rule_set.save()
                    policy_obj.save()
                return JsonResponse({'message': 'Policy published'}, status=status.HTTP_200_OK)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)