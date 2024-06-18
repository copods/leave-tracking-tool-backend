import math
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from rest_framework import status
from django.db.models import Count, Q
from UserApp.models import Department, Role, User
from UserApp.serializers import (
    ShortUserListSerializer, 
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

@csrf_exempt
@user_is_authorized
def userList(request):
    if request.method=='GET':
        try:
            users = User.objects.all()  # OR User.objects.all_with_deleted() based on whether to show deleted users too
            query_params = {key: request.GET.getlist(key) for key in request.GET.keys()}
            search = query_params.get('search', [None])[0] 
            sort = query_params.get('sort', [None])[0]
            page = query_params.get('page', [1])[0]
            pageSize = query_params.get('pageSize', [10])[0]
            serializer_class = ShortUserListSerializer if query_params.get('getShortList', [None])[0] else UserListSerializer
            
            filters = {}
            for key, value in query_params.items():
                if not key in ['search', 'sort', 'page', 'pageSize', 'getShortList']:
                    if key == 'department':
                        filters['department__department_key__in'] = value
                    elif key == 'role':
                        filters['role__role_key__in'] = value
                    else:
                        filters[f'{key}__in'] = value
            
            users = users.filter(**filters) 

            if search:
                users = users.filter(
                    Q(first_name__icontains=search) | 
                    Q(last_name__icontains=search) |
                    Q(role__role_name__icontains=search) |
                    Q(department__department_name__icontains=search)
                )
            
            users = users.order_by(sort) if sort else users.order_by('-updated_at')
            total_users = users.count()

            if page or pageSize:
                users = users[(int(page)-1)*int(pageSize):int(page)*int(pageSize)]

            users_serializer = serializer_class(users, many=True)
            return JsonResponse({
                'total_results': total_users, 
                'total_pages': math.ceil(total_users/int(pageSize)),
                'current_page': int(page),
                'page_size': int(pageSize),
                'data': users_serializer.data,

            }, safe=False)
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
        try:
            user = User.objects.get(id=id)
            user_serializer = UserSerializer(user)
            return JsonResponse(user_serializer.data, safe=False)
        except User.DoesNotExist as e:
            return JsonResponse({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    elif request.method=='DELETE':
        try:
            user = User.objects.get(id=id)
            user.delete()
            return JsonResponse({"id": id, "message": "Deleted Successfully!!"}, safe=False)
        except ValueError as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist as e:
            return JsonResponse({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    elif request.method=='PUT':
        try:
            user_data = JSONParser().parse(request)
            user = User.objects.get(id=user_data['id'])
            user_serializer = UserSerializer(user, data=user_data)
            if user_serializer.is_valid():
                user_serializer.save()
                return JsonResponse("Updated Successfully!!", safe=False)
            else:
                errors = user_serializer.errors
                return JsonResponse({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

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
            "Work-From-Home": work_type_counts['work_from_home'],
            "Total": work_type_counts['in_office'] + work_type_counts['work_from_home']
        }, safe=False)


@csrf_exempt
@user_is_authorized
def bulkUserAdd(request):
    if request.method == 'POST':
        users_data = JSONParser().parse(request)

        for user in users_data:
            role = Role.objects.get(role_key=user['role'])
            department = Department.objects.get(department_key=user['department'])

            role_serializer = RoleSerializer(role)
            user['role'] = role_serializer.data['id']

            department_serializer = DepartmentSerializer(department)
            user['department'] = department_serializer.data['id']


        users_serializer = UserSerializer(data=users_data, many=True)
        if users_serializer.is_valid():
            users_serializer.save()
            return JsonResponse("Added Successfully!!", safe=False)
        else:
            errors = users_serializer.errors
            return JsonResponse({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)
        

@csrf_exempt
@user_is_authorized
def addInitialUserPoints(request):
    if request.method == 'POST':
        try:
            points_data = JSONParser().parse(request)
            user_email = getattr(request, 'user_email', None)
            user = User.objects.get(email=user_email)
            user.points += points_data['correct_questions']
            user.save()
            return JsonResponse(f"The user has been awarded with {points_data['correct_questions']} points", safe=False)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        