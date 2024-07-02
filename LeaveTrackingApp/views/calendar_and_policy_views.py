from django.http.response import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.parsers import JSONParser
from LeaveTrackingApp.models import YearPolicy, yearCalendar
from LeaveTrackingApp.serializers import YearCalendarSerializer, YearCalendarSerializerList, YearPolicySerializer
from UserApp.decorators import user_is_authorized


@csrf_exempt
@user_is_authorized
def getHolidayCalendars(request):
    if request.method=='GET':
        # filter based on status in queryparam with default value Approved
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
# @user_is_authorized
def createYearPolicy(request):
    if request.method=='POST':
        year_policy_data = JSONParser().parse(request)
        year_policy_serializer = YearPolicySerializer(data=year_policy_data)
        if year_policy_serializer.is_valid():
            year_policy_serializer.save()
            return JsonResponse(year_policy_serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(year_policy_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
# @user_is_authorized
def getYearPolicy(request):
    if request.method=='GET':
        try:
            status = request.GET.get('status', 'Published')
            year = request.GET.get('year', None)
            if year:
                year_policy = YearPolicy.objects.filter(status=status, year=year).first()
            else:
                year_policy = YearPolicy.objects.filter(status=status).order_by('-year').first()
            year_policy_serializer = YearPolicySerializer(year_policy)
            return JsonResponse(year_policy_serializer.data, safe=False)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)