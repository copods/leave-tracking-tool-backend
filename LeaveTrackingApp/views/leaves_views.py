# create CRUD views for Role model and Department model

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from UserApp.models import User
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from rest_framework import status
from django.db.models import Q
from LeaveTrackingApp.models import Leave, LeaveType
from LeaveTrackingApp.serializers import LeaveSerializer, LeaveTypeSerializer
from UserApp.decorators import user_is_authorized

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
    if request.method=='POST':
        leave_data = JSONParser().parse(request)
        leave_serializer = LeaveSerializer(data=leave_data)
        if leave_serializer.is_valid():
            leave_serializer.save()
            return JsonResponse(leave_serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(leave_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# filter query param format=> filter=role:9f299ed6-caf0-4241-9265-7576af1d6426,status:P
@csrf_exempt
@user_is_authorized
def getAllLeaves(request):
    if request.method=='GET':
        try:
            user_email = getattr(request, 'user_email', None)
            filters = request.GET.get('filter', None)
            search = request.GET.get('search', None)
            sort = request.GET.get('sort', None)
            user = User.objects.get(email=user_email)
            leaves = Leave.objects.filter(approver=user)
            if filters:
                leaves = leaves.filter(Q(**{f.split(':')[0]: f.split(':')[1] for f in filters.split(',')}))
            if search:
                leaves = leaves.filter(Q(user__first_name__icontains=search) | Q(user__last_name__icontains=search))
            if sort:
                leaves = leaves.order_by(sort)
            leaves_serializer = LeaveSerializer(leaves, many=True)
            return JsonResponse(leaves_serializer.data, safe=False)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(e)
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@user_is_authorized
def getUserLeaves(request, id):
    if request.method=='GET':
        try:
            user = User.objects.get(id=id)
            leaves = Leave.objects.filter(user_id=user.id)
            leaves_serializer = LeaveSerializer(leaves, many=True)
            return JsonResponse(leaves_serializer.data, safe=False)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# get leaves left
# get leave list for candidate
# get leave list for approver
# get leave details
# change leave status with status message
# unpaid leave count list etc
# enable editing of leave request
