import math
from django.db.models import Count, Q
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from rest_framework import status
from rest_framework.parsers import JSONParser
from UserApp.decorators import user_is_authorized
from UserApp.models import Department, Role, User
from UserApp.serializers import (
    ApproverListSerializer,
    DepartmentSerializer,
    RoleSerializer,
    UserListSerializer,
    UserSerializer,
    UserAppProfileSerializer
)
from common.utils import send_email


# create user unauthorized
@csrf_exempt
def createUserUnauthorized(request):
    if request.method=='POST':
        user_data = JSONParser().parse(request)
        role = RoleSerializer(Role.objects.get(role_key='admin'))
        department = DepartmentSerializer(Department.objects.get(department_key='development'))
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
            pageSize = query_params.get('pageSize', [6])[0]
            serializer_class = UserListSerializer if query_params.get('admin', [False])[0] else ApproverListSerializer
            
            filters = {}
            for key, value in query_params.items():
                if not key in ['search', 'sort', 'page', 'pageSize', 'admin']:
                    if key == 'department':
                        filters['department__department_key__in'] = value
                    elif key == 'role':
                        filters['role__role_key__in'] = value
                    elif key == 'work_type':
                        value = [('in_office' if v == 'In-Office' else ('work_from_home' if v == 'Work-From-Home' else v)) for v in value]
                        filters[f'{key}__in'] = value
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
            
            users = users.order_by(sort) if sort else users.order_by('-created_at')
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
        try:
            user_data = JSONParser().parse(request)
            user_readded = False
            user_serializer = None
            user = User.objects.all_with_deleted().filter(email=user_data['email'], is_deleted=True).first()
            if user:
                user.is_deleted = False
                user.save()
                user_serializer = UserSerializer(user, data=user_data)
                if user_serializer.is_valid():
                    user_serializer.save()
                    user_readded = True
                else:
                    errors = user_serializer.errors
                    return JsonResponse({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)
            else:
                user_serializer = UserSerializer(data=user_data)
                if user_serializer.is_valid():
                    user_serializer.save()
                else:
                    errors = user_serializer.errors
                    return JsonResponse({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)

            errors = []

            #send email to user
            try:
                data = user_serializer.data
                if not isinstance(data, list):
                    data = [data]
                send_email(
                    recipients=data,
                    subject='Your Leave Management Platform Awaits!',
                    template_name='onboarding_template.html',
                    context={},
                    app_name='UserApp'
                )
            except Exception as e:
                errors.append(str(e))
            
            response = {"message": "Added Successfully!!" if not user_readded else "User readded successfully!!"}
            if errors:
                response["errors"] = errors
            return JsonResponse(response, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@csrf_exempt
@user_is_authorized
def user(request,id):
    if request.method=='GET':
        try:
            user = User.objects.get(id=id)
            app_profile = request.GET.get('app_profile', False)
            serializer_class = UserAppProfileSerializer if app_profile else UserSerializer
            user_serializer = serializer_class(user)
            return JsonResponse(user_serializer.data, safe=False)
        except User.DoesNotExist as e:
            return JsonResponse({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
            user = User.objects.get(id=id)
            user_serializer = UserSerializer(user, data=user_data, partial=True)
            if user_serializer.is_valid():
                user_serializer.save()
                return JsonResponse("Updated Successfully!!", safe=False)
            else:
                errors = user_serializer.errors
                return JsonResponse({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@user_is_authorized
def workTypeCounts(request):
    if request.method == 'GET':
        work_type_counts = User.objects.aggregate(
            in_office=Count('id', filter=Q(work_type="in_office")),
            work_from_home=Count('id', filter=Q(work_type="work_from_home")),
            total=Count('id')
        )
        return JsonResponse({
            "In-Office": work_type_counts['in_office'],
            "Work-From-Home": work_type_counts['work_from_home'],
            "Total": work_type_counts['total']
        }, safe=False)


@csrf_exempt
@user_is_authorized
@transaction.atomic
def bulkUserAdd(request):
    if request.method == 'POST':
        try:
            users_data = JSONParser().parse(request)                         
            deleted_users = User.objects.all_with_deleted().filter(is_deleted=True)
            deleted_users_emails = deleted_users.values_list('email', flat=True)
            readded_users = []

            roles = Role.objects.all()
            departments = Department.objects.all()

            idxs_to_remove = []
            for idx, user in enumerate(users_data):
                role = roles.get(role_key=user['role'])
                department = departments.get(department_key=user['department'])
                user['role'] = str(role.id)
                user['department'] = str(department.id)
                if user['email'] in deleted_users_emails:
                    readded_users.append(user)
                    idxs_to_remove.append(idx)
            users_data = [user for i, user in enumerate(users_data) if i not in idxs_to_remove]

            for user in readded_users:
                instance = deleted_users.get(email=user['email'])
                instance.is_deleted = False
                instance.save()
                user_serializer = UserSerializer(instance, data=user)
                if user_serializer.is_valid():
                    user_serializer.save()
                else:
                    return JsonResponse(user_serializer.errors, safe=False, status=status.HTTP_400_BAD_REQUEST)
         
            users_serializer = UserSerializer(data=users_data, many=True)
            if users_serializer.is_valid():
                users_serializer.save()
            else:
                return JsonResponse(users_serializer.errors, safe=False, status=status.HTTP_400_BAD_REQUEST)
            
            errors = []
            #send email to users
            try:
                data = users_serializer.data
                data = [data] if not isinstance(data, list) else data
                send_email(
                    recipients=data,
                    subject='Your Leave Management Platform Awaits!',
                    template_name='onboarding_template.html',
                    context={},
                    app_name='UserApp'
                )
            except Exception as e:
                errors.append(str(e))
            
            response = f"{len(users_data)} Added Successfully!!" if not readded_users else f"{len(users_data)} Added Successfully and {len(readded_users)} Re-Added Successfully!!"
            if errors:
                response['errors'] = errors
            return JsonResponse(response, safe=False)
        
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@user_is_authorized
def addInitialUserPoints(request):
    if request.method == 'POST':
        try:
            points_data = JSONParser().parse(request)
            user_email = getattr(request, 'user_email', None)
            user = User.objects.get(email=user_email)
            user.points += points_data['points']
            if points_data['user_onboarded']:
                if not user.onboarding_status:
                    user.onboarding_status = {}
                user.onboarding_status['LeaveTrackingApp'] = True
            user.save()
            return JsonResponse(f"Successfully onboarded", safe=False)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        