# create CRUD views for Role model and Department model

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from LeaveTrackingApp.utils import getYearLeaveStats
from UserApp.models import User
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from rest_framework import status
from django.db.models import Q
from LeaveTrackingApp.models import Leave, LeaveType, StatusReason
from LeaveTrackingApp.serializers import (
    LeaveSerializer,
    LeaveListSerializer,
    LeaveTypeSerializer,
    StatusReasonSerializer,
    UserLeaveListSerializer
)
from UserApp.decorators import user_is_authorized

@csrf_exempt
@user_is_authorized
def getLeaveTypes(request):
    if request.method=='GET':
        leave_types = LeaveType.objects.all()
        leave_types_serializer = LeaveTypeSerializer(leave_types, many=True)
        return JsonResponse(leave_types_serializer.data, safe=False)

@csrf_exempt
@user_is_authorized
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
def leavesForApprover(request):
    if request.method=='GET':
        try:
            user_email = getattr(request, 'user_email', None) #user_email is fetched from token while authorizing, then added to request object
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
            user_email = getattr(request, 'user_email', None) #user_email is fetched from token while authorizing, then added to request object
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
            leave_serializer = LeaveSerializer(leave)
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
            leave_stats = getYearLeaveStats(user.id, year)
            return JsonResponse(leave_stats, safe=False)
        except ValueError as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# change leave status with status message
@csrf_exempt
@user_is_authorized
def updateLeaveStatus(request):
    if request.method == 'POST':
        try:
            status_data = JSONParser().parse(request)
            # user_email = getattr(request, 'user_email', None)
            user_email = "sonali2.sharan@copods.co"
            
            status_id = status_data.get('id')
            status = status_data.get('status')
            reason_value = status_data.get('reason')
            leave_id = status_data.get('leave_id')

            if not all([status, reason_value, user_email, leave_id]):
                return JsonResponse({'error': 'Missing required fields'}, status=400)

            user = User.objects.get(email=user_email)
            leave = Leave.objects.get(id=leave_id)
            
            if status_id:
                status_reason = StatusReason.objects.get(id=status_id)
                status_reason.status = status
                status_reason.reason = reason_value
                status_reason.user = user
                status_reason.save()
                created = False
                
            else:
                status_reason = StatusReason.objects.create(
                    status=status,
                    reason=reason_value,
                    user=user
                )
                created = True
                leave.status_reasons.add(status_reason)

            leave.status = status
            leave.save()
            status_reason_serializer = StatusReasonSerializer(status_reason)
            return JsonResponse(status_reason_serializer.data, status=201 if created else 200)
        
        except Leave.DoesNotExist:
            return JsonResponse({'error': 'Leave not found'}, status=404)
        except StatusReason.DoesNotExist:
            return JsonResponse({'error': 'StatusReason not found'}, status=404)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


# enable editing of leave request
