# create CRUD views for Role model and Department model

from datetime import date, datetime, timedelta
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from LeaveTrackingApp.utils import get_onleave_wfh_details, getYearLeaveStats
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
    LeaveUtilSerializer,
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
        try:
            leave_data = JSONParser().parse(request)
            user = User.objects.get(id=leave_data['user'])
            try:
                approver = User.objects.get(id=leave_data['approver'])
            except User.DoesNotExist:
                return JsonResponse({'error': 'Approver not found'}, status=status.HTTP_404_NOT_FOUND)
            leave_serializer = LeaveSerializer(data=leave_data)
            if leave_serializer.is_valid():
                leave_serializer.save()
                return JsonResponse(leave_serializer.data, status=status.HTTP_201_CREATED)
            return JsonResponse(leave_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
def getOnLeaveAndWFH(request):
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
            wfh_leaves = leaves.filter(leave_type__name='wfh')
            on_leave = leaves.exclude(leave_type__name='wfh')
            wfh_leaves_data = LeaveUtilSerializer(wfh_leaves, many=True).data
            on_leave_data = LeaveUtilSerializer(on_leave, many=True).data
            
            response_obj = []
            while current_date <= last_date:
                if current_date.weekday()==5 or current_date.weekday()==6:
                    current_date += timedelta(days=1)
                    continue
                response_obj.append(get_onleave_wfh_details(wfh_leaves_data, on_leave_data, current_date))
                current_date += timedelta(days=1)
                
            return JsonResponse(response_obj, safe=False)
        
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