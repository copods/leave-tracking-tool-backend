# create CRUD views for Role model and Department model

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from rest_framework import status

from UserApp.models import Department, Role, User
from UserApp.serializers import DepartmentSerializer, RoleSerializer
from UserApp.decorators import user_is_authorized

@csrf_exempt
@user_is_authorized
def role(request):
    if request.method=='GET':
        roles = Role.objects.all()
        roles_serializer = RoleSerializer(roles, many=True)
        return JsonResponse(roles_serializer.data, safe=False)


@csrf_exempt
@user_is_authorized
def department(request):
    if request.method=='GET':
        departments = Department.objects.all()
        departments_serializer = DepartmentSerializer(departments, many=True)
        return JsonResponse(departments_serializer.data, safe=False)