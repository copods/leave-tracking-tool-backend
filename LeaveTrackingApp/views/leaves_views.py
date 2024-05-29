# create CRUD views for Role model and Department model

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from rest_framework import status

from LeaveTrackingApp.models import Leave, LeaveType
from LeaveTrackingApp.serializers import LeaveSerializer, LeaveTypeSerializer

@csrf_exempt
def getLeaveTypes(request):
    if request.method=='GET':
        leave_types = LeaveType.objects.all()
        leave_types_serializer = LeaveTypeSerializer(leave_types, many=True)
        return JsonResponse(leave_types_serializer.data, safe=False)

@csrf_exempt
def createLeaveRequest(request):
    if request.method=='POST':
        leave_data = JSONParser().parse(request)
        leave_serializer = LeaveSerializer(data=leave_data)
        if leave_serializer.is_valid():
            leave_serializer.save()
            return JsonResponse(leave_serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(leave_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
def getAllLeaves(request):
    if request.method=='GET':
        leaves = Leave.objects.all()
        leaves_serializer = LeaveSerializer(leaves, many=True)
        return JsonResponse(leaves_serializer.data, safe=False)

@csrf_exempt
def getUserLeaves(request):
    if request.method=='GET':
        leaves = Leave.objects.filter(user_id=id)
        leaves_serializer = LeaveSerializer(leaves, many=True)
        return JsonResponse(leaves_serializer.data, safe=False)



# get leaves left
# get leave list for candidate
# get leave list for approver
# get leave details
# change leave status with status message

