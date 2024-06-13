# create CRUD views for Role model and Department model

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from rest_framework import status

from LeaveTrackingApp.models import yearCalendar
from LeaveTrackingApp.serializers import YearCalendarSerializerList, YearCalendarSerializer
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