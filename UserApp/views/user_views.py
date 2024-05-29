from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from rest_framework import status

from UserApp.models import Department, Role, User
from UserApp.serializers import DepartmentSerializer, RoleSerializer, UserSerializer

# format of query param: filter=role:9f299ed6-caf0-4241-9265-7576af1d6426
@csrf_exempt
def userList(request):
    if request.method=='GET':
        users = User.objects.all()
        search = request.GET.get('search', None)
        sort = request.GET.get('sort', None)
        page = request.GET.get('page', 1)
        pageSize = request.GET.get('pageSize', 10)

        filter = request.GET.get('filter', None)
        if filter:
            filter = filter.split(':')
            users = users.filter(**{filter[0]: filter[1]})
        if search:
            users = users.filter(first_name__icontains=search) | users.filter(last_name__icontains=search) | users.filter(email__icontains=search)
        if sort:
            users = users.order_by(sort)
        if page and pageSize:
            users = users[(int(page)-1)*int(pageSize):int(page)*int(pageSize)]
        users_serializer = UserSerializer(users, many=True)
        return JsonResponse(users_serializer.data, safe=False)

@csrf_exempt
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





# from rest_framework.views import APIView
# from apps.department.models import Department
# from apps.role.models import Role
# from apps.user.models import User
# from apps.user.serializers import UserSerializers, ApproverListSerializer
# from rest_framework import generics, status
# from django.http import JsonResponse
# from apps.authorization.decorators import user_has_permission, user_is_authorized
# from django.utils.decorators import method_decorator

# @method_decorator(user_is_authorized, name='dispatch')
# class UserListCreateAPIView(generics.ListCreateAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserSerializers

#     @method_decorator(user_has_permission('getEmployeeList'), name='dispatch')
#     def get(self, request, *args, **kwargs):
#         return self.list(request, *args, **kwargs)

#     @method_decorator(user_has_permission('addEmployee'), name='dispatch')
#     def post(self, request, *args, **kwargs):
#         data = request.data
#         role_name = data.get('role')
#         dept_name = data.get('department')
#         try:
#             role = Role.objects.get(role_name=role_name)
#             department = Department.objects.get(dept_name=dept_name)
#             data['role'] = role.role_id
#             data['department'] = department.dept_id
#             serializer = self.get_serializer(data=data)
#             serializer.is_valid(raise_exception=True)
#             self.perform_create(serializer)
#             return JsonResponse(serializer.data, status=status.HTTP_201_CREATED, safe=False)
#         except Role.DoesNotExist:
#             return JsonResponse({"message": f"Role '{role_name}' does not exist."})
#         except Department.DoesNotExist:
#             return JsonResponse({"message": f"Department '{dept_name}' does not exist."})
        
# @method_decorator(user_is_authorized, name='dispatch')
# class UserRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserSerializers

#     @method_decorator(user_has_permission('getEmployee'), name='dispatch')
#     def get(self, request, *args, **kwargs):
#         user_id = kwargs.get('id')
#         try:
#             user = User.objects.get(user_id=user_id)
#             serializer = self.get_serializer(user)
#             return JsonResponse(serializer.data, safe=False)
#         except User.DoesNotExist:
#             return JsonResponse({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        
#     @method_decorator(user_has_permission('editEmployee'), name='dispatch')
#     def put(self, request, *args, **kwargs):
#         user_id = kwargs.get('id')
#         try:
#             user = User.objects.get(user_id = user_id)
#             serializer = self.get_serializer(user, data=request.data, partial=True)
#             serializer.is_valid(raise_exception=True)
#             self.perform_update(serializer)
#             return JsonResponse(serializer.data, safe=False)
#         except User.DoesNotExist:
#             return JsonResponse({"message": "User does not exists."}, status=status.HTTP_404_NOT_FOUND)

#     @method_decorator(user_has_permission('deleteEmployee'), name='dispatch')
#     def delete(self, request, *args, **kwargs):
#         user_id = kwargs.get('id')
#         try:
#             user = User.objects.get(user_id = user_id)
#             self.perform_destroy(user)
#             return JsonResponse({"message": "User deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
#         except User.DoesNotExist:
#             return JsonResponse({"message": "User does not exists."}, status=status.HTTP_404_NOT_FOUND)
    
# class ApproverListView(APIView):
#     def get(self, request):
#         approvers = User.objects.filter(role__role_name='team lead')
#         serializer = ApproverListSerializer(approvers, many=True)
#         return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)
