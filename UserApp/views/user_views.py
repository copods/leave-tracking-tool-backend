from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from rest_framework import status
from django.db.models import Count, Q
from UserApp.models import Department, Role, User
from UserApp.serializers import (
    ApproverListSerializer, 
    DepartmentSerializer, 
    RoleSerializer, 
    UserSerializer,
    UserListSerializer
)
from UserApp.decorators import user_is_authorized

# create user unauthorized
@csrf_exempt
def createUserUnauthorized(request):
    if request.method=='POST':
        user_data = JSONParser().parse(request)
        role = RoleSerializer(Role.objects.get(role_key='admin'))
        department = DepartmentSerializer(Department.objects.get(department_key='developer'))
        user_data['role'] = role.data['id']
        user_data['department'] = department.data['id']
        user_serializer = UserSerializer(data=user_data)
        if user_serializer.is_valid():
            user_serializer.save()
            return JsonResponse("Added Successfully!!", safe=False)
        else:
            errors = user_serializer.errors
            return JsonResponse({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)

# format of query param: filter=role:9f299ed6-caf0-4241-9265-7576af1d6426
@csrf_exempt
@user_is_authorized
def userList(request):
    if request.method=='GET':
        try:
            users = User.objects.all()
            search = request.GET.get('search', None)
            sort = request.GET.get('sort', None)
            page = request.GET.get('page', 1)
            pageSize = request.GET.get('pageSize', 10)
            filter = request.GET.get('filter', None)
            approvers = request.GET.get('approvers', False)  #param for getting approvers list; set it true for getting approvers list
            if approvers:
                users = users.filter(role__role_key='lead')
                users_serializer_class = ApproverListSerializer
            else:
                users_serializer_class = UserListSerializer
            if filter:
                filter = filter.split(':')
                users = users.filter(**{filter[0]: filter[1]})
            if search:
                users = users.filter(first_name__icontains=search) | users.filter(last_name__icontains=search) | users.filter(email__icontains=search)
            if sort:
                users = users.order_by(sort)
            if page and pageSize:
                users = users[(int(page)-1)*int(pageSize):int(page)*int(pageSize)]
            users_serializer = users_serializer_class(users, many=True)
            return JsonResponse(users_serializer.data, safe=False)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@user_is_authorized
def createUser(request):
    if request.method=='POST':
        user_data = JSONParser().parse(request)
        user_serializer = UserSerializer(data=user_data)
        if user_serializer.is_valid():
            user_serializer.save()
            return JsonResponse("Added Successfully!!", safe=False)
        else:
            errors = user_serializer.errors
            return JsonResponse({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)
    
@csrf_exempt
@user_is_authorized
def user(request,id):
    if request.method=='GET':
        user = User.objects.get(id=id)
        user_serializer = UserSerializer(user)
        return JsonResponse(user_serializer.data, safe=False)

    elif request.method=='DELETE':
        user = User.objects.get(id=id)
        user.delete()
        return JsonResponse("Deleted Successfully!!", safe=False)

    elif request.method=='PUT':
        user_data = JSONParser().parse(request)
        user = User.objects.get(id=user_data['id'])
        user_serializer = UserSerializer(user, data=user_data)
        if user_serializer.is_valid():
            user_serializer.save()
            return JsonResponse("Updated Successfully!!", safe=False)
        else:
            errors = user_serializer.errors
            return JsonResponse({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@user_is_authorized
def workTypeCounts(request):
     if request.method == 'GET':
        work_type_counts = User.objects.aggregate(
            in_office=Count('id', filter=Q(work_type="In-Office")),
            work_from_home=Count('id', filter=Q(work_type="Work-From-Home"))
        )
        return JsonResponse({
            "In-Office": work_type_counts['in_office'],
            "Work-From-Home": work_type_counts['work_from_home']
        }, safe=False)
