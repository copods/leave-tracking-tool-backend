from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from rest_framework import status

from UserApp.models import Department, Role, User
from UserApp.serializers import DepartmentSerializer, RoleSerializer, UserSerializer

# Create your views here.

@csrf_exempt
def userList(request):
    if request.method=='GET':
        users = User.objects.all()
        search = request.GET.get('search', None)
        sort = request.GET.get('sort', None)
        page = request.GET.get('page', 1)
        pageSize = request.GET.get('pageSize', 10)
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